from schemas.residencia import EnderecoSchema, ResidenceCreate, ResidenceResponse

def test_endereco_schema_model():
    endereco = EnderecoSchema(
        logradouro="Rua Exemplo",
        numero="123",
        bairro="Centro",
        cidade="São Paulo"
    )

    assert endereco.logradouro == "Rua Exemplo"
    assert endereco.numero == "123"
    assert endereco.bairro == "Centro"
    assert endereco.cidade == "São Paulo"

def test_residence_create_model():
    residence = ResidenceCreate(
        endereco=EnderecoSchema(
            logradouro="Rua Exemplo",
            numero="123",
            bairro="Centro",
            cidade="São Paulo"
        ),
        location={
            "latitude": -23.5505,
            "longitude": -46.6333
        }
    )

    assert residence.endereco.bairro == "Centro"
    assert isinstance(residence.location, dict)
    assert "latitude" in residence.location
    assert "longitude" in residence.location

def test_residence_response_model():
    response = ResidenceResponse(
        id="1",
        endereco=EnderecoSchema(
            logradouro="Rua Exemplo",
            numero="123",
            bairro="Centro",
            cidade="São Paulo"
        ),
        location={
            "latitude": -23.5505,
            "longitude": -46.6333
        },
        coletavel=True
    )

    assert response.id == "1"
    assert response.endereco.cidade == "São Paulo"
    assert response.location["latitude"] == -23.5505
    assert response.coletavel is True