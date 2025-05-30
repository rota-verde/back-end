import pytest
from http import HTTPStatus
from unittest.mock import MagicMock

from firebase_admin.exceptions import FirebaseError

# Importa as constantes para serem usadas no decorador 'parametrize'
from tests.routes.conftest import (
    PAYLOAD_CIDADAO,
    PAYLOAD_MOTORISTA,
    PAYLOAD_COOPERATIVA,
)


# --- Testes de Registro Parametrizados ---


@pytest.mark.parametrize(
    "payload, expected_uid, specific_db_check",
    [
        (PAYLOAD_CIDADAO, "uid-cidadao-123", "check_residencia"),
        (PAYLOAD_MOTORISTA, "uid-motorista-456", "no_residencia"),
        (PAYLOAD_COOPERATIVA, "uid-cooperativa-789", "no_residencia"),
    ],
)
def test_register_user_success_parametrized(
    client, mock_firebase, payload, expected_uid, specific_db_check
):
    """Testa o registro bem-sucedido para todas as roles."""
    mock_firebase_instance, mock_db, _ = mock_firebase
    mock_firebase_instance.auth().create_user_with_email_and_password.return_value = {
        "localId": expected_uid
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == HTTPStatus.CREATED
    response_data = response.json()
    assert response_data["uid"] == expected_uid
    assert response_data["role"] == payload["role"]

    mock_db.collection("usuarios").document(expected_uid).set.assert_called_once()
    if specific_db_check == "check_residencia":
        mock_db.collection("usuarios").document(expected_uid).collection(
            "residencias"
        ).document(expected_uid).set.assert_called_once()
    else:
        mock_db.collection("usuarios").document(expected_uid).collection(
            "residencias"
        ).document(expected_uid).set.assert_not_called()


def test_register_user_email_already_exists(client, mock_firebase, cidadao_payload):
    """Testa a falha de registro quando o e-mail já existe."""
    mock_firebase_instance, _, _ = mock_firebase
    mock_firebase_instance.auth().create_user_with_email_and_password.side_effect = (
        Exception("FirebaseError: EMAIL_EXISTS")
    )

    response = client.post("/auth/register", json=cidadao_payload)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "já existe" in response.json()["detail"]


# --- Testes de Login ---


def test_login_user_success(client, mock_firebase):
    """Testa o login bem-sucedido de um usuário."""
    mock_firebase_instance, mock_db, mock_auth_admin = mock_firebase
    mock_firebase_instance.auth().sign_in_with_email_and_password.return_value = {
        "idToken": "um-token-jwt-falso"
    }
    mock_auth_admin.verify_id_token.return_value = {"uid": "uid-do-usuario-logado"}
    mock_user_doc = MagicMock()
    mock_user_doc.to_dict.return_value = {"role": "motorista"}
    mock_db.collection("usuarios").document(
        "uid-do-usuario-logado"
    ).get.return_value = mock_user_doc

    credentials = {"email": "usuario@teste.com", "senha": "senha123"}
    response = client.post("/auth/login", json=credentials)

    assert response.status_code == HTTPStatus.OK
    assert response.json()["token"] == "um-token-jwt-falso"


def test_login_user_invalid_credentials(client, mock_firebase):
    """Testa o login com credenciais inválidas."""
    mock_firebase_instance, _, _ = mock_firebase
    mock_firebase_instance.auth().sign_in_with_email_and_password.side_effect = (
        FirebaseError(code=400, message="INVALID_PASSWORD")
    )
    credentials = {"email": "usuario@teste.com", "senha": "senha-errada"}

    response = client.post("/auth/login", json=credentials)

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "Email ou senha inválidos."


# --- Testes de Exclusão de Conta ---


def test_delete_account_success(client, mock_firebase):
    """Testa a exclusão de conta bem-sucedida."""
    _, mock_db, mock_auth_admin = mock_firebase
    user_id = "uid-para-deletar"

    response = client.delete(f"/auth/delete-account/{user_id}")

    assert response.status_code == HTTPStatus.OK
    mock_auth_admin.delete_user.assert_called_once_with(user_id)
    mock_db.collection("usuarios").document(user_id).delete.assert_called_once()


@pytest.mark.parametrize(
    "raised_exception, expected_status, expected_detail_text",
    [
        # Caso de teste para usuário não encontrado
        (
            FirebaseError("auth/user-not-found", "User not found"),
            HTTPStatus.NOT_FOUND,
            "Usuário não encontrado.",
        ),
        # Caso de teste para cobrir a exceção genérica do Firebase
        (
            FirebaseError("auth/internal-error", "Internal error"),
            HTTPStatus.INTERNAL_SERVER_ERROR,
            "Erro ao deletar usuário",
        ),
    ],
)
def test_delete_account_failures(
    client, mock_firebase, raised_exception, expected_status, expected_detail_text
):
    """Testa falhas na exclusão de conta (não encontrado, erro genérico) de forma parametrizada."""
    _, _, mock_auth_admin = mock_firebase
    mock_auth_admin.delete_user.side_effect = raised_exception

    response = client.delete("/auth/delete-account/some-uid")

    assert response.status_code == expected_status
    assert expected_detail_text in response.json()["detail"]


# --- Testes de Atualização de Usuário ---


def test_update_user_success(client, mock_firebase, cidadao_payload):
    """Testa a atualização bem-sucedida de um usuário (auth e firestore)."""
    _, mock_db, mock_auth_admin = mock_firebase
    user_id = "user-to-be-updated"

    # Usa a fixture como base para o payload
    update_payload = cidadao_payload
    update_payload["nome_usuario"] = "José Cidadão Super Atualizado"

    # Mock para a chamada get() que busca os dados atualizados no final
    final_user_data = update_payload.copy()
    del final_user_data["senha"]
    mock_db.collection("usuarios").document(
        user_id
    ).get().to_dict.return_value = final_user_data

    response = client.put(f"/auth/user/update/{user_id}", json=update_payload)

    assert response.status_code == HTTPStatus.OK
    mock_auth_admin.update_user.assert_called_once()
    mock_db.collection("usuarios").document(user_id).update.assert_called_once()
    mock_db.collection("usuarios").document(user_id).collection("residencias").document(
        user_id
    ).set.assert_called_once()


def test_update_user_not_found(client, mock_firebase):
    """Testa a falha de atualização quando o usuário não é encontrado no Firebase Auth."""
    _, _, mock_auth_admin = mock_firebase
    user_id = "non-existent-user"
    valid_payload = {
        "nome_usuario": "Fantasma",
        "email": "fantasma@email.com",
        "telefone": "000",
        "senha": "123",
        "role": "motorista",
        "cnh": "123",
    }
    mock_auth_admin.update_user.side_effect = FirebaseError(
        code="auth/user-not-found", message="User not found"
    )

    response = client.put(f"/auth/user/update/{user_id}", json=valid_payload)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Usuário não encontrado."


def test_update_user_firestore_error(client, mock_firebase):
    """Testa a falha de atualização quando ocorre um erro no Firestore."""
    _, mock_db, _ = mock_firebase
    user_id = "user-with-db-problem"
    valid_payload = {
        "nome_usuario": "DB Error User",
        "email": "db@error.com",
        "telefone": "111",
        "senha": "123",
        "role": "cooperativa",
        "cnpj": "123",
    }
    mock_db.collection("usuarios").document(user_id).update.side_effect = FirebaseError(
        code=500, message="Database permission denied"
    )

    response = client.put(f"/auth/user/update/{user_id}", json=valid_payload)

    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert "Erro ao atualizar usuário" in response.json()["detail"]


# --- Testes para GET /user/{user_id} ---


def test_get_user_success(client, mock_firebase):
    """Testa a busca bem-sucedida de um usuário pelo ID."""
    # Arrange
    _, mock_db, _ = mock_firebase
    user_id = "user-existente-123"

    # Prepara o dado que o Firestore retornaria
    expected_user_data = {
        "nome_usuario": "Usuário Teste",
        "email": "teste@email.com",
        "telefone": "82999998888",
        "role": "cidadao",
    }

    # Configura o mock do documento
    mock_user_doc = MagicMock()
    mock_user_doc.exists = True
    mock_user_doc.to_dict.return_value = expected_user_data
    mock_db.collection("usuarios").document(user_id).get.return_value = mock_user_doc

    # Act
    response = client.get(f"/auth/user/{user_id}")

    # Assert
    assert response.status_code == HTTPStatus.OK
    # Como o response_model é UserBase, ele deve corresponder ao que foi mockado
    assert response.json()["nome_usuario"] == expected_user_data["nome_usuario"]
    assert response.json()["email"] == expected_user_data["email"]


def test_get_user_not_found(client, mock_firebase):
    """Testa a busca por um usuário que não existe no Firestore."""
    # Arrange
    _, mock_db, _ = mock_firebase
    user_id = "user-inexistente-404"

    # Configura o mock para simular que o documento não existe
    mock_user_doc = MagicMock()
    mock_user_doc.exists = False
    mock_db.collection("usuarios").document(user_id).get.return_value = mock_user_doc

    # Act
    response = client.get(f"/auth/user/{user_id}")

    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert "Usuário não encontrado" in response.json()["detail"]


def test_get_user_firebase_error(client, mock_firebase):
    """Testa a falha na busca de usuário devido a um erro genérico do Firebase."""
    # Arrange
    _, mock_db, _ = mock_firebase
    user_id = "user-com-erro-500"

    # Configura o mock para levantar uma exceção ao tentar buscar o documento
    mock_db.collection("usuarios").document(user_id).get.side_effect = FirebaseError(
        code=500, message="Erro interno do Firestore"
    )

    # Act
    response = client.get(f"/auth/user/{user_id}")

    # Assert
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert "Erro ao buscar usuário" in response.json()["detail"]
