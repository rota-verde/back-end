import pytest
from models.user import UserModel


def test_user_model_required_fields():
    user = UserModel(uid="123", email="test@example.com", senha="abc123")
    assert user.uid == "123"
    assert user.email == "test@example.com"
    assert user.senha == "abc123"


def test_user_model_optional_fields():
    user = UserModel(
        uid="123",
        email="test@example.com",
        senha="abc123",
        cpf="123.456.789-00",
        area_atuacao=["bairro1", "bairro2"],
    )
    assert user.cpf == "123.456.789-00"
    assert user.area_atuacao == ["bairro1", "bairro2"]


def test_user_model_invalid_missing_uid():
    with pytest.raises(ValueError):
        UserModel(email="test@example.com", senha="abc123")
