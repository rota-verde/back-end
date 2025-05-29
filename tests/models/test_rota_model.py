import pytest
from datetime import datetime
from models.rota import RotaModel


def test_rota_model_valid_data():
    rota = RotaModel(
        id="rota123",
        cooperativa_id="coop001",
        nome="Rota Centro",
        data=datetime.now(),
        motorista_id="mot001",
        residencias_ids=["res1", "res2"],
        ativa=True,
    )
    assert rota.ativa is True
    assert isinstance(rota.residencias_ids, list)


def test_rota_model_missing_required_field():
    with pytest.raises(ValueError):
        RotaModel(
            id="rota123",
            cooperativa_id="coop001",
            nome="Rota Centro",
            data=datetime.now(),
            motorista_id="mot001",
            # residencias_ids missing
        )
