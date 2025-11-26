import json
import asyncio
from fastapi import APIRouter, Request, Form, Query, status, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Optional
from pydantic import ValidationError
from datetime import datetime

from dtos.chat_dto import CriarSalaDTO, EnviarMensagemDTO
from repo import usuario_repo, chat_sala_repo, chat_mensagem_repo, chat_participante_repo
from util.auth_decorator import requer_autenticacao
from util.chat_manager import chat_manager

# Cria o router com prefixo /chat e tag para documentação
router = APIRouter(prefix="/chat", tags=["Chat"])


def formatar_data_iso(valor):
    """
    Converte data para formato ISO string.
    SQLite retorna datas como strings, então precisamos verificar o tipo.

    Args:
        valor: datetime object ou string

    Returns:
        String ISO ou None
    """
    if valor is None:
        return None
    if isinstance(valor, str):
        return valor  # Já é string
    if isinstance(valor, datetime):
        return valor.isoformat()
    return str(valor)


# =============================================================================
# SSE - STREAM DE MENSAGENS EM TEMPO REAL
# =============================================================================

@router.get("/stream")
@requer_autenticacao()
async def stream_mensagens(request: Request, usuario_logado: Optional[dict] = None):
    """
    Endpoint SSE para receber mensagens em tempo real.

    Server-Sent Events (SSE) é uma tecnologia que permite o servidor
    enviar dados para o cliente em tempo real através de uma conexão HTTP.

    Cada usuário mantém UMA conexão que recebe mensagens de TODAS as suas salas.

    Returns:
        StreamingResponse com content-type text/event-stream

    Formato das mensagens SSE:
        data: {"tipo": "nova_mensagem", "sala_id": "1_2", "mensagem": {...}}
    """
    usuario_id = usuario_logado["id"]

    async def event_generator():
        """Gerador assíncrono que produz eventos SSE."""
        # Registra conexão e obtém a queue
        queue = await chat_manager.connect(usuario_id)
        try:
            while True:
                # Aguarda próxima mensagem na queue (bloqueia até receber)
                evento = await queue.get()
                # Formata como SSE (data: JSON\n\n)
                sse_data = f"data: {json.dumps(evento)}\n\n"
                yield sse_data
                # Pequeno delay para não sobrecarregar
                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            # Conexão cancelada pelo cliente
            print(f"[SSE] Conexão cancelada para usuário {usuario_id}")
        finally:
            # Sempre desconecta ao finalizar
            await chat_manager.disconnect(usuario_id)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",      # Não cachear
            "Connection": "keep-alive",        # Manter conexão aberta
            "X-Accel-Buffering": "no",        # Desabilitar buffering (nginx)
        }
    )


# =============================================================================
# SALAS
# =============================================================================

@router.post("/salas")
@requer_autenticacao()
async def criar_ou_obter_sala(
    request: Request,
    outro_usuario_id: int = Form(...),
    usuario_logado: Optional[dict] = None
):
    """
    Cria uma nova sala de chat ou retorna a existente entre dois usuários.

    Form data:
        outro_usuario_id: ID do usuário com quem criar a sala

    Returns:
        JSON com sala_id e dados do outro usuário

    Validações:
    - Não pode criar sala consigo mesmo
    - O outro usuário deve existir
    """
    try:
        # Valida os dados
        dto = CriarSalaDTO(outro_usuario_id=outro_usuario_id)
        usuario_id = usuario_logado["id"]

        # Não pode criar sala consigo mesmo
        if dto.outro_usuario_id == usuario_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é possível criar sala de chat consigo mesmo."
            )

        # Verifica se outro usuário existe
        outro_usuario = usuario_repo.obter_por_id(dto.outro_usuario_id)
        if not outro_usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado."
            )

        # Cria ou obtém a sala (função idempotente)
        sala = chat_sala_repo.criar_ou_obter_sala(usuario_id, dto.outro_usuario_id)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "sala_id": sala.id,
                "outro_usuario": {
                    "id": outro_usuario.id,
                    "nome": outro_usuario.nome,
                    "email": outro_usuario.email
                }
            }
        )

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.errors()[0]["msg"] if e.errors() else "Dados inválidos."
        )


# =============================================================================
# CONVERSAS
# =============================================================================

@router.get("/conversas")
@requer_autenticacao()
async def listar_conversas(
    request: Request,
    limite: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    usuario_logado: Optional[dict] = None
):
    """
    Lista todas as conversas do usuário com último mensagem e contador de não lidas.

    Query params:
        limite: Número máximo de conversas (1-100, default 20)
        offset: Número de conversas a pular (para paginação)

    Returns:
        JSON com lista de conversas
    """
    usuario_id = usuario_logado["id"]
    conversas = chat_participante_repo.listar_conversas_por_usuario(usuario_id, limite, offset)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"conversas": conversas}
    )


# =============================================================================
# MENSAGENS
# =============================================================================

