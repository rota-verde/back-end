# tests/models/test_route.py
from datetime import date, time
from schemas.rota import RouteCreate, RouteResponse, FeedbackSchema


def test_feedback_schema():
    feedback = FeedbackSchema(residencia_id="residencia1", coletado=True)
    assert feedback.residencia_id == "residencia1"
    assert feedback.coletado is True


def test_route_create():
    route = RouteCreate(
        motorista_id="1",
        residencias_incluidas_ids=["residencia1", "residencia2"],
        bairro="Centro",
        data=date(2023, 10, 1),
        hora_inicio=time(8, 0),
        pontos={
            "ponto1": [40.7128, -74.0060],
            "ponto2": [34.0522, -118.2437]
        }
    )
    assert route.motorista_id == "1"
    assert route.bairro == "Centro"
    assert len(route.residencias_incluidas_ids) == 2
    assert "ponto1" in route.pontos
    assert isinstance(route.pontos["ponto1"], list)
    assert isinstance(route.pontos["ponto1"][0], float)


def test_route_response():
    feedbacks = [
        FeedbackSchema(residencia_id="residencia1", coletado=True),
        FeedbackSchema(residencia_id="residencia2", coletado=False),
    ]
    route_response = RouteResponse(
        id="1",
        cooperativa_id="coop123",
        motorista_id="1",
        residencias_incluidas_ids=["residencia1", "residencia2"],
        data=date(2023, 10, 1),
        hora_inicio=time(8, 0),
        status=True,
        feedbacks=feedbacks
    )

    assert route_response.id == "1"
    assert route_response.cooperativa_id == "coop123"
    assert route_response.status is True
    assert len(route_response.feedbacks) == 2
    assert isinstance(route_response.feedbacks[0], FeedbackSchema)
    assert route_response.feedbacks[1].coletado is False
