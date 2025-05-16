from datetime import date, time
from schemas.rota import RouteCreate, RouteResponse, FeedbackSchema

def test_route_create_model():
    route = RouteCreate(
        motorista_id="1",
        residencias_incluidas=["residencia1", "residencia2"],
        bairro="Centro",
        data=date(2023, 10, 1),
        hora_inicio=time(8, 0, 0),
        pontos={
            "ponto1": 40.7128,
            "ponto2": -74.0060
        }
    )

    assert route.motorista_id == "1"
    assert route.bairro == "Centro"
    assert route.data == date(2023, 10, 1)
    assert len(route.residencias_incluidas) == 2
    assert isinstance(route.pontos, dict)

def test_feedback_schema_model():
    feedback = FeedbackSchema(
        residencia_id="residencia1",
        coletado=True
    )

    assert feedback.residencia_id == "residencia1"
    assert feedback.coletado is True

def test_route_response_model():
    feedbacks = [
        FeedbackSchema(residencia_id="residencia1", coletado=True),
        FeedbackSchema(residencia_id="residencia2", coletado=False),
    ]

    route_response = RouteResponse(
        id="1",
        cooperativa_id="1",
        motorista_id="1",
        residencias_incluidas=["residencia1", "residencia2"],
        data=date(2023, 10, 1),
        hora_inicio=time(8, 0, 0),
        status=True,
        feedbacks=feedbacks
    )

    assert route_response.id == "1"
    assert route_response.status is True
    assert len(route_response.feedbacks) == 2
    assert route_response.feedbacks[1].coletado is False