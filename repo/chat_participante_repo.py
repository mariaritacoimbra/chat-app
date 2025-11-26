from typing import Optional
from model.chat_participante_model import ChatParticipante
from util.database import get_connection


def obter_por_sala_e_usuario(sala_id: str, usuario_id: int) -> Optional[ChatParticipante]:
    """
    Verifica se um usuário é participante de uma sala.

    Args:
        sala_id: ID da sala
        usuario_id: ID do usuário

    Returns:
        Objeto ChatParticipante se for participante, None caso contrário

    Usado para validar permissão de acesso às mensagens de uma sala.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM chat_participante WHERE sala_id = ? AND usuario_id = ?",
            (sala_id, usuario_id)
        )
        row = cursor.fetchone()
        if row:
            return ChatParticipante(
                sala_id=row["sala_id"],
                usuario_id=row["usuario_id"],
                ultima_leitura=row["ultima_leitura"]
            )
    return None


def listar_conversas_por_usuario(usuario_id: int, limite: int = 20, offset: int = 0) -> list[dict]:
    """
    Lista todas as conversas de um usuário com informações do outro participante.

    Esta é uma query complexa que retorna:
    - Dados da sala
    - Dados do outro participante
    - Última mensagem enviada
    - Contador de mensagens não lidas

    Args:
        usuario_id: ID do usuário
        limite: Número máximo de conversas a retornar
        offset: Número de conversas a pular (para paginação)

    Returns:
        Lista de dicionários com:
        - sala_id: ID da sala
        - ultima_atividade: Data da última atividade
        - outro_usuario: {id, nome, email}
        - ultima_mensagem: Texto da última mensagem
        - nao_lidas: Contador de mensagens não lidas

    Exemplo de retorno:
        [{
            "sala_id": "1_2",
            "ultima_atividade": "2024-01-15 10:30:00",
            "outro_usuario": {
                "id": 2,
                "nome": "Maria",
                "email": "maria@email.com"
            },
            "ultima_mensagem": "Olá, tudo bem?",
            "nao_lidas": 3
        }]
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                cs.id as sala_id,
                cs.ultima_atividade,
                u.id as outro_usuario_id,
                u.nome as outro_usuario_nome,
                u.email as outro_usuario_email,
                (
                    SELECT mensagem FROM chat_mensagem
                    WHERE sala_id = cs.id
                    ORDER BY data_envio DESC LIMIT 1
                ) as ultima_mensagem,
                (
                    SELECT COUNT(*) FROM chat_mensagem
                    WHERE sala_id = cs.id AND usuario_id != ? AND lida_em IS NULL
                ) as nao_lidas
            FROM chat_participante cp
            INNER JOIN chat_sala cs ON cp.sala_id = cs.id
            INNER JOIN chat_participante cp2 ON cs.id = cp2.sala_id AND cp2.usuario_id != ?
            INNER JOIN usuario u ON cp2.usuario_id = u.id
            WHERE cp.usuario_id = ?
            ORDER BY cs.ultima_atividade DESC
            LIMIT ? OFFSET ?
        """, (usuario_id, usuario_id, usuario_id, limite, offset))

        return [
            {
                "sala_id": row["sala_id"],
                "ultima_atividade": row["ultima_atividade"],
                "outro_usuario": {
                    "id": row["outro_usuario_id"],
                    "nome": row["outro_usuario_nome"],
                    "email": row["outro_usuario_email"]
                },
                "ultima_mensagem": row["ultima_mensagem"],
                "nao_lidas": row["nao_lidas"]
            }
            for row in cursor.fetchall()
        ]