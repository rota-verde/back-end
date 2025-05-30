import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

# Importações do projeto
from main import app  # Importa a instância principal do FastAPI
from firebase_admin.exceptions import FirebaseError

# --- Fixtures de Configuração e Mocks ---


@pytest.fixture(scope="session")
def client():
    """
    Fixture que cria e disponibiliza um TestClient para toda a sessão de testes.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_firebase(mocker):
    """
    Cria e retorna mocks para as dependências do Firebase.
    Agora, aplica o patch em todos os módulos de rota que usam as dependências.
    """
    # --- Mocks dos objetos ---
    mock_firebase_instance = MagicMock()
    mock_db = MagicMock()
    mock_auth_admin = MagicMock()

    # --- Patches para a rota de autenticação ---
    mocker.patch("routes.auth.firebase_instance", mock_firebase_instance)
    mocker.patch("routes.auth.db", mock_db)
    mocker.patch("routes.auth.auth", mock_auth_admin)

    # --- Patches para a rotas de usuarios ---
    mocker.patch("routes.cidadao.db", mock_db)
    mocker.patch("routes.motorista.db", mock_db)
    mocker.patch("routes.cooperativa.db", mock_db)

    return mock_firebase_instance, mock_db, mock_auth_admin


# --- Payloads como Constantes (para Parametrize) ---

PAYLOAD_CIDADAO = {
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

PAYLOAD_MOTORISTA = {
    "nome_usuario": "Carlos Motorista",
    "telefone": "82933334444",
    "email": "motorista.teste@email.com",
    "senha": "senha_motorista_123",
    "role": "motorista",
    "cnh": "12345678901",
    "nome_cooperativa": "Recicla-AL",
}

PAYLOAD_COOPERATIVA = {
    "nome_usuario": "Coop Recicla Bem",
    "telefone": "8233334444",
    "email": "coop.teste@email.com",
    "senha": "senha_coop_123",
    "role": "cooperativa",
    "cnpj": "12.345.678/0001-99",
    "nome_cooperativa": "Coop Recicla Bem",
    "area_atuacao": ["Ponta Verde", "Jatiúca"],
    "materiais_reciclaveis": ["Plástico", "Papelão", "Metal"],
}

RESIDENCIA_PAYLOAD = {
    "endereco": {
        "logradouro": "Avenida Fernandes Lima",
        "numero": "1024",
        "bairro": "Farol",
        "cidade": "Maceió",
    },
    "location": {"latitude": -9.6434, "longitude": -35.7333},
}


# --- Fixtures de Payloads (para injeção direta) ---


@pytest.fixture
def cidadao_payload():
    return PAYLOAD_CIDADAO.copy()


@pytest.fixture
def motorista_payload():
    return PAYLOAD_MOTORISTA.copy()


@pytest.fixture
def cooperativa_payload():
    return PAYLOAD_COOPERATIVA.copy()


@pytest.fixture
def residencia_payload():
    return RESIDENCIA_PAYLOAD.copy()


# --- Fixtures de Usuários Já Criados ---


@pytest.fixture
def created_cidadao(client, mock_firebase, cidadao_payload):
    """
    Cria um usuário cidadão via API (mock) e retorna seus dados, incluindo o UID.
    Útil para testes que precisam de um cidadão já existente.
    """
    mock_firebase_instance, _, _ = mock_firebase
    uid = "uid-cidadao-fixture-123"

    # Configura o mock para a chamada de criação de usuário
    mock_firebase_instance.auth().create_user_with_email_and_password.return_value = {
        "localId": uid
    }

    # Faz a chamada de registro
    response = client.post("/auth/register", json=cidadao_payload)
    assert response.status_code == 201  # Garante que a criação (mock) foi bem sucedida

    # Retorna o corpo da resposta, que contém o UID e outros dados
    return response.json()


@pytest.fixture
def created_motorista(client, mock_firebase, motorista_payload):
    """Cria um usuário motorista via API (mock) e retorna seus dados."""
    mock_firebase_instance, _, _ = mock_firebase
    uid = "uid-motorista-fixture-456"
    mock_firebase_instance.auth().create_user_with_email_and_password.return_value = {
        "localId": uid
    }
    response = client.post("/auth/register", json=motorista_payload)
    assert response.status_code == 201
    return response.json()
