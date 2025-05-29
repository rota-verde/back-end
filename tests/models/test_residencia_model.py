import pytest
from models.residencia import ResidenceModel, EnderecoModel


def test_residencia_model_valid():
    endereco = EnderecoModel(
        logradouro="Rua A", numero="123", bairro="Centro", cidade="Cidade X"
    )
    residencia = ResidenceModel(
        id="res001",
        user_id="user123",
        endereco=endereco,
        location={"lat": -9.0, "lng": -35.0},
        coletavel=True,
    )
    assert residencia.coletavel is True
    assert residencia.location["lat"] == -9.0


def test_residencia_model_missing_location():
    endereco = EnderecoModel(
        logradouro="Rua A", numero="123", bairro="Centro", cidade="Cidade X"
    )
    with pytest.raises(ValueError):
        ResidenceModel(
            id="res001",
            user_id="user123",
            endereco=endereco,
            # missing location
        )


def test_endereco_model_bairros_atendidos():
    endereco = EnderecoModel(
        logradouro="Rua X",
        numero="12",
        bairro="Bairro A",
        bairros_atendidos=["Bairro A", "Bairro B"],
        cidade="Cidade Y",
    )
    assert "Bairro B" in endereco.bairros_atendidos
