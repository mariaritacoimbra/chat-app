from fastapi import Request
from typing import Optional


def adicionar_mensagem(request: Request, tipo: str, texto: str):
    """
    Adiciona uma mensagem flash à sessão.

    Args:
        request: Objeto Request do FastAPI
        tipo: Tipo da mensagem (success, danger, warning, info)
        texto: Texto da mensagem

    Os tipos correspondem às classes do Bootstrap Alert.
    """
    if "flash_messages" not in request.session:
        request.session["flash_messages"] = []
    request.session["flash_messages"].append({"tipo": tipo, "texto": texto})


def informar_sucesso(request: Request, texto: str):
    """
    Adiciona mensagem de sucesso (verde).

    Args:
        request: Objeto Request do FastAPI
        texto: Texto da mensagem

    Exemplo:
        informar_sucesso(request, "Cadastro realizado com sucesso!")
    """
    adicionar_mensagem(request, "success", texto)


def informar_erro(request: Request, texto: str):
    """
    Adiciona mensagem de erro (vermelho).

    Args:
        request: Objeto Request do FastAPI
        texto: Texto da mensagem

    Exemplo:
        informar_erro(request, "E-mail ou senha incorretos.")
    """
    adicionar_mensagem(request, "danger", texto)


def obter_mensagens(request: Request) -> list:
    """
    Obtém e limpa as mensagens flash da sessão.

    As mensagens são removidas após serem lidas (comportamento flash).

    Args:
        request: Objeto Request do FastAPI

    Returns:
        Lista de dicionários com tipo e texto das mensagens

    Exemplo:
        mensagens = obter_mensagens(request)
        # [{"tipo": "success", "texto": "Login realizado!"}]
    """
    mensagens = request.session.get("flash_messages", [])
    request.session["flash_messages"] = []
    return mensagens