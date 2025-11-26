from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Usuario:
    """
    Representa um usuário do sistema.

    Atributos:
        id: Identificador único do usuário
        nome: Nome completo do usuário
        email: E-mail (único no sistema)
        senha: Hash da senha (nunca armazenar senha em texto plano!)
        data_cadastro: Data/hora do cadastro
    """
    id: int
    nome: str
    email: str
    senha: str
    data_cadastro: Optional[datetime] = None