import pytest
from http import HTTPStatus
from unittest.mock import MagicMock
from datetime import date, datetime

# As fixtures 'client', 'mock_firebase' e 'created_motorista' são injetadas a partir do conftest.py

# --- Constantes para o Teste ---
FIXED_DATE = date(2025, 5, 30)
FIXED_DATETIME = datetime(2025, 5, 30, 10, 30, 0)
FIXED_DATETIME_ISO = FIXED_DATETIME.isoformat()

# --- Testes das Rotas de Motorista ---


def test_listar_rotas_hoje_motorista_success(
    client, mock_firebase, created_motorista, mocker
):
    """
    Testa a listagem de rotas de um motorista para a data de hoje (fixa).
    """
    # Arrange
    mock_date = mocker.patch("routes.motorista.date")
    mock_date.today.return_value = FIXED_DATE

    motorista_id = created_motorista["uid"]
    _, mock_db, _ = mock_firebase

    mock_data_1 = {
        "id": "rota-1",
        "nome": "Rota Manhã - Jatiúca",
        "cooperativa_id": "coop-1",
        "motorista_id": motorista_id,
        "residencias_incluidas_ids": ["res-1"],
        "bairro": "Jatiúca",
        "data": str(FIXED_DATE),
        "hora_inicio": "08:00",
        "pontos": {"coordinates": []},
        "status": False,
    }
    mock_data_2 = {
        "id": "rota-2",
        "nome": "Rota Tarde - Ponta Verde",
        "cooperativa_id": "coop-1",
        "motorista_id": motorista_id,
        "residencias_incluidas_ids": ["res-2"],
        "bairro": "Ponta Verde",
        "data": str(FIXED_DATE),
        "hora_inicio": "14:00",
        "pontos": {"coordinates": [-35.71, -9.65]},  # <-- AJUSTADO
        "status": False,
    }

    mock_rota1 = MagicMock()
    mock_rota1.to_dict.return_value = mock_data_1
    mock_rota2 = MagicMock()
    mock_rota2.to_dict.return_value = mock_data_2

    mock_db.collection().where().where().stream.return_value = [mock_rota1, mock_rota2]

    # Act
    response = client.get(f"/motorista/rotas/hoje?current_user_id={motorista_id}")

    # Assert
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["nome"] == "Rota Manhã - Jatiúca"


def test_obter_rota_atual_success(client, mock_firebase, created_motorista, mocker):
    """
    Testa a obtenção de uma rota que já está em andamento.
    """
    # Arrange
    motorista_id = created_motorista["uid"]
    mocker.patch("routes.motorista.verificar_user")
    mocker.patch(
        "routes.motorista.acompanhar_rota",
        return_value={"proxima_parada": "Rua ABC, 123", "eta": "5 minutos"},
    )
    _, mock_db, _ = mock_firebase

    complete_rota_data = {
        "nome": "Rota Ativa",
        "status": True,
        "cooperativa_id": "coop-1",
        "motorista_id": motorista_id,
        "residencias_incluidas_ids": ["res-1", "res-2"],
        "bairro": "Jatiúca",
        "data": str(FIXED_DATE),
        "hora_inicio": "10:30",
        "pontos": {"coordinates": [-35.73, -9.66]},  # <-- AJUSTADO
    }

    mock_rota_doc = MagicMock()
    mock_rota_doc.id = "rota-ativa-123"
    mock_rota_doc.to_dict.return_value = complete_rota_data
    mock_db.collection().where().where().limit().stream.return_value = [mock_rota_doc]

    # Act
    response = client.get(f"/motorista/rota/atual?current_user_id={motorista_id}")

    # Assert
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["id"] == "rota-ativa-123"
    assert data["proxima_parada"] == "Rua ABC, 123"


def test_obter_rota_atual_not_found(client, mock_firebase, created_motorista, mocker):
    """
    Testa o cenário onde não há nenhuma rota em andamento para o motorista.
    """
    # Arrange
    motorista_id = created_motorista["uid"]
    mocker.patch("routes.motorista.verificar_user")
    _, mock_db, _ = mock_firebase

    mock_db.collection().where().where().limit().stream.return_value = []

    # Act
    response = client.get(f"/motorista/rota/atual?current_user_id={motorista_id}")

    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert "Nenhuma rota iniciada" in response.json()["detail"]


def test_iniciar_rota_success(client, mock_firebase, mocker):
    """
    Testa o início de uma rota com sucesso.
    """
    # Arrange
    mock_datetime = mocker.patch("routes.motorista.datetime")
    mock_datetime.now.return_value = FIXED_DATETIME

    rota_id = "rota-para-iniciar"
    _, mock_db, _ = mock_firebase

    mock_rota_ref = mock_db.collection().document()
    mock_rota_ref.get.return_value.exists = True

    # Act
    response = client.post(f"/motorista/iniciar_rota/{rota_id}")

    # Assert
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()["message"] == "Rota iniciada com sucesso."

    mock_rota_ref.update.assert_called_once_with(
        {"inicio": FIXED_DATETIME_ISO, "status": True}
    )


def test_iniciar_rota_not_found(client, mock_firebase):
    """
    Testa a falha ao tentar iniciar uma rota que não existe.
    """
    # Arrange
    rota_id = "rota-inexistente"
    _, mock_db, _ = mock_firebase
    mock_db.collection().document().get.return_value.exists = False

    # Act
    response = client.post(f"/motorista/iniciar_rota/{rota_id}")

    # Assert
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "Rota não encontrada."


def test_finalizar_rota_success(client, mock_firebase, mocker):
    """
    Testa a finalização de uma rota com sucesso.
    """
    # Arrange
    mock_datetime = mocker.patch("routes.motorista.datetime")
    mock_datetime.now.return_value = FIXED_DATETIME

    rota_id = "rota-para-finalizar"
    _, mock_db, _ = mock_firebase

    mock_rota_ref = mock_db.collection().document()
    mock_rota_ref.get.return_value.exists = True

    # Act
    response = client.post(f"/motorista/finalizar_rota/{rota_id}")

    # Assert
    assert response.status_code == HTTPStatus.CREATED
    assert response.json()["message"] == "Rota finalizada com sucesso."

    mock_rota_ref.update.assert_called_once_with(
        {"fim": FIXED_DATETIME_ISO, "status": False}
    )
