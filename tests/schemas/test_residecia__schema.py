import pytest
from pydantic import ValidationError
from schemas.residencia import ResidenceCreate, ResidenceResponse


def test_create_residencia(residencia_data):
    endereco = residencia_data.endereco
    location = residencia_data.location

    assert endereco.logradouro == "Rua Teste"
    assert endereco.numero == "100"
    assert endereco.bairro == "Centro"
    assert endereco.cidade == "São Paulo"

    assert location["lat"] == -23.5505
    assert location["lng"] == -46.6333


def test_create_residencia_missing_field():
    with pytest.raises(ValidationError):
        ResidenceCreate(endereco="Rua Teste", numero="100", cidade="São Paulo")


def test_residencia_response():
    r = ResidenceResponse(
        id="abc123",
        endereco={
            "logradouro": "Rua Teste",
            "numero": "100",
            "bairro": "Centro",
            "cidade": "São Paulo",
        },
        location={"lat": -23.5, "lng": -46.6},
        coletavel=True,
    )
    assert r.coletavel is True
