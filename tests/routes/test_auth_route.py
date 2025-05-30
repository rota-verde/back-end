import pytest
from fastapi.testclient import TestClient
from firebase_admin import auth
from http import HTTPStatus
from unittest.mock import MagicMock

# Importações do projeto
from main import app
from firebase_admin.exceptions import FirebaseError

# Cliente de teste para a aplicação
client = TestClient(app)


# --- Fixture de Mocks ---


@pytest.fixture
def mock_firebase(mocker):
    """Cria e retorna mocks para as dependências do Firebase."""
    mock_firebase_instance = MagicMock()
    mocker.patch("routes.auth.firebase_instance", mock_firebase_instance)

    mock_db = MagicMock()
    mocker.patch("routes.auth.db", mock_db)

    mock_auth_admin = MagicMock()
    mocker.patch("routes.auth.auth", mock_auth_admin)

    return mock_firebase_instance, mock_db, mock_auth_admin


# --- Testes de Registro Parametrizados ---

payload_cidadao = {
    "nome_usuario": "José Cidadão",
    "telefone": "82911112222",
    "email": "cidadao.teste@email.com",
    "senha": "senha_cidadao_123",
    "role": "cidadao",
    "cpf": "111.222.333-44",
    "endereco": {
        "logradouro": "Rua da Cidadania",
        "numero": "10",
        "bairro": "Centro",
        "cidade": "Maceió",
    },
}
payload_motorista = {
    "nome_usuario": "Carlos Motorista",
    "telefone": "82933334444",
    "email": "motorista.teste@email.com",
    "senha": "senha_motorista_123",
    "role": "motorista",
    "cnh": "12345678901",
    "nome_cooperativa": "Recicla-AL",
}
payload_cooperativa = {
    "nome_usuario": "Coop Recicla Bem",
    "telefone": "8233334444",
    "email": "coop.teste@email.com",
    "senha": "senha_coop_123",
    "role": "cooperativa",
    "cnpj": "12.345.678/0001-99",
    "nome_cooperativa": "Coop Recicla Bem",
    "area_atuacao": ["Ponta Verde", "Jatiúca"],
    "materiais_reciclaveis": ["Plástico", "Papelão", "Metal"],
    "endereco": {
        "logradouro": "Avenida da Reciclagem",
        "numero": "1000",
        "bairro": "Jatiúca",
        "cidade": "Maceió",
    },
}


@pytest.mark.parametrize(
    "payload, expected_uid, specific_db_check",
    [
        (payload_cidadao, "uid-cidadao-123", "check_residencia"),
        (payload_motorista, "uid-motorista-456", "no_residencia"),
        (payload_cooperativa, "uid-cooperativa-789", "no_residencia"),
    ],
)
def test_register_user_success_parametrized(
    mock_firebase, payload, expected_uid, specific_db_check
):
    """Testa o registro bem-sucedido para todas as roles."""
    # Arrange
    mock_firebase_instance, mock_db, _ = mock_firebase
    mock_firebase_instance.auth().create_user_with_email_and_password.return_value = {
        "localId": expected_uid
    }

    # Act
    response = client.post("/auth/register", json=payload)

    # Assert
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


def test_register_user_email_already_exists(mock_firebase):
    """Testa a falha de registro quando o e-mail já existe."""
    # Arrange
    mock_firebase_instance, _, _ = mock_firebase
    mock_firebase_instance.auth().create_user_with_email_and_password.side_effect = (
        Exception("FirebaseError: EMAIL_EXISTS")
    )
    user_data = {
        "email": "existente@teste.com",
        "senha": "s1",
        "nome_usuario": "u1",
        "telefone": "t1",
        "role": "cidadao",
        "cpf": "c1",
    }

    # Act
    response = client.post("/auth/register", json=user_data)

    # Assert
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert "já existe" in response.json()["detail"]


# --- Testes de Login ---


