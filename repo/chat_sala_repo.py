from datetime import datetime
from typing import Optional
from model.chat_sala_model import ChatSala
from util.database import get_connection


def gerar_sala_id(usuario1_id: int, usuario2_id: int) -> str:
    """
    Gera ID único e determinístico para sala entre dois usuários.

    O ID é gerado ordenando os IDs dos usuários, garantindo que
    dois usuários sempre tenham o mesmo ID de sala.

    Args:
        usuario1_id: ID do primeiro usuário
        usuario2_id: ID do segundo usuário

    Returns:
        ID da sala no formato "menor_id_maior_id"

    Exemplos:
        >>> gerar_sala_id(3, 7)
        '3_7'
        >>> gerar_sala_id(7, 3)
        '3_7'
    """
    ids_ordenados = sorted([usuario1_id, usuario2_id])
    return f"{ids_ordenados[0]}_{ids_ordenados[1]}"


def obter_por_id(sala_id: str) -> Optional[ChatSala]:
    """
    Busca uma sala pelo ID.

    Args:
        sala_id: ID da sala

    Returns:
        Objeto ChatSala se encontrado, None caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chat_sala WHERE id = ?", (sala_id,))
        row = cursor.fetchone()
        if row:
            return ChatSala(
                id=row["id"],
                criada_em=row["criada_em"],
                ultima_atividade=row["ultima_atividade"]
            )
    return None


def criar_ou_obter_sala(usuario1_id: int, usuario2_id: int) -> ChatSala:
    """
    Cria uma nova sala ou retorna sala existente entre dois usuários.

    Esta função é idempotente - chamar múltiplas vezes retorna a mesma sala.
    Também cria os registros de participantes automaticamente.

    Args:
        usuario1_id: ID do primeiro usuário
        usuario2_id: ID do segundo usuário

    Returns:
        Objeto ChatSala (existente ou recém-criado)
    """
    sala_id = gerar_sala_id(usuario1_id, usuario2_id)

    # Verifica se já existe
    sala_existente = obter_por_id(sala_id)
    if sala_existente:
        return sala_existente

    # Cria nova sala
    agora = datetime.now()
    with get_connection() as conn:
        cursor = conn.cursor()

        # Insere a sala
        cursor.execute(
            "INSERT INTO chat_sala (id, criada_em, ultima_atividade) VALUES (?, ?, ?)",
            (sala_id, agora, agora)
        )

        # Insere os participantes
        cursor.execute(
            "INSERT INTO chat_participante (sala_id, usuario_id) VALUES (?, ?)",
            (sala_id, usuario1_id)
        )
        cursor.execute(
            "INSERT INTO chat_participante (sala_id, usuario_id) VALUES (?, ?)",
            (sala_id, usuario2_id)
        )

    return ChatSala(id=sala_id, criada_em=agora, ultima_atividade=agora)


def atualizar_ultima_atividade(sala_id: str):
    """
    Atualiza o timestamp de última atividade da sala.

    Chamado sempre que uma nova mensagem é enviada na sala.

    Args:
        sala_id: ID da sala
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE chat_sala SET ultima_atividade = ? WHERE id = ?",
            (datetime.now(), sala_id)
        )