from pydantic import BaseModel, field_validator


class CriarSalaDTO(BaseModel):
    """
    DTO para criar ou obter uma sala de chat.

    Valida:
    - ID do outro usuário é positivo
    """
    outro_usuario_id: int

    @field_validator('outro_usuario_id')
    @classmethod
    def validar_outro_usuario_id(cls, v):
        """Valida que o ID é um número positivo."""
        if v <= 0:
            raise ValueError('ID do usuário deve ser um número positivo.')
        return v


class EnviarMensagemDTO(BaseModel):
    """
    DTO para enviar uma mensagem em uma sala.

    Valida:
    - ID da sala não vazio
    - Mensagem não vazia e com tamanho máximo de 5000 caracteres
    """
    sala_id: str
    mensagem: str

    @field_validator('sala_id')
    @classmethod
    def validar_sala_id(cls, v):
        """Valida que o ID da sala não está vazio."""
        v = v.strip()
        if not v:
            raise ValueError('ID da sala é obrigatório.')
        return v

    @field_validator('mensagem')
    @classmethod
    def validar_mensagem(cls, v):
        """Valida que a mensagem não está vazia e tem tamanho adequado."""
        v = v.strip()
        if not v:
            raise ValueError('Mensagem não pode estar vazia.')
        if len(v) > 5000:
            raise ValueError('Mensagem muito longa (máximo 5000 caracteres).')
        return v