# tests/models/test_user.py
import pytest
from schemas.user import UserCreate, UserLogin, UserResponse

@pytest.fixture
def cidadao_data():
    return {
        "nome_usuario": "Maria Cidadã",
        "email": "maria@exemplo.com",
        "telefone": "+551199999999",
        "role": "cidadao",
        "senha": "senha123",
        "cpf": "12345678901"
    }

@pytest.fixture
def motorista_data():
    return {
        "nome_usuario": "Carlos Motorista",
        "email": "carlos@exemplo.com",
        "telefone": "+551188888888",
        "role": "motorista",
        "senha": "senha456",
        "cpf": "23456789012",
        "cnh": "CNH123456"
    }

@pytest.fixture
def cooperativa_data():
    return {
        "nome_usuario": "Coop Exemplo",
        "email": "coop@exemplo.com",
        "telefone": "+551177777777",
        "role": "cooperativa",
        "senha": "senha789",
        "cnpj": "9876543210001",
        "nome_cooperativa": "Cooperativa Centro",
        "area_atuacao": ["Centro", "Farol"]
    }

def test_user_create_cidadao(cidadao_data):
    user = UserCreate(**cidadao_data)
    assert user.nome_usuario == "Maria Cidadã"
    assert user.role == "cidadao"
    assert user.cpf is not None
    assert user.cnh is None

def test_user_create_motorista(motorista_data):
    user = UserCreate(**motorista_data)
    assert user.nome_usuario == "Carlos Motorista"
    assert user.role == "motorista"
    assert user.cnh == "CNH123456"
    assert user.cnpj is None

def test_user_create_cooperativa(cooperativa_data):
    user = UserCreate(**cooperativa_data)
    assert user.nome_usuario == "Coop Exemplo"
    assert user.role == "cooperativa"
    assert user.cnpj is not None
    assert user.nome_cooperativa == "Cooperativa Centro"
    assert user.area_atuacao == ["Centro", "Farol"]

def test_user_login():
    login_data = {
        "email": "joao@email.com",
        "senha": "senha123"
    }
    login = UserLogin(**login_data)
    assert login.email == "joao@email.com"
    assert login.senha == "senha123"

def test_user_response_cidadao(cidadao_data):
    user = UserResponse(uid="user-1", **cidadao_data)
    assert user.uid == "user-1"
    assert user.email == "maria@exemplo.com"
    assert user.role == "cidadao"

def test_user_response_motorista(motorista_data):
    user = UserResponse(uid="user-2", **motorista_data)
    assert user.uid == "user-2"
    assert user.role == "motorista"

def test_user_response_cooperativa(cooperativa_data):
    user = UserResponse(uid="user-3", **cooperativa_data)
    assert user.uid == "user-3"
    assert user.role == "cooperativa"
