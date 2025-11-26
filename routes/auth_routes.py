
from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from dtos.auth_dto import LoginDTO, CadastroDTO
from repo import usuario_repo
from util.security import criar_hash_senha, verificar_senha
from util.auth_decorator import criar_sessao, destruir_sessao, obter_usuario_logado
from util.flash_messages import informar_sucesso, informar_erro, obter_mensagens

# Cria o router para agrupar as rotas de autenticação
router = APIRouter()
templates = Jinja2Templates(directory="templates")


# =============================================================================
# LOGIN
# =============================================================================

@router.get("/login", response_class=HTMLResponse)
async def get_login(request: Request, redirect: str = "/home"):
    """
    Exibe a página de login.

    Query params:
        redirect: URL para redirecionar após login bem-sucedido

    Se já estiver logado, redireciona direto para a página de destino.
    """
    # Se já está logado, redireciona
    if obter_usuario_logado(request):
        return RedirectResponse(redirect, status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("login.html", {
        "request": request,
        "redirect": redirect,
        "mensagens": obter_mensagens(request)
    })


@router.post("/login")
async def post_login(
    request: Request,
    email: str = Form(...),
    senha: str = Form(...),
    redirect: str = Form(default="/home")
):
    """
    Processa o login do usuário.

    Form data:
        email: E-mail do usuário
        senha: Senha do usuário
        redirect: URL para redirecionar após sucesso

    Fluxo:
    1. Valida os dados com o DTO
    2. Busca usuário pelo e-mail
    3. Verifica a senha com bcrypt
    4. Cria a sessão
    5. Redireciona para página de destino
    """
    try:
        # Valida os dados com Pydantic
        dto = LoginDTO(email=email, senha=senha)

        # Busca o usuário no banco
        usuario = usuario_repo.obter_por_email(dto.email)

        # Verifica credenciais (usuário existe E senha correta)
        if not usuario or not verificar_senha(dto.senha, usuario.senha):
            informar_erro(request, "E-mail ou senha incorretos.")
            return RedirectResponse(
                f"/login?redirect={redirect}",
                status_code=status.HTTP_303_SEE_OTHER
            )

        # Cria a sessão com dados do usuário
        criar_sessao(request, {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email
        })

        informar_sucesso(request, f"Bem-vindo(a), {usuario.nome}!")
        return RedirectResponse(redirect, status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        # Extrai mensagem de erro do Pydantic
        erro = e.errors()[0]["msg"] if e.errors() else "Dados inválidos."
        informar_erro(request, erro)
        return RedirectResponse(
            f"/login?redirect={redirect}",
            status_code=status.HTTP_303_SEE_OTHER
        )


# =============================================================================
# CADASTRO
# =============================================================================

@router.get("/cadastrar", response_class=HTMLResponse)
async def get_cadastrar(request: Request):
    """
    Exibe a página de cadastro.

    Se já estiver logado, redireciona para home.
    """
    # Se já está logado, redireciona
    if obter_usuario_logado(request):
        return RedirectResponse("/home", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("cadastro.html", {
        "request": request,
        "mensagens": obter_mensagens(request)
    })


@router.post("/cadastrar")
async def post_cadastrar(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    confirmar_senha: str = Form(...)
):
    """
    Processa o cadastro de novo usuário.

    Form data:
        nome: Nome completo
        email: E-mail
        senha: Senha
        confirmar_senha: Confirmação da senha

    Fluxo:
    1. Valida os dados com o DTO
    2. Verifica se e-mail já existe
    3. Cria hash da senha
    4. Insere usuário no banco
    5. Cria sessão automaticamente (login automático)
    6. Redireciona para home
    """
    try:
        # Valida os dados com Pydantic
        dto = CadastroDTO(
            nome=nome,
            email=email,
            senha=senha,
            confirmar_senha=confirmar_senha
        )

        # Verifica se email já existe
        if usuario_repo.email_existe(dto.email):
            informar_erro(request, "Este e-mail já está cadastrado.")
            return RedirectResponse("/cadastrar", status_code=status.HTTP_303_SEE_OTHER)

        # Cria o hash da senha (NUNCA armazenar senha em texto plano!)
        senha_hash = criar_hash_senha(dto.senha)

        # Insere o usuário no banco
        usuario = usuario_repo.inserir(dto.nome, dto.email, senha_hash)

        # Cria a sessão automaticamente (login após cadastro)
        criar_sessao(request, {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email
        })

        informar_sucesso(request, "Cadastro realizado com sucesso!")
        return RedirectResponse("/home", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        # Extrai mensagem de erro do Pydantic
        erro = e.errors()[0]["msg"] if e.errors() else "Dados inválidos."
        informar_erro(request, erro)
        return RedirectResponse("/cadastrar", status_code=status.HTTP_303_SEE_OTHER)


# =============================================================================
# LOGOUT
# =============================================================================

@router.get("/logout")
async def logout(request: Request):
    """
    Encerra a sessão do usuário.

    Destrói a sessão e redireciona para login.
    """
    destruir_sessao(request)
    informar_sucesso(request, "Você saiu do sistema.")
    return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)