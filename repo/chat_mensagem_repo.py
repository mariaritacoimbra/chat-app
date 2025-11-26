from datetime import datetime
from typing import Optional
from model.chat_mensagem_model import ChatMensagem
from util.database import get_connection


def inserir(sala_id: str, usuario_id: int, mensagem: str) -> ChatMensagem:
    """
    Insere uma nova mensagem em uma sala.

    Args:
        sala_id: ID da sala
        usuario_id: ID do usuário que está enviando
        mensagem: Conteúdo da mensagem

    Returns:
        Objeto ChatMensagem com os dados da mensagem criada
    """
    data_envio = datetime.now()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_mensagem (sala_id, usuario_id, mensagem, data_envio) VALUES (?, ?, ?, ?)",
            (sala_id, usuario_id, mensagem, data_envio)
        )
        mensagem_id = cursor.lastrowid

    return ChatMensagem(
        id=mensagem_id,
        sala_id=sala_id,
        usuario_id=usuario_id,
        mensagem=mensagem,
        data_envio=data_envio,
        lida_em=None
    )


def listar_por_sala(sala_id: str, limite: int = 50, offset: int = 0) -> list[ChatMensagem]:
    """
    Lista mensagens de uma sala, ordenadas por data (mais recentes primeiro).

    Args:
        sala_id: ID da sala
        limite: Número máximo de mensagens a retornar
        offset: Número de mensagens a pular (para paginação)

    Returns:
        Lista de objetos ChatMensagem

    Nota: As mensagens vêm em ordem DESC (mais recentes primeiro).
    O frontend deve inverter se quiser exibir em ordem cronológica.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM chat_mensagem
            WHERE sala_id = ?
            ORDER BY data_envio DESC
            LIMIT ? OFFSET ?
        """, (sala_id, limite, offset))

        return [
            ChatMensagem(
                id=row["id"],
                sala_id=row["sala_id"],
                usuario_id=row["usuario_id"],
                mensagem=row["mensagem"],
                data_envio=row["data_envio"],
                lida_em=row["lida_em"]
            )
            for row in cursor.fetchall()
        ]


def marcar_como_lidas(sala_id: str, usuario_id: int) -> bool:
    """
    Marca como lidas todas as mensagens não lidas de outros usuários em uma sala.

    Args:
        sala_id: ID da sala
        usuario_id: ID do usuário que está lendo (marca mensagens de OUTROS)

    Returns:
        True se alguma mensagem foi marcada, False caso contrário

    Nota: Marca apenas mensagens enviadas por OUTROS usuários.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE chat_mensagem
            SET lida_em = ?
            WHERE sala_id = ? AND usuario_id != ? AND lida_em IS NULL
        """, (datetime.now(), sala_id, usuario_id))
        return cursor.rowcount > 0


def contar_nao_lidas_por_usuario(usuario_id: int) -> int:
    """
    Conta total de mensagens não lidas para um usuário em todas as suas salas.

    Args:
        usuario_id: ID do usuário

    Returns:
        Número total de mensagens não lidas

    Usado para exibir o badge no botão do chat.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM chat_mensagem cm
            INNER JOIN chat_participante cp ON cm.sala_id = cp.sala_id
            WHERE cp.usuario_id = ? AND cm.usuario_id != ? AND cm.lida_em IS NULL
        """, (usuario_id, usuario_id))
        return cursor.fetchone()[0]


def contar_nao_lidas_por_sala(sala_id: str, usuario_id: int) -> int:
    """
    Conta mensagens não lidas em uma sala específica para um usuário.

    Args:
        sala_id: ID da sala
        usuario_id: ID do usuário

    Returns:
        Número de mensagens não lidas na sala

    Usado para exibir o badge em cada conversa na lista.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM chat_mensagem
            WHERE sala_id = ? AND usuario_id != ? AND lida_em IS NULL
        """, (sala_id, usuario_id))
        return cursor.fetchone()[0]