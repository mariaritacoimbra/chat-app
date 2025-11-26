from typing import Optional
from model.usuario_model import Usuario
from util.database import get_connection


def inserir(nome: str, email: str, senha_hash: str) -> Usuario:
    """
    Insere um novo usuário no banco.

    Args:
        nome: Nome completo do usuário
        email: E-mail do usuário
        senha_hash: Hash da senha (já processado pelo bcrypt)

    Returns:
        Objeto Usuario com o ID gerado

    Nota: A senha deve ser hasheada ANTES de chamar esta função.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuario (nome, email, senha) VALUES (?, ?, ?)",
            (nome, email, senha_hash)
        )
        usuario_id = cursor.lastrowid
    return Usuario(id=usuario_id, nome=nome, email=email, senha=senha_hash)


def obter_por_email(email: str) -> Optional[Usuario]:
    """
    Busca usuário pelo email.

    Args:
        email: E-mail do usuário

    Returns:
        Objeto Usuario se encontrado, None caso contrário

    Usado principalmente no login para verificar credenciais.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuario WHERE email = ?", (email,))
        row = cursor.fetchone()
        if row:
            return Usuario(
                id=row["id"],
                nome=row["nome"],
                email=row["email"],
                senha=row["senha"],
                data_cadastro=row["data_cadastro"]
            )
    return None


def obter_por_id(usuario_id: int) -> Optional[Usuario]:
    """
    Busca usuário pelo ID.

    Args:
        usuario_id: ID do usuário

    Returns:
        Objeto Usuario se encontrado, None caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuario WHERE id = ?", (usuario_id,))
        row = cursor.fetchone()
        if row:
            return Usuario(
                id=row["id"],
                nome=row["nome"],
                email=row["email"],
                senha=row["senha"],
                data_cadastro=row["data_cadastro"]
            )
    return None


def email_existe(email: str) -> bool:
    """
    Verifica se o email já está cadastrado.

    Args:
        email: E-mail a verificar

    Returns:
        True se o email já existe, False caso contrário

    Usado no cadastro para evitar e-mails duplicados.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM usuario WHERE email = ?", (email,))
        return cursor.fetchone() is not None


def buscar_por_termo(termo: str, usuario_id_excluir: int, limite: int = 10) -> list[Usuario]:
    """
    Busca usuários por nome ou email, excluindo o próprio usuário.

    Args:
        termo: Termo de busca (busca parcial em nome e email)
        usuario_id_excluir: ID do usuário a excluir dos resultados
        limite: Número máximo de resultados

    Returns:
        Lista de objetos Usuario que correspondem à busca

    Usado para buscar usuários ao iniciar nova conversa.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        termo_like = f"%{termo}%"
        cursor.execute("""
            SELECT * FROM usuario
            WHERE id != ? AND (nome LIKE ? OR email LIKE ?)
            LIMIT ?
        """, (usuario_id_excluir, termo_like, termo_like, limite))
        return [
            Usuario(
                id=row["id"],
                nome=row["nome"],
                email=row["email"],
                senha=row["senha"],
                data_cadastro=row["data_cadastro"]
            )
            for row in cursor.fetchall()
        ]