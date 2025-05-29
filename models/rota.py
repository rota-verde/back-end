from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime


class RotaModel(BaseModel):
    id: str
    cooperativa_id: str
    motorista_id: str  # lista de uids
    residencias_incluidas_ids: List[str]  # lista de ids das residências
    data: datetime
    coleta_iniciada_em: Optional[datetime] = None
    status: bool = False
    pontos: Dict[str, List[float]]
    coleta_finalizada_em: Optional[datetime] = None
