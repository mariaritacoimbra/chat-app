from dataclasses import dataclass
from datetime import datetime


@dataclass
class ChatSala:
    """
    Representa uma sala de chat privada entre dois usuários.

    O ID da sala segue o padrão: "menor_id_maior_id"
    Isso garante que dois usuários sempre tenham a mesma sala.

    Exemplo:
        Usuários com ID 3 e 7 sempre usam a sala "3_7"
        Usuários com ID 7 e 3 também usam a sala "3_7"

    Atributos:
        id: Identificador único da sala (formato "menor_id_maior_id")
        criada_em: Data/hora de criação da sala
        ultima_atividade: Data/hora da última mensagem enviada
    """
    id: str
    criada_em: datetime
    ultima_atividade: datetime