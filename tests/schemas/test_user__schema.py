import pytest
from pydantic import ValidationError
from schemas.user import UserLogin


def test_cidadao_user_fixture(cidadao_user):
    assert cidadao_user.nome_usuario == "Maria"
    assert cidadao_user.email == "maria@email.com"
    assert cidadao_user.telefone == "11999999999"
    assert cidadao_user.role == "cidadao"
    assert cidadao_user.senha == "senha123"
    assert cidadao_user.cpf == "12345678909"
    endereco = cidadao_user.endereco
    assert endereco.logradouro == "Rua X"
    assert endereco.numero == "123"
    assert endereco.bairro == "Centro"
    assert endereco.cidade == "São Paulo"
    assert cidadao_user.materiais_reciclaveis is None


def test_motorista_user_fixture(motorista_user):
    assert motorista_user.nome_usuario == "José"
    assert motorista_user.email == "jose@email.com"
    assert motorista_user.telefone == "11999999999"
    assert motorista_user.role == "motorista"
    assert motorista_user.senha == "senha123"
    assert motorista_user.cnh is None


def test_cooperativa_user_fixture(cooperativa_user):
    assert cooperativa_user.nome_usuario == "Coop Verde"
    assert cooperativa_user.email == "coop@email.com"
    assert cooperativa_user.telefone == "11999999999"
    assert cooperativa_user.role == "cooperativa"
    assert cooperativa_user.senha == "senha123"
    assert cooperativa_user.cnpj == "1234567890001"


def test_user_login_valid():
    login = UserLogin(email="user@email.com", senha="123456")
    assert login.email == "user@email.com"


def test_user_login_invalid_email():
    with pytest.raises(ValidationError):
        UserLogin(email="invalid", senha="123")