@router.get("/mensagens/{sala_id}")
@requer_autenticacao()
async def listar_mensagens(
    request: Request,
    sala_id: str,
    limite: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    usuario_logado: Optional[dict] = None
):
    """
    Lista mensagens de uma sala com paginação.

    Path params:
        sala_id: ID da sala

    Query params:
        limite: Número máximo de mensagens (1-100, default 50)
        offset: Número de mensagens a pular

    Returns:
        JSON com lista de mensagens (mais recentes primeiro)

    Validações:
    - Usuário deve ser participante da sala
    """
    usuario_id = usuario_logado["id"]

    # Verifica se é participante da sala
    participante = chat_participante_repo.obter_por_sala_e_usuario(sala_id, usuario_id)
    if not participante:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem acesso a esta sala."
        )

    mensagens = chat_mensagem_repo.listar_por_sala(sala_id, limite, offset)

    # Converte para formato JSON serializável
    mensagens_dict = [
        {
            "id": m.id,
            "sala_id": m.sala_id,
            "usuario_id": m.usuario_id,
            "mensagem": m.mensagem,
            "data_envio": formatar_data_iso(m.data_envio),
            "lida_em": formatar_data_iso(m.lida_em)
        }
        for m in mensagens
    ]

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"mensagens": mensagens_dict}
    )


@router.post("/mensagens")
@requer_autenticacao()
async def enviar_mensagem(
    request: Request,
    sala_id: str = Form(...),
    mensagem: str = Form(...),
    usuario_logado: Optional[dict] = None
):
    """
    Envia uma mensagem em uma sala de chat.

    Form data:
        sala_id: ID da sala
        mensagem: Conteúdo da mensagem

    Returns:
        JSON com dados da mensagem enviada

    Fluxo:
    1. Valida os dados
    2. Verifica permissão
    3. Insere mensagem no banco
    4. Atualiza última atividade da sala
    5. Envia via SSE para os participantes
    """
    try:
        # Valida os dados
        dto = EnviarMensagemDTO(sala_id=sala_id, mensagem=mensagem)
        usuario_id = usuario_logado["id"]

        # Verifica se é participante
        participante = chat_participante_repo.obter_por_sala_e_usuario(dto.sala_id, usuario_id)
        if not participante:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem acesso a esta sala."
            )

        # Insere a mensagem no banco
        nova_mensagem = chat_mensagem_repo.inserir(dto.sala_id, usuario_id, dto.mensagem)

        # Atualiza última atividade da sala
        chat_sala_repo.atualizar_ultima_atividade(dto.sala_id)

        # Prepara mensagem para broadcast SSE
        mensagem_sse = {
            "tipo": "nova_mensagem",
            "sala_id": nova_mensagem.sala_id,
            "mensagem": {
                "id": nova_mensagem.id,
                "sala_id": nova_mensagem.sala_id,
                "usuario_id": nova_mensagem.usuario_id,
                "mensagem": nova_mensagem.mensagem,
                "data_envio": formatar_data_iso(nova_mensagem.data_envio),
                "lida_em": None
            }
        }

        # Broadcast para participantes da sala via SSE
        await chat_manager.broadcast_para_sala(dto.sala_id, mensagem_sse)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "sucesso": True,
                "mensagem": mensagem_sse["mensagem"]
            }
        )

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.errors()[0]["msg"] if e.errors() else "Dados inválidos."
        )


@router.post("/mensagens/lidas/{sala_id}")
@requer_autenticacao()
async def marcar_mensagens_lidas(
    request: Request,
    sala_id: str,
    usuario_logado: Optional[dict] = None
):
    """
    Marca todas as mensagens não lidas de uma sala como lidas.

    Path params:
        sala_id: ID da sala

    Returns:
        JSON com sucesso=True

    Marca como lidas apenas mensagens de OUTROS usuários.
    """
    usuario_id = usuario_logado["id"]

    # Verifica se é participante
    participante = chat_participante_repo.obter_por_sala_e_usuario(sala_id, usuario_id)
    if not participante:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem acesso a esta sala."
        )

    chat_mensagem_repo.marcar_como_lidas(sala_id, usuario_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"sucesso": True}
    )


# =============================================================================
# BUSCA DE USUÁRIOS
# =============================================================================

@router.get("/usuarios/buscar")
@requer_autenticacao()
async def buscar_usuarios(
    request: Request,
    q: str = Query(..., min_length=2),
    usuario_logado: Optional[dict] = None
):
    """
    Busca usuários por nome ou email para iniciar nova conversa.

    Query params:
        q: Termo de busca (mínimo 2 caracteres)

    Returns:
        JSON com lista de usuários encontrados

    O próprio usuário é excluído dos resultados.
    """
    usuario_id = usuario_logado["id"]
    usuarios = usuario_repo.buscar_por_termo(q, usuario_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "usuarios": [
                {"id": u.id, "nome": u.nome, "email": u.email}
                for u in usuarios
            ]
        }
    )


# =============================================================================
# CONTADORES
# =============================================================================

@router.get("/mensagens/nao-lidas/total")
@requer_autenticacao()
async def contar_nao_lidas(
    request: Request,
    usuario_logado: Optional[dict] = None
):
    """
    Retorna o total de mensagens não lidas do usuário.

    Returns:
        JSON com total de mensagens não lidas

    Usado para exibir o badge no botão do chat.
    """
    usuario_id = usuario_logado["id"]
    total = chat_mensagem_repo.contar_nao_lidas_por_usuario(usuario_id)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"total": total}
    )