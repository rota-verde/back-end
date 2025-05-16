import pytest
from schemas.user import UserCreate, UserResponse


# -------- Instancias --------
@pytest.fixture
def cidadao_data():
    return {
        "nome_usuario": "Maria Cidadã",
        "email": "maria@exemplo.com",
        "telefone": "+5511988888888",
        "role": "cidadao",
        "senha": "senhaSegura123",
        "cpf": "12345678901"
    }

@pytest.fixture
def motorista_data():
    return {
        "nome_usuario": "Carlos Motorista",
        "email": "carlos@exemplo.com",
        "telefone": "+5511977777777",
        "role": "motorista",
        "senha": "senhaSegura123",
        "cpf": "23456789012",
        "cnh": "CNH123456"
    }

@pytest.fixture
def cooperativa_data():
    return {
        "nome_usuario": "Coop Exemplo",
        "email": "coop@exemplo.com",
        "telefone": "+5511966666666",
        "role": "cooperativa",
        "senha": "senhaSegura123",
        "cnpj": "9876543210001",
        "nome_cooperativa": "Cooperativa Centro"
    }

# -------- TESTES Criacao -------- #

def test_create_cidadao(cidadao_data):
    user = UserCreate(**cidadao_data)
    assert user.role == "cidadao"
    assert user.cpf is not None
    assert user.cnh is None
    assert user.cnpj is None
    assert user.nome_cooperativa is None

def test_create_motorista(motorista_data):
    user = UserCreate(**motorista_data)
    assert user.role == "motorista"
    assert user.cnh is not None
    assert user.cpf is not None
    assert user.cnpj is None
    assert user.nome_cooperativa is None

def test_create_cooperativa(cooperativa_data):
    user = UserCreate(**cooperativa_data)
    assert user.role == "cooperativa"
    assert user.cnpj is not None
    assert user.nome_cooperativa == "Cooperativa Centro"
    assert user.cnh is None
    assert user.cpf is None

# -------- TESTES Resposta -------- #

def test_user_response_cidadao(cidadao_data):
    user = UserResponse(uid="user-1", **cidadao_data)
    assert user.uid == "user-1"
    assert user.role == "cidadao"
    assert user.cpf == cidadao_data["cpf"]
    assert user.cnh is None
    assert user.cnpj is None

def test_user_response_motorista(motorista_data):
    user = UserResponse(uid="user-2", **motorista_data)
    assert user.uid == "user-2"
    assert user.role == "motorista"
    assert user.cnh == motorista_data["cnh"]
    assert user.cpf == motorista_data["cpf"]
    assert user.cnpj is None

def test_user_response_cooperativa(cooperativa_data):
    user = UserResponse(uid="user-3", **cooperativa_data)
    assert user.uid == "user-3"
    assert user.role == "cooperativa"
    assert user.cnpj == cooperativa_data["cnpj"]
    assert user.nome_cooperativa == cooperativa_data["nome_cooperativa"]
    assert user.cpf is None
    assert user.cnh is None
