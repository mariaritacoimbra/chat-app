from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
import secrets

# Importa rotas
from routes import auth_routes, chat_routes

# Importa utilitários
from util.database import inicializar_banco
from util.auth_decorator import requer_autenticacao, obter_usuario_logado
from util.flash_messages import obter_mensagens


# =============================================================================
# LIFESPAN - EVENTOS DE INICIALIZAÇÃO E ENCERRAMENTO
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação.
    Código antes do yield executa na inicialização.
    Código depois do yield executa no encerramento.
    """
    # Inicialização
    inicializar_banco()
    print("=" * 50)
    print("  CHAT APP - Servidor iniciado!")
    print("  Acesse: http://localhost:8000")
    print("=" * 50)

    yield  # Aplicação em execução

    # Encerramento (se necessário)
    print("Servidor encerrado.")


# =============================================================================
# CONFIGURAÇÃO DA APLICAÇÃO
# =============================================================================

# Cria instância do FastAPI com metadados para documentação
app = FastAPI(
    title="Chat App",
    description="Aplicação de chat em tempo real com autenticação",
    version="1.0.0",
    lifespan=lifespan  # Usa o gerenciador de ciclo de vida
)

# Middleware de sessão para manter usuário logado
# IMPORTANTE: Deve ser adicionado ANTES das rotas
# Em produção, use variável de ambiente para secret_key
app.add_middleware(
    SessionMiddleware,
    secret_key=secrets.token_hex(32),  # Gera chave aleatória de 64 caracteres
    max_age=3600 * 24  # Sessão válida por 24 horas
)

# Monta diretório de arquivos estáticos (CSS, JS, imagens)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configura templates Jinja2
templates = Jinja2Templates(directory="templates")

# Registra routers de autenticação e chat
app.include_router(auth_routes.router)
app.include_router(chat_routes.router)


# =============================================================================
# ROTAS PRINCIPAIS
# =============================================================================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Rota raiz da aplicação.

    - Se usuário estiver logado: redireciona para /home
    - Se não estiver logado: exibe página de login
    """
    if obter_usuario_logado(request):
        from fastapi.responses import RedirectResponse
        return RedirectResponse("/home", status_code=303)

    return templates.TemplateResponse("login.html", {
        "request": request,
        "redirect": "/home",
        "mensagens": obter_mensagens(request)
    })


@app.get("/home", response_class=HTMLResponse)
@requer_autenticacao()
async def home(request: Request, usuario_logado: dict = None):
    """
    Página principal com widget de chat.

    Esta rota é protegida pelo decorator @requer_autenticacao().
    Se o usuário não estiver logado, será redirecionado para /login.

    Args:
        request: Objeto Request do FastAPI
        usuario_logado: Dicionário com dados do usuário (injetado pelo decorator)
    """
    return templates.TemplateResponse("home.html", {
        "request": request,
        "usuario_logado": usuario_logado,
        "mensagens": obter_mensagens(request)
    })


# =============================================================================
# EXECUÇÃO DO SERVIDOR
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    # Inicia servidor Uvicorn
    # - host="0.0.0.0": Aceita conexões de qualquer IP
    # - port=8000: Porta padrão
    # - reload=True: Reinicia automaticamente ao detectar mudanças (desenvolvimento)
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )