import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from firebase_admin import auth as firebase_admin_auth
from firebase_admin.exceptions import FirebaseError

from main import app
from schemas.user import UserCreate, UserResponse

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
    "area_atuacao": "Plástico"
}

# ---- Testes para a rota /register ----

@patch('firebase_config.firebase_instance.auth') # Mock o cliente de autenticação do Pyrebase4
@patch('firebase_config.db.collection') # Mock o cliente Firestore
def test_register_user_success_cidadao(mock_db_collection, mock_firebase_auth):
    """
    Testa o registro bem-sucedido de um usuário 'cidadao'.
    """
    # Configuração do mock para firebase_instance.auth()
    mock_auth_instance = mock_firebase_auth.return_value
    mock_auth_instance.create_user_with_email_and_password.return_value = {
        'localId': 'test_uid_cidadao',
        'email': user_create_data_cidadao['email']
    }

    # Configuração do mock para db.collection("usuarios").document(uid).set(user_data)
    mock_usuarios_collection = MagicMock()
    mock_document_ref = MagicMock()
    mock_usuarios_collection.document.return_value = mock_document_ref
    mock_db_collection.return_value = mock_usuarios_collection

    # Faz a requisição POST para a rota /register
    response = client.post("/auth/register", json=user_create_data_cidadao)

    # Verifica o status code da resposta
    assert response.status_code == 201, response.text

    # Verifica o corpo da resposta
    response_data = response.json()
    assert response_data["email"] == user_create_data_cidadao['email']
    assert response_data["nome_usuario"] == user_create_data_cidadao['nome_usuario']
    assert response_data["uid"] == 'test_uid_cidadao'
    assert response_data["role"] == "cidadao"
    assert response_data["cpf"] == user_create_data_cidadao['cpf']
    assert "cnpj" not in response_data or response_data["cnpj"] is None # Garante que campos de outros roles não estão presentes

    # Verifica se as funções mockadas foram chamadas corretamente
    mock_auth_instance.create_user_with_email_and_password.assert_called_once_with(
        email=user_create_data_cidadao['email'],
        password=user_create_data_cidadao['senha']
    )
    mock_db_collection.assert_called_once_with("usuarios")
    mock_usuarios_collection.document.assert_called_once_with('test_uid_cidadao')

    # Captura os dados que seriam enviados ao Firestore
    expected_db_data = {
        "uid": "test_uid_cidadao",
        "email": user_create_data_cidadao['email'],
        "nome_usuario": user_create_data_cidadao['nome_usuario'],
        "telefone": user_create_data_cidadao['telefone'],
        "role": user_create_data_cidadao['role'],
        "cpf": user_create_data_cidadao['cpf'],
        "cnpj": None,
        "cnh": None,
        "nome_cooperativa": None,
        "area_atuacao": None
    }
    # Ajuste para model_dump(exclude={"senha"})
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
    assert response_data["cnpj"] == user_create_data_cooperativa['cnpj']
    assert response_data["nome_cooperativa"] == user_create_data_cooperativa['nome_cooperativa']
    assert "cpf" not in response_data or response_data["cpf"] is None

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
        "cnpj": user_create_data_cooperativa['cnpj'],
        "cnh": None,
        "nome_cooperativa": user_create_data_cooperativa['nome_cooperativa'],
        "area_atuacao": user_create_data_cooperativa['area_atuacao']
    }
    call_args, _ = mock_document_ref.set.call_args
    actual_db_data = call_args[0]

    assert actual_db_data == expected_db_data
    mock_document_ref.set.assert_called_once_with(expected_db_data)


@patch('firebase_config.firebase_instance.auth') # Mock o cliente de autenticação do Pyrebase4
def test_register_user_email_already_exists(mock_firebase_auth):
    """
    Testa o caso em que o email já existe durante o registro.
    """
    # Configuração do mock para simular EmailAlreadyExistsError
    # Para Pyrebase4, a exceção é geralmente uma HTTPError com uma mensagem específica.
    # Se você estiver usando firebase_admin.auth diretamente para create_user,
    # a exceção seria firebase_admin.auth.EmailAlreadyExistsError
    # Pyrebase4 pode encapsular isso ou ter sua própria maneira de indicar.
    # Vamos assumir que create_user_with_email_and_password em Pyrebase4
    # levanta uma exceção que o seu código captura como auth.EmailAlreadyExistsError.
    # Se Pyrebase4 levanta uma exceção genérica que você depois verifica a mensagem,
    # você precisaria ajustar o mock para essa exceção genérica.
    # No seu código, você está usando `firebase_admin.auth.EmailAlreadyExistsError`.
    mock_auth_instance = mock_firebase_auth.return_value
    mock_auth_instance.create_user_with_email_and_password.side_effect = \
        firebase_admin_auth.EmailAlreadyExistsError("Email already exists.", None, None) # Adicionei os argumentos faltantes para o construtor

    response = client.post("/auth/register", json=user_create_data_cidadao)

    assert response.status_code == 400
    assert response.json() == {"detail": f"Conta com o email {user_create_data_cidadao['email']} já existe."}

    mock_auth_instance.create_user_with_email_and_password.assert_called_once_with(
        email=user_create_data_cidadao['email'],
        password=user_create_data_cidadao['senha']
    )

@patch('firebase_config.firebase_instance.auth') # Mock o cliente de autenticação do Pyrebase4
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