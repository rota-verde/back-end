from schemas.residencia import EnderecoSchema, ResidenceCreate, ResidenceResponse


def test_endereco_schema_model():
    """Testa a criação e os atributos do EnderecoSchema."""
    endereco_data = {
        "logradouro": "Avenida da Paz",
        "numero": "1020",
        "bairro": "Ponta Verde",
        "cidade": "Maceió"
    }
    endereco = EnderecoSchema(**endereco_data)

    assert endereco.logradouro == endereco_data["logradouro"]
    assert endereco.numero == endereco_data["numero"]
    assert endereco.bairro == endereco_data["bairro"]
    assert endereco.cidade == endereco_data["cidade"]
    # Alternativamente, para Pydantic models, você pode comparar dicionários:
    # assert endereco.model_dump() == endereco_data # Para Pydantic V2
    # assert endereco.dict() == endereco_data # Para Pydantic V1

def test_residence_create_model():
    """Testa a criação e os atributos do ResidenceCreate schema."""
    endereco_data = {
        "logradouro": "Rua das Acácias",
        "numero": "55",
        "bairro": "Jardim Felicidade",
        "cidade": "Rio Largo"
    }
    residence_create_data = {
        "endereco": endereco_data, # Pode ser um dict ou uma instância de EnderecoSchema
        "location": {
            "latitude": -9.5505, # Coordenadas de exemplo para Alagoas
            "longitude": -35.8333
        }
    }
    
    # Instanciando com dicionário para endereco
    residence = ResidenceCreate(**residence_create_data)

    # Verificando o endereço aninhado
    assert residence.endereco.logradouro == endereco_data["logradouro"]
    assert residence.endereco.numero == endereco_data["numero"]
    assert residence.endereco.bairro == endereco_data["bairro"]
    assert residence.endereco.cidade == endereco_data["cidade"]
    # Ou, se você instanciou residence.endereco com EnderecoSchema(**endereco_data)
    # assert residence.endereco == EnderecoSchema(**endereco_data)

    # Verificando a localização
    assert isinstance(residence.location, dict)
    assert residence.location["latitude"] == residence_create_data["location"]["latitude"]
    assert residence.location["longitude"] == residence_create_data["location"]["longitude"]
    assert len(residence.location) == 2 # Garante que não há chaves extras

def test_residence_response_model():
    """Testa a criação e os atributos do ResidenceResponse schema."""
    endereco_data = {
        "logradouro": "Travessa São José",
        "numero": "7B",
        "bairro": "Vergel do Lago",
        "cidade": "Maceió"
    }
    residence_response_data = {
        "id": "res_abc_123",
        "endereco": endereco_data, # Pode ser um dict ou uma instância de EnderecoSchema
        "location": {
            "latitude": -9.6800, # Coordenadas de exemplo
            "longitude": -35.7500
        },
        "coletavel": False
    }
    
    response = ResidenceResponse(**residence_response_data)

    assert response.id == residence_response_data["id"]
    
    # Verificando o endereço aninhado
    assert response.endereco.logradouro == endereco_data["logradouro"]
    assert response.endereco.numero == endereco_data["numero"]
    assert response.endereco.bairro == endereco_data["bairro"]
    assert response.endereco.cidade == endereco_data["cidade"]
    # Ou, para uma comparação mais completa do objeto EnderecoSchema:
    # endereco_obj = EnderecoSchema(**endereco_data)
    # assert response.endereco == endereco_obj
    # Nota: se você passou um dict para 'endereco' na instanciação de ResidenceResponse,
    # Pydantic o converterá para EnderecoSchema. Comparar com endereco_obj é mais robusto.

    # Verificando a localização
    assert isinstance(response.location, dict)
    assert response.location["latitude"] == residence_response_data["location"]["latitude"]
    assert response.location["longitude"] == residence_response_data["location"]["longitude"]
    assert len(response.location) == 2

    assert response.coletavel is residence_response_data["coletavel"]