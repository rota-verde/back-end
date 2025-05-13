from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class RotaModel(BaseModel):
    id: str
    cooperativa_id: str
    nome: str
    data: datetime
    motorista_id: str  # lista de uids
    residencias_ids: List[str]  # lista de ids das residências
    coleta_iniciada_em: Optional[datetime] = None
    coleta_finalizada_em: Optional[datetime] = None
    ativa: bool = False
