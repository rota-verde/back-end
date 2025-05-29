import pytest
from pydantic import ValidationError
from schemas.cooperativa import RotaBase, RotaUpdate
from schemas.rota import RouteCreate
from datetime import datetime, date, time


def test_rota_create():
    rota = RouteCreate(
        data=date(2023, 10, 1),
        hora_inicio=time(8, 0),
        motorista_id="motorista1",
        bairro="Centro",
        pontos={"ponto1": [1.0, 2.0], "ponto2": [3.0, 4.0]},
        residencias_ids=["res1", "res2"],
        residencias_incluidas_ids=["res1"],
    )

    assert rota.data == date(2023, 10, 1)
    assert rota.hora_inicio == time(8, 0)
    assert rota.motorista_id == "motorista1"
    assert rota.bairro == "Centro"
    assert rota.pontos == {"ponto1": [1.0, 2.0], "ponto2": [3.0, 4.0]}
    assert rota.residencias_incluidas_ids == ["res1"]


def test_rota_update_partial():
    rota = RotaUpdate(
        nome="Rota Atualizada",
        data=datetime(2025, 1, 2, 9, 0),
        motoristas=["motorista2"],
        pontos={"ponto3": 3.0},
        residencias_ids=["res3"],
    )

    assert rota.nome == "Rota Atualizada"
    assert rota.data == datetime(2025, 1, 2, 9, 0)
    assert rota.motoristas == ["motorista2"]
    assert rota.pontos == {"ponto3": 3.0}
    assert rota.residencias_ids == ["res3"]


def test_rota_base_valid(rota_base):
    assert rota_base.nome == "Rota A"
    assert rota_base.motoristas == ["motorista1"]


def test_rota_missing_motoristas():
    with pytest.raises(ValidationError):
        RotaBase(
            nome="Rota B",
            data="2025-01-01T08:00:00",
            motoristas=None,
            pontos={},
            residencias_ids=[],
        )
