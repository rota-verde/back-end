import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from firebase_admin import auth as firebase_admin_auth
from firebase_admin.exceptions import FirebaseError
from main import app

client = TestClient(app)

# Dados de exemplo para os testes
user_create_data_cidadao = {
    "email": "cidadao@example.com",
    "senha": "password123",
    "nome_usuario": "Cidadao Teste",
    "telefone": "11999998888",
    "role": "cidadao",
    "cpf": "12345678900"
}

user_create_data_cooperativa = {
    "email": "cooperativa@example.com",
    "senha": "securepass",
    "nome_usuario": "Cooperativa Teste",
    "telefone": "21988887777",
    "role": "cooperativa",
    "cnpj": "12345678000199",
    "nome_cooperativa": "Coop Recicla",
    "area_atuacao": ["Pajucara", "Jatiuca"]
}

# ---- Testes para a rota /register ----

@patch('firebase_config.firebase_instance.auth')
@patch('firebase_config.db.collection')
def test_register_user_success_cidadao(mock_db_collection, mock_firebase_auth):
    """
    Testa o registro bem-sucedido de um usuário 'cidadao'.
    """
    mock_auth_instance = mock_firebase_auth.return_value
    mock_auth_instance.create_user_with_email_and_password.return_value = {
        'localId': 'test_uid_cidadao',
        'email': user_create_data_cidadao['email']
    }

    mock_usuarios_collection = MagicMock()
    mock_document_ref = MagicMock()
    mock_usuarios_collection.document.return_value = mock_document_ref
    mock_db_collection.return_value = mock_usuarios_collection

    response = client.post("/auth/register", json=user_create_data_cidadao)

    assert response.status_code == 201, response.text

    response_data = response.json()
    assert response_data["email"] == user_create_data_cidadao['email']
    assert response_data["nome_usuario"] == user_create_data_cidadao['nome_usuario']
    assert response_data["uid"] == 'test_uid_cidadao'
    assert response_data["role"] == "cidadao"
    assert response_data.get("cpf") is None
    assert "cnpj" not in response_data or response_data.get("cnpj") is None

    mock_auth_instance.create_user_with_email_and_password.assert_called_once_with(
        email=user_create_data_cidadao['email'],
        password=user_create_data_cidadao['senha']
    )
    mock_db_collection.assert_called_once_with("usuarios")
    mock_usuarios_collection.document.assert_called_once_with('test_uid_cidadao')

    expected_db_data = {
        "uid": "test_uid_cidadao",
        "email": user_create_data_cidadao['email'],
        "nome_usuario": user_create_data_cidadao['nome_usuario'],
        "telefone": user_create_data_cidadao['telefone'],
        "role": user_create_data_cidadao['role'],
        "cpf": user_create_data_cidadao['cpf'], # CPF é esperado no BD
        "cnpj": None,
        "cnh": None,
        "nome_cooperativa": None,
        "area_atuacao": None
    }
    call_args, _ = mock_document_ref.set.call_args
    actual_db_data = call_args[0]
    assert actual_db_data == expected_db_data
    mock_document_ref.set.assert_called_once_with(expected_db_data)

@patch('firebase_config.firebase_instance.auth')
@patch('firebase_config.db.collection')
def test_register_user_success_cooperativa(mock_db_collection, mock_firebase_auth):
    """
    Testa o registro bem-sucedido de um usuário 'cooperativa'.
    """
    mock_auth_instance = mock_firebase_auth.return_value
    mock_auth_instance.create_user_with_email_and_password.return_value = {
        'localId': 'test_uid_coop',
        'email': user_create_data_cooperativa['email']
    }

    mock_usuarios_collection = MagicMock()
    mock_document_ref = MagicMock()
    mock_usuarios_collection.document.return_value = mock_document_ref
    mock_db_collection.return_value = mock_usuarios_collection

    response = client.post("/auth/register", json=user_create_data_cooperativa)

    assert response.status_code == 201, response.text
    response_data = response.json()
    assert response_data["email"] == user_create_data_cooperativa['email']
    assert response_data["uid"] == 'test_uid_coop'
    assert response_data["role"] == "cooperativa"
    assert response_data.get("cnpj") is None
    assert response_data.get("nome_cooperativa") == user_create_data_cooperativa['nome_cooperativa']
    assert response_data.get("area_atuacao") is None
    assert "cpf" not in response_data or response_data.get("cpf") is None

    mock_auth_instance.create_user_with_email_and_password.assert_called_once_with(
        email=user_create_data_cooperativa['email'],
        password=user_create_data_cooperativa['senha']
    )
    mock_db_collection.assert_called_once_with("usuarios")
    mock_usuarios_collection.document.assert_called_once_with('test_uid_coop')

    expected_db_data = {
        "uid": "test_uid_coop",
        "email": user_create_data_cooperativa['email'],
        "nome_usuario": user_create_data_cooperativa['nome_usuario'],
        "telefone": user_create_data_cooperativa['telefone'],
        "role": user_create_data_cooperativa['role'],
        "cpf": None,
        "cnpj": user_create_data_cooperativa['cnpj'], # CNPJ é esperado no BD
        "cnh": None,
        "nome_cooperativa": user_create_data_cooperativa['nome_cooperativa'], # Esperado no BD
        "area_atuacao": user_create_data_cooperativa['area_atuacao'] # Esperado no BD
    }
    call_args, _ = mock_document_ref.set.call_args
    actual_db_data = call_args[0]
    assert actual_db_data == expected_db_data
    mock_document_ref.set.assert_called_once_with(expected_db_data)


@patch('firebase_config.firebase_instance.auth')
def test_register_user_email_already_exists(mock_firebase_auth):
    """
    Testa o caso em que o email já existe durante o registro.
    """
    mock_auth_instance = mock_firebase_auth.return_value
    mock_auth_instance.create_user_with_email_and_password.side_effect = \
        firebase_admin_auth.EmailAlreadyExistsError("Email already exists.", None, None)

    response = client.post("/auth/register", json=user_create_data_cidadao)

    assert response.status_code == 400
    assert response.json() == {"detail": f"Conta com o email {user_create_data_cidadao['email']} já existe."}

    mock_auth_instance.create_user_with_email_and_password.assert_called_once_with(
        email=user_create_data_cidadao['email'],
        password=user_create_data_cidadao['senha']
    )

@patch('firebase_config.firebase_instance.auth')
def test_register_user_firebase_error(mock_firebase_auth):
    """
    Testa um erro genérico do Firebase durante o registro.
    """
    mock_auth_instance = mock_firebase_auth.return_value
    mock_auth_instance.create_user_with_email_and_password.side_effect = \
        FirebaseError("123", "A generic Firebase error occurred.")

    response = client.post("/auth/register", json=user_create_data_cidadao)

    assert response.status_code == 500
    assert response.json() == {"detail": "Erro ao criar conta: A generic Firebase error occurred."}

    mock_auth_instance.create_user_with_email_and_password.assert_called_once_with(
        email=user_create_data_cidadao['email'],
        password=user_create_data_cidadao['senha']
    )