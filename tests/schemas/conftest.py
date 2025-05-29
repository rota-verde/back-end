import pytest
from datetime import datetime
from schemas.user import UserCreate
from schemas.cooperativa import RotaBase
from schemas.residencia import ResidenceCreate
from schemas.residencia import EnderecoSchema


@pytest.fixture
def endereco_dict():
    return {
        "logradouro": "Rua X",
        "numero": "123",
        "bairro": "Centro",
        "cidade": "São Paulo",
    }


@pytest.fixture
def cidadao_user(endereco_dict):
    return UserCreate(
        nome_usuario="Maria",
        email="maria@email.com",
        telefone="11999999999",
        role="cidadao",
        senha="senha123",
        cpf="12345678909",
        endereco=endereco_dict,
    )


@pytest.fixture
def motorista_user():
    return UserCreate(
        nome_usuario="José",
        email="jose@email.com",
        telefone="11999999999",
        role="motorista",
        senha="senha123",
        nome_cooperativa="Cooperativa X",
    )


@pytest.fixture
def cooperativa_user(endereco_dict):
    return UserCreate(
        nome_usuario="Coop Verde",
        email="coop@email.com",
        telefone="11999999999",
        role="cooperativa",
        senha="senha123",
        nome_cooperativa="Coop Verde",
        cnpj="1234567890001",
        area_atuacao=["Centro", "Zona Sul"],
        materiais_reciclaveis=["papel", "plástico"],
        endereco=endereco_dict,
    )


@pytest.fixture
def residencia_data():
    return ResidenceCreate(
        endereco={
            "logradouro": "Rua Teste",
            "numero": "100",
            "bairro": "Centro",
            "cidade": "São Paulo",
        },
        location={"lat": -23.5505, "lng": -46.6333},
    )


@pytest.fixture
def rota_base():
    return RotaBase(
        nome="Rota A",
        data=datetime(2023, 10, 1, 8, 0),
        motoristas=["motorista1"],
        pontos={"ponto1": 1.0},  # valor float, conforme requerido
        residencias_incluidas_ids=["res1", "res2"],
    )
