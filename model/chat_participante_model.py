from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ChatParticipante:
    """
    Representa a participação de um usuário em uma sala.

    Esta entidade relaciona usuários às suas salas de chat.
    A chave primária é composta por (sala_id, usuario_id).

    Atributos:
        sala_id: ID da sala de chat
        usuario_id: ID do usuário participante
        ultima_leitura: Data/hora da última leitura das mensagens
    """
    sala_id: str
    usuario_id: int
    ultima_leitura: Optional[datetime] = None