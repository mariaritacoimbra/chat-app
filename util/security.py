from passlib.context import CryptContext

# Contexto para hash de senhas com bcrypt
# "deprecated=auto" marca esquemas antigos como obsoletos automaticamente
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def criar_hash_senha(senha: str) -> str:
    """
    Cria hash seguro da senha usando bcrypt.

    Args:
        senha: Senha em texto plano

    Returns:
        Hash da senha (inclui salt automaticamente)

    Exemplo:
        >>> hash = criar_hash_senha("minha_senha_123")
        >>> # hash será algo como: $2b$12$...
    """
    return pwd_context.hash(senha)


def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
    """
    Verifica se a senha corresponde ao hash armazenado.

    Args:
        senha_plana: Senha digitada pelo usuário
        senha_hash: Hash armazenado no banco de dados

    Returns:
        True se a senha estiver correta, False caso contrário

    Exemplo:
        >>> hash = criar_hash_senha("minha_senha")
        >>> verificar_senha("minha_senha", hash)
        True
        >>> verificar_senha("senha_errada", hash)
        False
    """
    return pwd_context.verify(senha_plana, senha_hash)