def test_login_user_success(mock_firebase):
    """Testa o login bem-sucedido de um usuário."""
    # Arrange
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

    # Act
    response = client.post("/auth/login", json=credentials)

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert response.json()["token"] == "um-token-jwt-falso"


def test_login_user_invalid_credentials(mock_firebase):
    """Testa o login com credenciais inválidas."""
    # Arrange
    mock_firebase_instance, _, _ = mock_firebase
    mock_firebase_instance.auth().sign_in_with_email_and_password.side_effect = (
        FirebaseError(code=400, message="INVALID_PASSWORD")
    )
    credentials = {"email": "usuario@teste.com", "senha": "senha-errada"}

    # Act
    response = client.post("/auth/login", json=credentials)

    # Assert
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "Email ou senha inválidos."


# --- Testes de Exclusão de Conta ---


def test_delete_account_success(mock_firebase):
    """Testa a exclusão de conta bem-sucedida."""
    # Arrange
    _, mock_db, mock_auth_admin = mock_firebase
    user_id = "uid-para-deletar"

    # Act
    response = client.delete(f"/auth/delete-account/{user_id}")

    # Assert
    assert response.status_code == HTTPStatus.OK
    assert response.json()["message"] == f"Usuário {user_id} deletado com sucesso."

    mock_auth_admin.delete_user.assert_called_once_with(user_id)
    mock_db.collection("usuarios").document(user_id).delete.assert_called_once()


def test_delete_account_user_not_found(mock_firebase):
    """Testa a tentativa de exclusão de um usuário que não existe."""
    # Arrange
    _, _, mock_auth_admin = mock_firebase
    mock_auth_admin.delete_user.side_effect = FirebaseError(
        code="auth/user-not-found", message="..."
    )

    # Act
    response = client.delete("/auth/delete-account/uid-inexistente")

    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Usuário não encontrado."


# --- Testes de Atualização de Usuário ---


def test_update_user_success(mock_firebase):
    """Testa a atualização bem-sucedida de um usuário (auth e firestore)."""
    # Arrange
    mock_firebase_instance, mock_db, mock_auth_admin = mock_firebase
    user_id = "user-to-be-updated"
    update_payload = {
        "nome_usuario": "José Cidadão Atualizado",
        "telefone": "82999998888",
        "email": "cidadao.atualizado@email.com",
        "senha": "nova_senha_segura",
        "role": "cidadao",
        "cpf": "111.222.333-44",
        "endereco": {
            "logradouro": "Nova Rua",
            "numero": "123",
            "bairro": "Novo Bairro",
            "cidade": "Maceió",
        },
    }

    final_user_data = update_payload.copy()
    del final_user_data["senha"]
    mock_db.collection("usuarios").document(
        user_id
    ).get().to_dict.return_value = final_user_data

    # Act
    response = client.put(f"/auth/user/update/{user_id}", json=update_payload)

    # Assert
    assert response.status_code == HTTPStatus.OK
    mock_auth_admin.update_user.assert_called_once()
    mock_db.collection("usuarios").document(user_id).update.assert_called_once()

    # CORREÇÃO AQUI: Adiciona a chamada .document(user_id) ao mock
    mock_db.collection("usuarios").document(user_id).collection("residencias").document(
        user_id
    ).set.assert_called_once()


def test_update_user_not_found(mock_firebase):
    """Testa a falha de atualização quando o usuário não é encontrado no Firebase Auth."""
    # Arrange
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

    # Act
    response = client.put(f"/auth/user/update/{user_id}", json=valid_payload)

    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Usuário não encontrado."


def test_update_user_firestore_error(mock_firebase):
    """Testa a falha de atualização quando ocorre um erro no Firestore."""
    # Arrange
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

    # Act
    response = client.put(f"/auth/user/update/{user_id}", json=valid_payload)

    # Assert
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert "Erro ao atualizar usuário" in response.json()["detail"]
