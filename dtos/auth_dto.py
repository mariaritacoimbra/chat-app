from pydantic import BaseModel, Field, field_validator, model_validator
import re


class LoginDTO(BaseModel):
    """
    DTO para validação do login.

    Valida:
    - E-mail no formato correto
    - Senha com tamanho adequado
    """
    email: str = Field(..., description="E-mail do usuário")
    senha: str = Field(..., min_length=6, max_length=128, description="Senha do usuário")

    @field_validator("email")
    @classmethod
    def validar_email(cls, v):
        """Valida e normaliza o e-mail."""
        v = v.strip().lower()
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError("E-mail inválido.")
        return v


class CadastroDTO(BaseModel):
    """
    DTO para validação do cadastro de usuário.

    Valida:
    - Nome com pelo menos 3 caracteres
    - E-mail no formato correto
    - Senha com pelo menos 6 caracteres
    - Confirmação de senha igual à senha
    """
    nome: str = Field(..., min_length=3, max_length=100, description="Nome completo")
    email: str = Field(..., description="E-mail do usuário")
    senha: str = Field(..., min_length=6, max_length=128, description="Senha")
    confirmar_senha: str = Field(..., min_length=6, max_length=128, description="Confirmação da senha")

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, v):
        """Valida e normaliza o nome."""
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Nome deve ter pelo menos 3 caracteres.")
        return v

    @field_validator("email")
    @classmethod
    def validar_email(cls, v):
        """Valida e normaliza o e-mail."""
        v = v.strip().lower()
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError("E-mail inválido.")
        return v

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, v):
        """Valida tamanho da senha."""
        if len(v) < 6:
            raise ValueError("Senha deve ter pelo menos 6 caracteres.")
        return v

    @model_validator(mode="after")
    def validar_senhas_coincidem(self):
        """Valida se senha e confirmação são iguais."""
        if self.senha != self.confirmar_senha:
            raise ValueError("As senhas não coincidem.")
        return self