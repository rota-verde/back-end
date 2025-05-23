from datetime import date, time
from schemas.rota import RouteCreate, RouteResponse, FeedbackSchema

def test_feedback_schema():
    """Testa a criação e os atributos do schema FeedbackSchema."""
    feedback_data = {
        "residencia_id": "res_001_alpha",
        "coletado": True
    }
    feedback = FeedbackSchema(**feedback_data)

    assert feedback.residencia_id == feedback_data["residencia_id"]
    assert feedback.coletado is feedback_data["coletado"]

def test_route_create():
    """Testa a criação e os atributos do schema RouteCreate."""
    route_create_data = {
        "motorista_id": "mot_123_xyz",
        "residencias_incluidas_ids": ["res_A01", "res_B02", "res_C03"],
        "bairro": "Jatiúca",
        "data": date(2025, 6, 10), # Usando a data atual (22/05/2025) como referência para o exemplo
        "hora_inicio": time(7, 45, 0),
        "pontos": {
            "garagem_saida": [-9.6580, -35.7030], # Coordenadas de exemplo em Maceió
            "res_A01": [-9.6550, -35.7010],
            "res_B02": [-9.6520, -35.6990]
        }
    }
    route = RouteCreate(**route_create_data)

    assert route.motorista_id == route_create_data["motorista_id"]
    assert route.residencias_incluidas_ids == route_create_data["residencias_incluidas_ids"]
    assert route.bairro == route_create_data["bairro"]
    assert route.data == route_create_data["data"]
    assert route.hora_inicio == route_create_data["hora_inicio"]
    assert route.pontos == route_create_data["pontos"]
    assert len(route.residencias_incluidas_ids) == 3
    assert "garagem_saida" in route.pontos
    assert isinstance(route.pontos["garagem_saida"], list)
    assert isinstance(route.pontos["garagem_saida"][0], float)

def test_route_response():
    """Testa a criação e os atributos do schema RouteResponse."""
    
    # A lista 'feedbacks_data' simula a criação de dados de feedback,
    # como no seu exemplo original. No entanto, ela não é usada para
    # instanciar 'RouteResponse', pois o schema 'RouteResponse' atual
    # não possui um campo 'feedbacks'.
    feedbacks_data = [
        {"residencia_id": "res_001_feedback", "coletado": True},
        {"residencia_id": "res_002_feedback", "coletado": False},
    ]
    # Você poderia instanciar FeedbackSchema aqui se quisesse testá-los:
    # feedbacks_objects = [FeedbackSchema(**data) for data in feedbacks_data]

    # Dados para instanciar RouteResponse
    route_response_data = {
        "id": "resp_rota_987",
        "cooperativa_id": "coop_central_mcz",
        "motorista_id": "mot_efg_654",
        "residencias_incluidas_ids": ["casa_verde", "apto_azul"],
        "bairro": "Ponta Grossa",
        "data": date(2025, 5, 22), # Data atual
        "hora_inicio": time(13, 0, 0),
        "status": True,
        "pontos": {
            "inicio_rota": [-9.6700, -35.7500], # Coordenadas de exemplo em Maceió
            "casa_verde": [-9.6725, -35.7530],
            "fim_rota": [-9.6750, -35.7560]
        }
    }
    
    route_resp = RouteResponse(**route_response_data)

    assert route_resp.id == route_response_data["id"]
    assert route_resp.cooperativa_id == route_response_data["cooperativa_id"]
    assert route_resp.motorista_id == route_response_data["motorista_id"]
    assert route_resp.residencias_incluidas_ids == route_response_data["residencias_incluidas_ids"]
    assert route_resp.bairro == route_response_data["bairro"]
    assert route_resp.data == route_response_data["data"]
    assert route_resp.hora_inicio == route_response_data["hora_inicio"]
    assert route_resp.status is route_response_data["status"]
    assert route_resp.pontos == route_response_data["pontos"]
    assert len(route_resp.pontos) == 3