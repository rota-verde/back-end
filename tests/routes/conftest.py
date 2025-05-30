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
    Cria e retorna mocks para as dependências do Firebase (movido de test_auth_route.py).
    Esta fixture pode ser usada por qualquer teste que precise simular o Firebase.
    """
    mock_firebase_instance = MagicMock()
    mocker.patch("routes.auth.firebase_instance", mock_firebase_instance)

    mock_db = MagicMock()
    mocker.patch("routes.auth.db", mock_db)

    mock_auth_admin = MagicMock()
    mocker.patch("routes.auth.auth", mock_auth_admin)

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
