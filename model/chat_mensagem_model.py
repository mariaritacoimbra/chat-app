from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ChatMensagem:
    """
    Representa uma mensagem enviada em uma sala de chat.

    Atributos:
        id: Identificador único da mensagem
        sala_id: ID da sala onde foi enviada
        usuario_id: ID do usuário que enviou
        mensagem: Conteúdo da mensagem
        data_envio: Data/hora do envio
        lida_em: Data/hora em que foi lida (None se não lida)
    """
    id: int
    sala_id: str
    usuario_id: int
    mensagem: str
    data_envio: datetime
    lida_em: Optional[datetime] = None