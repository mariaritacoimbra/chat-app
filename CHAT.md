# Aplicação de Chat com Autenticação Básica

**Guia Completo** | **Stack:** FastAPI + Jinja2 + SQLite + SSE

---

## Índice

1. [Visão Geral](#visão-geral)
2. [Setup Inicial do Projeto](#setup-inicial-do-projeto)
3. [Estrutura de Arquivos](#estrutura-de-arquivos)
4. [Dependências](#dependências)
5. [Configuração do Banco de Dados](#configuração-do-banco-de-dados)
6. [Sistema de Autenticação](#sistema-de-autenticação)
7. [Sistema de Chat](#sistema-de-chat)
8. [Frontend - Páginas](#frontend---páginas)
9. [Componente de Chat](#componente-de-chat)
10. [Arquivo Principal](#arquivo-principal)
11. [Executando a Aplicação](#executando-a-aplicação)

---

## Visão Geral

Este guia apresenta um passo a passo completo para criar uma aplicação web com:

- **Autenticação básica** (sem refresh tokens) usando sessões
- **Chat em tempo real** entre usuários logados usando Server-Sent Events (SSE)
- **4 páginas principais:** Login, Cadastro, Home (com widget de chat)
- **Componente de chat independente** e reutilizável

### Arquitetura

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │ ←── │   FastAPI   │ ←── │   SQLite    │
│  (Jinja2)   │     │   Backend   │     │  Database   │
└─────────────┘     └─────────────┘     └─────────────┘
       ↑                   │
       │                   │
       └───── SSE ─────────┘
        (Tempo Real)
```

---

## Setup Inicial do Projeto

Esta seção guia você na criação do projeto do zero, incluindo ambiente virtual, estrutura de pastas e integração com GitHub.

### 2.1 Criar Pasta do Projeto

1. Abra o **VS Code**
2. Vá em **File > Open Folder...**
3. Navegue até onde deseja criar o projeto
4. Clique em **New Folder** e crie uma pasta chamada `chat-app`
5. Selecione a pasta criada e clique em **Open**

### 2.2 Inicializar Repositório Git

1. Abra o terminal integrado: **Terminal > New Terminal** (ou `Ctrl+`` `)
2. Execute os comandos:

```bash
# Inicializa repositório Git
git init

# Configura usuário (se ainda não configurado globalmente)
git config user.name "Seu Nome"
git config user.email "seu.email@exemplo.com"
```

### 2.3 Criar Arquivo .gitignore

Crie o arquivo `.gitignore` na raiz do projeto com o seguinte conteúdo:

```gitignore
# Ambiente virtual Python
.venv/
venv/
env/

# Arquivos Python compilados
__pycache__/
*.py[cod]
*$py.class

# Banco de dados SQLite
*.db

# Variáveis de ambiente
.env

# IDE
.vscode/
.idea/

# Sistema operacional
.DS_Store
Thumbs.db
```

### 2.4 Criar Ambiente Virtual Python

No terminal integrado do VS Code:

```bash
# Cria o ambiente virtual
python -m venv .venv

# Ativa o ambiente virtual
# No macOS/Linux:
source .venv/bin/activate

# No Windows:
.venv\Scripts\activate
```

Após ativar, você verá `(.venv)` no início da linha do terminal.

### 2.5 Selecionar Interpretador Python no VS Code

1. Pressione `Ctrl+Shift+P` (ou `Cmd+Shift+P` no macOS)
2. Digite "Python: Select Interpreter"
3. Selecione o interpretador dentro da pasta `.venv`

### 2.6 Criar Estrutura de Diretórios

Execute no terminal:

```bash
mkdir -p model repo routes dtos util templates/components static/css static/js
```

### 2.7 Configurar VS Code para Debug (launch.json)

1. Crie a pasta `.vscode` na raiz do projeto:

```bash
mkdir .vscode
```

2. Crie o arquivo `.vscode/launch.json` com o conteúdo:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Chat App",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
            "console": "integratedTerminal",
            "cwd": "${workspaceFolder}"
        }
    ]
}
```

Agora você pode executar o projeto com:
- **F5**: Executa com debugger (breakpoints funcionam)
- **Ctrl+F5**: Executa sem debugger (mais rápido)

### 2.8 Criar Repositório no GitHub

0. Adicione esse arquivo **CHAT.md** à raiz do projeto e renomeie para **README.md**.

1. Clique no ícone/extensão **Source Control** na barra de ferramentas do VSCode.

2. Adicione a mensagem "versao inicial" no campo de texto do commit e clique no botão **Commit**.

3. Clique no botão **Publish Branch**, selecione **Public Repository** na caixa de seleção que se abrir, e mantenha o nome **chat-app**.

---

## Estrutura de Arquivos

```
chat-app/
├── .vscode/
│   └── launch.json                  # Configuração de debug
├── .gitignore                       # Arquivos ignorados pelo Git
├── main.py                          # Ponto de entrada da aplicação
├── requirements.txt                 # Dependências Python
├── database.db                      # Banco SQLite (criado automaticamente)
│
├── model/                           # Modelos de dados
│   ├── usuario_model.py
│   ├── chat_sala_model.py
│   ├── chat_mensagem_model.py
│   └── chat_participante_model.py
│
├── repo/                            # Camada de repositório (acesso a dados)
│   ├── usuario_repo.py
│   ├── chat_sala_repo.py
│   ├── chat_mensagem_repo.py
│   └── chat_participante_repo.py
│
├── routes/                          # Rotas da API
│   ├── auth_routes.py
│   └── chat_routes.py
│
├── dtos/                            # Data Transfer Objects (validação)
│   ├── auth_dto.py
│   └── chat_dto.py
│
├── util/                            # Utilitários
│   ├── database.py
│   ├── security.py
│   ├── auth_decorator.py
│   ├── chat_manager.py
│   └── flash_messages.py
│
├── templates/                       # Templates Jinja2
│   ├── base.html
│   ├── login.html
│   ├── cadastro.html
│   ├── home.html
│   └── components/
│       └── chat_widget.html
│
└── static/                          # Arquivos estáticos
    ├── css/
    │   └── chat-widget.css
    └── js/
        └── chat-widget.js
```

---

## Dependências

### requirements.txt

```txt
# Framework Web
fastapi==0.115.0
uvicorn[standard]==0.32.0

# Templates
jinja2==3.1.4

# Validação
pydantic==2.9.2
pydantic[email]==2.9.2

# Segurança
passlib[bcrypt]==1.7.4
bcrypt>=3.2.0,<4.0.0
python-multipart==0.0.12

# Sessões
itsdangerous==2.2.0
```

### Instalação

Com o ambiente virtual ativado, execute:

```bash
pip install -r requirements.txt
```

---

## Configuração do Banco de Dados

### util/database.py

```python
# =============================================================================
# CONFIGURAÇÃO DO BANCO DE DADOS SQLite
# =============================================================================
# Este módulo fornece funções para conexão e inicialização do banco de dados.
# Utiliza SQLite por simplicidade, mas pode ser adaptado para outros bancos.

import sqlite3
from contextlib import contextmanager

# Caminho do arquivo do banco de dados
DATABASE_PATH = "database.db"


@contextmanager
def get_connection():
    """
    Gerenciador de contexto para conexões SQLite.

    Uso:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tabela")

    - Abre conexão automaticamente
    - Configura row_factory para acessar colunas por nome
    - Faz commit automático ao sair do bloco
    - Faz rollback em caso de erro
    - Fecha conexão automaticamente
    """
    conn = sqlite3.connect(DATABASE_PATH)
    # Permite acessar colunas por nome (row["coluna"])
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def inicializar_banco():
    """
    Cria todas as tabelas necessárias para a aplicação.

    Tabelas criadas:
    - usuario: dados dos usuários
    - chat_sala: salas de chat entre dois usuários
    - chat_mensagem: mensagens enviadas nas salas
    - chat_participante: relacionamento usuário-sala
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        # Tabela de usuários
        # Armazena informações básicas do usuário
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuario (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Tabela de salas de chat
        # O ID da sala segue o padrão "menor_id_maior_id" para ser determinístico
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_sala (
                id TEXT PRIMARY KEY,
                criada_em TIMESTAMP NOT NULL,
                ultima_atividade TIMESTAMP NOT NULL
            )
        """)

        # Tabela de mensagens
        # Cada mensagem pertence a uma sala e foi enviada por um usuário
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_mensagem (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sala_id TEXT NOT NULL,
                usuario_id INTEGER NOT NULL,
                mensagem TEXT NOT NULL,
                data_envio TIMESTAMP NOT NULL,
                lida_em TIMESTAMP,
                FOREIGN KEY (sala_id) REFERENCES chat_sala(id) ON DELETE CASCADE,
                FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
            )
        """)

        # Tabela de participantes
        # Relaciona usuários às suas salas de chat
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_participante (
                sala_id TEXT NOT NULL,
                usuario_id INTEGER NOT NULL,
                ultima_leitura TIMESTAMP,
                PRIMARY KEY (sala_id, usuario_id),
                FOREIGN KEY (sala_id) REFERENCES chat_sala(id) ON DELETE CASCADE,
                FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
            )
        """)

        # Índices para melhorar performance das consultas mais frequentes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mensagem_sala ON chat_mensagem(sala_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mensagem_data ON chat_mensagem(data_envio)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_participante_usuario ON chat_participante(usuario_id)")
```

---

## Sistema de Autenticação

### 5.1 Model - Usuario

#### model/usuario_model.py

```python
# =============================================================================
# MODEL - USUÁRIO
# =============================================================================
# Representa um usuário do sistema usando dataclass para simplicidade.

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
```

### 5.2 Utilitários de Segurança

#### util/security.py

```python
# =============================================================================
# UTILITÁRIOS DE SEGURANÇA
# =============================================================================
# Este módulo fornece funções para hash e verificação de senhas usando bcrypt.
# Bcrypt é um algoritmo seguro que inclui salt automaticamente.

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
```

### 5.3 Decorator de Autenticação

#### util/auth_decorator.py

```python
# =============================================================================
# DECORATOR E FUNÇÕES DE AUTENTICAÇÃO
# =============================================================================
# Este módulo fornece funções para gerenciar sessões de usuário e um decorator
# para proteger rotas que exigem autenticação.

from fastapi import Request, status
from fastapi.responses import RedirectResponse
from functools import wraps
from typing import Optional


def criar_sessao(request: Request, usuario: dict):
    """
    Cria sessão de usuário após login bem-sucedido.

    Args:
        request: Objeto Request do FastAPI
        usuario: Dicionário com dados do usuário (id, nome, email)

    Exemplo:
        criar_sessao(request, {
            "id": 1,
            "nome": "João",
            "email": "joao@email.com"
        })
    """
    request.session["usuario_logado"] = usuario


def destruir_sessao(request: Request):
    """
    Destrói a sessão do usuário (logout).
    Remove todos os dados da sessão.

    Args:
        request: Objeto Request do FastAPI
    """
    request.session.clear()


def obter_usuario_logado(request: Request) -> Optional[dict]:
    """
    Obtém dados do usuário logado da sessão.

    Args:
        request: Objeto Request do FastAPI

    Returns:
        Dicionário com dados do usuário ou None se não estiver logado
    """
    return request.session.get("usuario_logado")


def esta_logado(request: Request) -> bool:
    """
    Verifica se há um usuário logado na sessão.

    Args:
        request: Objeto Request do FastAPI

    Returns:
        True se há usuário logado, False caso contrário
    """
    return "usuario_logado" in request.session


def requer_autenticacao():
    """
    Decorator para proteger rotas que exigem autenticação.

    Se o usuário não estiver logado, redireciona para /login.
    Se estiver logado, injeta o usuario_logado nos kwargs da função.

    Uso:
        @router.get("/pagina-protegida")
        @requer_autenticacao()
        async def pagina_protegida(request: Request, usuario_logado: dict = None):
            # usuario_logado é injetado automaticamente
            return {"usuario": usuario_logado["nome"]}
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Obtém o request dos argumentos
            request = kwargs.get('request') or args[0]

            # Verifica se está logado
            usuario = obter_usuario_logado(request)
            if not usuario:
                # Redireciona para login mantendo a URL original
                return RedirectResponse(
                    f"/login?redirect={request.url.path}",
                    status_code=status.HTTP_303_SEE_OTHER
                )

            # Injeta usuario_logado nos kwargs para uso na função
            kwargs['usuario_logado'] = usuario
            return await func(*args, **kwargs)

        return wrapper
    return decorator
```

### 5.4 Flash Messages

#### util/flash_messages.py

```python
# =============================================================================
# SISTEMA DE MENSAGENS FLASH
# =============================================================================
# Mensagens flash são mensagens temporárias exibidas uma única vez ao usuário.
# São úteis para feedback de ações como "Login realizado com sucesso!".

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
```

### 5.5 Repository - Usuario

#### repo/usuario_repo.py

```python
# =============================================================================
# REPOSITORY - USUÁRIO
# =============================================================================
# Camada de acesso a dados para a entidade Usuário.
# Contém todas as operações de banco de dados relacionadas a usuários.

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
```

### 5.6 DTOs de Autenticação

#### dtos/auth_dto.py

```python
# =============================================================================
# DTOs - AUTENTICAÇÃO
# =============================================================================
# Data Transfer Objects para validação de dados de login e cadastro.
# Usam Pydantic para validação automática com mensagens de erro claras.

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
```

### 5.7 Rotas de Autenticação

#### routes/auth_routes.py

```python
# =============================================================================
# ROTAS DE AUTENTICAÇÃO
# =============================================================================
# Este módulo contém as rotas de login, cadastro e logout.
# Usa sessões para manter o usuário autenticado.

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
```

---

## Sistema de Chat

### 6.1 Models do Chat

#### model/chat_sala_model.py

```python
# =============================================================================
# MODEL - SALA DE CHAT
# =============================================================================
# Representa uma sala de chat privada entre dois usuários.

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ChatSala:
    """
    Representa uma sala de chat privada entre dois usuários.

    O ID da sala segue o padrão: "menor_id_maior_id"
    Isso garante que dois usuários sempre tenham a mesma sala.

    Exemplo:
        Usuários com ID 3 e 7 sempre usam a sala "3_7"
        Usuários com ID 7 e 3 também usam a sala "3_7"

    Atributos:
        id: Identificador único da sala (formato "menor_id_maior_id")
        criada_em: Data/hora de criação da sala
        ultima_atividade: Data/hora da última mensagem enviada
    """
    id: str
    criada_em: datetime
    ultima_atividade: datetime
```

#### model/chat_mensagem_model.py

```python
# =============================================================================
# MODEL - MENSAGEM DE CHAT
# =============================================================================
# Representa uma mensagem enviada em uma sala de chat.

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ChatMensagem:
    """
    Representa uma mensagem enviada em uma sala de chat.

    Atributos:
        id: Identificador único da mensagem
        sala_id: ID da sala onde foi enviada
        usuario_id: ID do usuário que enviou
        mensagem: Conteúdo da mensagem
        data_envio: Data/hora do envio
        lida_em: Data/hora em que foi lida (None se não lida)
    """
    id: int
    sala_id: str
    usuario_id: int
    mensagem: str
    data_envio: datetime
    lida_em: Optional[datetime] = None
```

#### model/chat_participante_model.py

```python
# =============================================================================
# MODEL - PARTICIPANTE DE CHAT
# =============================================================================
# Representa a participação de um usuário em uma sala de chat.

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ChatParticipante:
    """
    Representa a participação de um usuário em uma sala.

    Esta entidade relaciona usuários às suas salas de chat.
    A chave primária é composta por (sala_id, usuario_id).

    Atributos:
        sala_id: ID da sala de chat
        usuario_id: ID do usuário participante
        ultima_leitura: Data/hora da última leitura das mensagens
    """
    sala_id: str
    usuario_id: int
    ultima_leitura: Optional[datetime] = None
```

### 6.2 Chat Manager (SSE)

#### util/chat_manager.py

```python
# =============================================================================
# GERENCIADOR DE CONEXÕES SSE PARA CHAT
# =============================================================================
# Este módulo gerencia as conexões Server-Sent Events (SSE) do chat.
# Cada usuário mantém UMA conexão que recebe mensagens de TODAS as suas salas.

import asyncio
from typing import Dict, Set


class ChatManager:
    """
    Gerencia conexões SSE para o sistema de chat em tempo real.

    Características:
    - Cada usuário tem uma única conexão SSE
    - Mensagens são entregues via asyncio.Queue
    - Suporta múltiplos usuários conectados simultaneamente
    """

    def __init__(self):
        # Dicionário: usuario_id -> Queue de mensagens
        self._connections: Dict[int, asyncio.Queue] = {}
        # Set de usuários atualmente conectados
        self._active_connections: Set[int] = set()

    async def connect(self, usuario_id: int) -> asyncio.Queue:
        """
        Registra nova conexão SSE para um usuário.

        Args:
            usuario_id: ID do usuário que está conectando

        Returns:
            asyncio.Queue onde as mensagens serão colocadas

        A Queue é usada pelo endpoint SSE para aguardar novas mensagens.
        """
        queue = asyncio.Queue()
        self._connections[usuario_id] = queue
        self._active_connections.add(usuario_id)
        print(f"[ChatManager] Usuário {usuario_id} conectado. Total: {len(self._active_connections)}")
        return queue

    async def disconnect(self, usuario_id: int):
        """
        Remove conexão SSE de um usuário.

        Args:
            usuario_id: ID do usuário que está desconectando
        """
        if usuario_id in self._connections:
            del self._connections[usuario_id]
        if usuario_id in self._active_connections:
            self._active_connections.remove(usuario_id)
        print(f"[ChatManager] Usuário {usuario_id} desconectado. Total: {len(self._active_connections)}")

    async def broadcast_para_sala(self, sala_id: str, mensagem_dict: dict):
        """
        Envia mensagem SSE para ambos os participantes de uma sala.

        Args:
            sala_id: ID da sala (formato "menor_id_maior_id")
            mensagem_dict: Dicionário com os dados da mensagem

        O sala_id tem formato "3_7", onde 3 e 7 são IDs dos usuários.
        A mensagem é enviada para ambos os participantes se estiverem conectados.
        """
        # Extrai IDs dos usuários do sala_id
        partes = sala_id.split("_")
        if len(partes) != 2:
            print(f"[ChatManager] sala_id inválido: {sala_id}")
            return

        usuario1_id = int(partes[0])
        usuario2_id = int(partes[1])

        # Envia para cada participante se estiver conectado
        for usuario_id in [usuario1_id, usuario2_id]:
            if usuario_id in self._connections:
                await self._connections[usuario_id].put(mensagem_dict)
                print(f"[ChatManager] Mensagem enviada para usuário {usuario_id}")

    def is_connected(self, usuario_id: int) -> bool:
        """
        Verifica se o usuário está conectado.

        Args:
            usuario_id: ID do usuário

        Returns:
            True se conectado, False caso contrário
        """
        return usuario_id in self._active_connections


# Instância singleton global
# Usada por toda a aplicação para gerenciar conexões
chat_manager = ChatManager()
```

### 6.3 Repositories do Chat

#### repo/chat_sala_repo.py

```python
# =============================================================================
# REPOSITORY - SALA DE CHAT
# =============================================================================
# Camada de acesso a dados para a entidade ChatSala.
# Gerencia operações de criação e consulta de salas de chat.

from datetime import datetime
from typing import Optional
from model.chat_sala_model import ChatSala
from util.database import get_connection


def gerar_sala_id(usuario1_id: int, usuario2_id: int) -> str:
    """
    Gera ID único e determinístico para sala entre dois usuários.

    O ID é gerado ordenando os IDs dos usuários, garantindo que
    dois usuários sempre tenham o mesmo ID de sala.

    Args:
        usuario1_id: ID do primeiro usuário
        usuario2_id: ID do segundo usuário

    Returns:
        ID da sala no formato "menor_id_maior_id"

    Exemplos:
        >>> gerar_sala_id(3, 7)
        '3_7'
        >>> gerar_sala_id(7, 3)
        '3_7'
    """
    ids_ordenados = sorted([usuario1_id, usuario2_id])
    return f"{ids_ordenados[0]}_{ids_ordenados[1]}"


def obter_por_id(sala_id: str) -> Optional[ChatSala]:
    """
    Busca uma sala pelo ID.

    Args:
        sala_id: ID da sala

    Returns:
        Objeto ChatSala se encontrado, None caso contrário
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chat_sala WHERE id = ?", (sala_id,))
        row = cursor.fetchone()
        if row:
            return ChatSala(
                id=row["id"],
                criada_em=row["criada_em"],
                ultima_atividade=row["ultima_atividade"]
            )
    return None


def criar_ou_obter_sala(usuario1_id: int, usuario2_id: int) -> ChatSala:
    """
    Cria uma nova sala ou retorna sala existente entre dois usuários.

    Esta função é idempotente - chamar múltiplas vezes retorna a mesma sala.
    Também cria os registros de participantes automaticamente.

    Args:
        usuario1_id: ID do primeiro usuário
        usuario2_id: ID do segundo usuário

    Returns:
        Objeto ChatSala (existente ou recém-criado)
    """
    sala_id = gerar_sala_id(usuario1_id, usuario2_id)

    # Verifica se já existe
    sala_existente = obter_por_id(sala_id)
    if sala_existente:
        return sala_existente

    # Cria nova sala
    agora = datetime.now()
    with get_connection() as conn:
        cursor = conn.cursor()

        # Insere a sala
        cursor.execute(
            "INSERT INTO chat_sala (id, criada_em, ultima_atividade) VALUES (?, ?, ?)",
            (sala_id, agora, agora)
        )

        # Insere os participantes
        cursor.execute(
            "INSERT INTO chat_participante (sala_id, usuario_id) VALUES (?, ?)",
            (sala_id, usuario1_id)
        )
        cursor.execute(
            "INSERT INTO chat_participante (sala_id, usuario_id) VALUES (?, ?)",
            (sala_id, usuario2_id)
        )

    return ChatSala(id=sala_id, criada_em=agora, ultima_atividade=agora)


def atualizar_ultima_atividade(sala_id: str):
    """
    Atualiza o timestamp de última atividade da sala.

    Chamado sempre que uma nova mensagem é enviada na sala.

    Args:
        sala_id: ID da sala
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE chat_sala SET ultima_atividade = ? WHERE id = ?",
            (datetime.now(), sala_id)
        )
```

#### repo/chat_mensagem_repo.py

```python
# =============================================================================
# REPOSITORY - MENSAGEM DE CHAT
# =============================================================================
# Camada de acesso a dados para a entidade ChatMensagem.
# Gerencia operações de envio, listagem e marcação de mensagens.

from datetime import datetime
from typing import Optional
from model.chat_mensagem_model import ChatMensagem
from util.database import get_connection


def inserir(sala_id: str, usuario_id: int, mensagem: str) -> ChatMensagem:
    """
    Insere uma nova mensagem em uma sala.

    Args:
        sala_id: ID da sala
        usuario_id: ID do usuário que está enviando
        mensagem: Conteúdo da mensagem

    Returns:
        Objeto ChatMensagem com os dados da mensagem criada
    """
    data_envio = datetime.now()
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_mensagem (sala_id, usuario_id, mensagem, data_envio) VALUES (?, ?, ?, ?)",
            (sala_id, usuario_id, mensagem, data_envio)
        )
        mensagem_id = cursor.lastrowid

    return ChatMensagem(
        id=mensagem_id,
        sala_id=sala_id,
        usuario_id=usuario_id,
        mensagem=mensagem,
        data_envio=data_envio,
        lida_em=None
    )


def listar_por_sala(sala_id: str, limite: int = 50, offset: int = 0) -> list[ChatMensagem]:
    """
    Lista mensagens de uma sala, ordenadas por data (mais recentes primeiro).

    Args:
        sala_id: ID da sala
        limite: Número máximo de mensagens a retornar
        offset: Número de mensagens a pular (para paginação)

    Returns:
        Lista de objetos ChatMensagem

    Nota: As mensagens vêm em ordem DESC (mais recentes primeiro).
    O frontend deve inverter se quiser exibir em ordem cronológica.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM chat_mensagem
            WHERE sala_id = ?
            ORDER BY data_envio DESC
            LIMIT ? OFFSET ?
        """, (sala_id, limite, offset))

        return [
            ChatMensagem(
                id=row["id"],
                sala_id=row["sala_id"],
                usuario_id=row["usuario_id"],
                mensagem=row["mensagem"],
                data_envio=row["data_envio"],
                lida_em=row["lida_em"]
            )
            for row in cursor.fetchall()
        ]


def marcar_como_lidas(sala_id: str, usuario_id: int) -> bool:
    """
    Marca como lidas todas as mensagens não lidas de outros usuários em uma sala.

    Args:
        sala_id: ID da sala
        usuario_id: ID do usuário que está lendo (marca mensagens de OUTROS)

    Returns:
        True se alguma mensagem foi marcada, False caso contrário

    Nota: Marca apenas mensagens enviadas por OUTROS usuários.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE chat_mensagem
            SET lida_em = ?
            WHERE sala_id = ? AND usuario_id != ? AND lida_em IS NULL
        """, (datetime.now(), sala_id, usuario_id))
        return cursor.rowcount > 0


def contar_nao_lidas_por_usuario(usuario_id: int) -> int:
    """
    Conta total de mensagens não lidas para um usuário em todas as suas salas.

    Args:
        usuario_id: ID do usuário

    Returns:
        Número total de mensagens não lidas

    Usado para exibir o badge no botão do chat.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM chat_mensagem cm
            INNER JOIN chat_participante cp ON cm.sala_id = cp.sala_id
            WHERE cp.usuario_id = ? AND cm.usuario_id != ? AND cm.lida_em IS NULL
        """, (usuario_id, usuario_id))
        return cursor.fetchone()[0]


def contar_nao_lidas_por_sala(sala_id: str, usuario_id: int) -> int:
    """
    Conta mensagens não lidas em uma sala específica para um usuário.

    Args:
        sala_id: ID da sala
        usuario_id: ID do usuário

    Returns:
        Número de mensagens não lidas na sala

    Usado para exibir o badge em cada conversa na lista.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM chat_mensagem
            WHERE sala_id = ? AND usuario_id != ? AND lida_em IS NULL
        """, (sala_id, usuario_id))
        return cursor.fetchone()[0]
```

#### repo/chat_participante_repo.py

```python
# =============================================================================
# REPOSITORY - PARTICIPANTE DE CHAT
# =============================================================================
# Camada de acesso a dados para a entidade ChatParticipante.
# Gerencia operações de verificação de participação e listagem de conversas.

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
```

### 6.4 DTOs do Chat

#### dtos/chat_dto.py

```python
# =============================================================================
# DTOs - CHAT
# =============================================================================
# Data Transfer Objects para validação de dados do sistema de chat.
# Usam Pydantic para validação automática com mensagens de erro claras.

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
```

### 6.5 Rotas do Chat

#### routes/chat_routes.py

```python
# =============================================================================
# ROTAS DO CHAT
# =============================================================================
# Este módulo contém todas as rotas da API de chat:
# - SSE para mensagens em tempo real
# - CRUD de salas e mensagens
# - Busca de usuários
# - Contadores de não lidas

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
```

---

## Frontend - Páginas

### 7.1 Template Base

#### templates/base.html

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Título dinâmico via Jinja2 -->
    <title>{% block titulo %}Minha Aplicação{% endblock %}</title>

    <!-- Bootstrap 5 CSS - Framework CSS para estilização rápida -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons - Biblioteca de ícones -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.1/font/bootstrap-icons.css" rel="stylesheet">

    <!-- Bloco para CSS adicional específico de cada página -->
    {% block head_extra %}{% endblock %}
</head>
<body {% block body_attrs %}{% endblock %}>

    <!-- Bloco principal de conteúdo -->
    {% block content %}{% endblock %}

    <!-- Bootstrap 5 JS Bundle (inclui Popper.js) -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>

    <!-- Bloco para scripts adicionais específicos de cada página -->
    {% block scripts %}{% endblock %}
</body>
</html>
```

### 7.2 Página de Login

#### templates/login.html

```html
{% extends "base.html" %}

{% block titulo %}Login{% endblock %}

{% block content %}
<div class="container">
    <!-- Centraliza o card vertical e horizontalmente -->
    <div class="row justify-content-center min-vh-100 align-items-center">
        <div class="col-12 col-sm-8 col-md-6 col-lg-4">

            <div class="card shadow">
                <div class="card-body p-4">
                    <h3 class="card-title text-center mb-4">
                        <i class="bi bi-box-arrow-in-right"></i> Login
                    </h3>

                    <!-- Mensagens Flash - Exibe feedback de ações -->
                    {% for msg in mensagens %}
                    <div class="alert alert-{{ msg.tipo }} alert-dismissible fade show" role="alert">
                        {{ msg.texto }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                    {% endfor %}

                    <!-- Formulário de Login -->
                    <form method="POST" action="/login">
                        <!-- Campo oculto com URL de redirecionamento -->
                        <input type="hidden" name="redirect" value="{{ redirect }}">

                        <div class="mb-3">
                            <label for="email" class="form-label">E-mail</label>
                            <input
                                type="email"
                                class="form-control"
                                id="email"
                                name="email"
                                required
                                autofocus
                            >
                        </div>

                        <div class="mb-3">
                            <label for="senha" class="form-label">Senha</label>
                            <input
                                type="password"
                                class="form-control"
                                id="senha"
                                name="senha"
                                required
                                minlength="6"
                            >
                        </div>

                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary">
                                <i class="bi bi-box-arrow-in-right"></i> Entrar
                            </button>
                        </div>
                    </form>
                </div>

                <!-- Link para cadastro -->
                <div class="card-footer text-center">
                    <small>
                        Não tem conta?
                        <a href="/cadastrar" class="text-decoration-none">Cadastre-se</a>
                    </small>
                </div>
            </div>

        </div>
    </div>
</div>
{% endblock %}
```

### 7.3 Página de Cadastro

#### templates/cadastro.html

```html
{% extends "base.html" %}

{% block titulo %}Cadastro{% endblock %}

{% block content %}
<div class="container">
    <!-- Centraliza o card vertical e horizontalmente -->
    <div class="row justify-content-center min-vh-100 align-items-center">
        <div class="col-12 col-sm-8 col-md-6 col-lg-4">

            <div class="card shadow">
                <div class="card-body p-4">
                    <h3 class="card-title text-center mb-4">
                        <i class="bi bi-person-plus"></i> Cadastro
                    </h3>

                    <!-- Mensagens Flash - Exibe feedback de ações -->
                    {% for msg in mensagens %}
                    <div class="alert alert-{{ msg.tipo }} alert-dismissible fade show" role="alert">
                        {{ msg.texto }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                    {% endfor %}

                    <!-- Formulário de Cadastro -->
                    <form method="POST" action="/cadastrar">

                        <div class="mb-3">
                            <label for="nome" class="form-label">Nome Completo</label>
                            <input
                                type="text"
                                class="form-control"
                                id="nome"
                                name="nome"
                                required
                                autofocus
                                minlength="3"
                                maxlength="100"
                            >
                        </div>

                        <div class="mb-3">
                            <label for="email" class="form-label">E-mail</label>
                            <input
                                type="email"
                                class="form-control"
                                id="email"
                                name="email"
                                required
                            >
                        </div>

                        <div class="mb-3">
                            <label for="senha" class="form-label">Senha</label>
                            <input
                                type="password"
                                class="form-control"
                                id="senha"
                                name="senha"
                                required
                                minlength="6"
                            >
                            <div class="form-text">Mínimo de 6 caracteres</div>
                        </div>

                        <div class="mb-3">
                            <label for="confirmar_senha" class="form-label">Confirmar Senha</label>
                            <input
                                type="password"
                                class="form-control"
                                id="confirmar_senha"
                                name="confirmar_senha"
                                required
                                minlength="6"
                            >
                        </div>

                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary">
                                <i class="bi bi-person-plus"></i> Cadastrar
                            </button>
                        </div>
                    </form>
                </div>

                <!-- Link para login -->
                <div class="card-footer text-center">
                    <small>
                        Já tem conta?
                        <a href="/login" class="text-decoration-none">Faça login</a>
                    </small>
                </div>
            </div>

        </div>
    </div>
</div>
{% endblock %}
```

### 7.4 Página Home

#### templates/home.html

```html
{% extends "base.html" %}

{% block titulo %}Home{% endblock %}

{% block head_extra %}
<!-- CSS do Widget de Chat -->
<link rel="stylesheet" href="/static/css/chat-widget.css">
{% endblock %}

<!-- Passa o ID do usuário para o JavaScript via data attribute -->
{% block body_attrs %}data-usuario-id="{{ usuario_logado.id }}"{% endblock %}

{% block content %}
<!-- Navbar com nome do usuário e link de logout -->
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
        <a class="navbar-brand" href="/home">
            <i class="bi bi-chat-dots"></i> Chat App
        </a>

        <div class="navbar-nav ms-auto">
            <span class="navbar-text me-3">
                <i class="bi bi-person-circle"></i> {{ usuario_logado.nome }}
            </span>
            <a class="nav-link text-light" href="/logout">
                <i class="bi bi-box-arrow-right"></i> Sair
            </a>
        </div>
    </div>
</nav>

<div class="container mt-5">
    <div class="row">
        <div class="col-12">
            <!-- Mensagens Flash -->
            {% for msg in mensagens %}
            <div class="alert alert-{{ msg.tipo }} alert-dismissible fade show" role="alert">
                {{ msg.texto }}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
            {% endfor %}

            <!-- Card de boas-vindas -->
            <div class="card">
                <div class="card-body text-center py-5">
                    <h2 class="mb-3">Bem-vindo(a), {{ usuario_logado.nome }}!</h2>
                    <p class="text-muted mb-4">
                        Use o widget de chat no canto inferior direito para conversar com outros usuários.
                    </p>
                    <p>
                        <i class="bi bi-arrow-down-right display-4 text-primary"></i>
                    </p>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Inclui o Widget de Chat -->
{% include "components/chat_widget.html" %}
{% endblock %}

{% block scripts %}
<!-- JavaScript do Widget de Chat -->
<script src="/static/js/chat-widget.js"></script>
<script>
    // Inicializa o widget quando o DOM estiver pronto
    document.addEventListener('DOMContentLoaded', function() {
        chatWidget.init();
    });
</script>
{% endblock %}
```

---

## Componente de Chat

O componente de chat é independente e pode ser reutilizado em qualquer página. Ele consiste em três partes: HTML, CSS e JavaScript.

### 8.1 HTML do Widget

#### templates/components/chat_widget.html

```html
<!-- =============================================================================
     WIDGET DE CHAT - COMPONENTE INDEPENDENTE
     =============================================================================
     Este componente pode ser incluído em qualquer página.
     Requer: chat-widget.css e chat-widget.js
-->

<!-- Widget de Chat - Botão Flutuante -->
<button id="chat-toggle-btn" class="chat-toggle-btn" type="button">
    <i class="bi bi-chat-dots-fill"></i>
    <!-- Badge de mensagens não lidas -->
    <span id="chat-badge" class="chat-badge d-none">0</span>
</button>

<!-- Widget de Chat - Painel Principal -->
<div id="chat-panel" class="chat-panel d-none">

    <!-- Header do Chat -->
    <div class="chat-header">
        <div class="d-flex align-items-center justify-content-between">
            <h6 class="mb-0">
                <i class="bi bi-chat-dots"></i> Chat
            </h6>
            <button id="chat-close-btn" class="btn btn-sm btn-link text-white p-0">
                <i class="bi bi-x-lg"></i>
            </button>
        </div>

        <!-- Busca de Usuários -->
        <div class="mt-2">
            <div class="position-relative">
                <input
                    type="text"
                    id="chat-search-input"
                    class="form-control form-control-sm"
                    placeholder="Buscar usuário..."
                    autocomplete="off"
                >
                <!-- Resultados da busca aparecem aqui -->
                <div id="chat-search-results" class="chat-search-results d-none"></div>
            </div>
        </div>
    </div>

    <!-- Corpo do Chat -->
    <div class="chat-body">

        <!-- Lista de Conversas (visível quando não há conversa aberta) -->
        <div id="chat-conversas-container" class="chat-conversas-container">
            <div id="chat-conversas-list" class="chat-conversas-list">
                <!-- Conversas serão carregadas via JavaScript -->
            </div>
            <!-- Mensagem quando não há conversas -->
            <div id="chat-conversas-empty" class="text-center text-muted py-4 d-none">
                <i class="bi bi-chat-square-text display-6"></i>
                <p class="mt-2 small">Nenhuma conversa</p>
            </div>
        </div>

        <!-- Área de Mensagens (visível quando há conversa aberta) -->
        <div id="chat-mensagens-container" class="chat-mensagens-container d-none">

            <!-- Header da Conversa com nome do usuário -->
            <div class="chat-conversa-header">
                <button id="chat-voltar-btn" class="btn btn-sm btn-link p-0 me-2">
                    <i class="bi bi-arrow-left"></i>
                </button>
                <span id="chat-conversa-nome">Nome do Usuário</span>
            </div>

            <!-- Lista de Mensagens -->
            <div id="chat-mensagens-list" class="chat-mensagens-list">
                <!-- Mensagens serão carregadas via JavaScript -->
            </div>

            <!-- Formulário para enviar mensagem -->
            <form id="chat-message-form" class="chat-message-form">
                <div class="input-group">
                    <input
                        type="text"
                        id="chat-message-input"
                        class="form-control form-control-sm"
                        placeholder="Digite sua mensagem..."
                        autocomplete="off"
                        maxlength="5000"
                    >
                    <button type="submit" class="btn btn-primary btn-sm">
                        <i class="bi bi-send"></i>
                    </button>
                </div>
            </form>
        </div>

    </div>
</div>
```

### 8.2 CSS do Widget

#### static/css/chat-widget.css

```css
/* =============================================================================
   CHAT WIDGET - ESTILOS CSS
   =============================================================================
   Estilos para o componente de chat flutuante.
   Usa variáveis CSS para fácil customização.
*/

/* =============================================================================
   VARIÁVEIS CSS
   ============================================================================= */

:root {
    /* Cores principais */
    --chat-primary: #0d6efd;
    --chat-primary-dark: #0b5ed7;
    --chat-bg: #ffffff;
    --chat-border: #dee2e6;
    --chat-header-bg: #0d6efd;
    --chat-header-text: #ffffff;
    --chat-hover: #f8f9fa;

    /* Cores das mensagens */
    --chat-message-sent: #0d6efd;
    --chat-message-sent-text: #ffffff;
    --chat-message-received: #e9ecef;
    --chat-message-received-text: #212529;
}

/* =============================================================================
   BOTÃO FLUTUANTE
   =============================================================================
   Botão circular fixo no canto inferior direito que abre/fecha o chat.
*/

.chat-toggle-btn {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background-color: var(--chat-primary);
    color: white;
    border: none;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    cursor: pointer;
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    transition: all 0.2s ease;
}

.chat-toggle-btn:hover {
    background-color: var(--chat-primary-dark);
    transform: scale(1.05);
}

/* Badge de notificação */
.chat-badge {
    position: absolute;
    top: -5px;
    right: -5px;
    background-color: #dc3545;
    color: white;
    border-radius: 50%;
    padding: 2px 6px;
    font-size: 0.7rem;
    min-width: 20px;
    text-align: center;
}

/* =============================================================================
   PAINEL PRINCIPAL
   =============================================================================
   Container principal do chat que aparece acima do botão.
*/

.chat-panel {
    position: fixed;
    bottom: 90px;
    right: 20px;
    width: 380px;
    height: 500px;
    background-color: var(--chat-bg);
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    z-index: 1001;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

/* Responsividade para mobile */
@media (max-width: 576px) {
    .chat-panel {
        width: calc(100% - 20px);
        right: 10px;
        bottom: 80px;
        height: 60vh;
    }
}

/* =============================================================================
   HEADER DO CHAT
   ============================================================================= */

.chat-header {
    background-color: var(--chat-header-bg);
    color: var(--chat-header-text);
    padding: 12px;
    flex-shrink: 0;
}

.chat-header .form-control {
    background-color: rgba(255, 255, 255, 0.9);
    border: none;
}

/* =============================================================================
   BUSCA DE USUÁRIOS
   =============================================================================
   Dropdown com resultados da busca de usuários.
*/

.chat-search-results {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background-color: var(--chat-bg);
    border: 1px solid var(--chat-border);
    border-radius: 4px;
    max-height: 200px;
    overflow-y: auto;
    z-index: 1002;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.chat-search-item {
    padding: 8px 12px;
    cursor: pointer;
    border-bottom: 1px solid var(--chat-border);
}

.chat-search-item:last-child {
    border-bottom: none;
}

.chat-search-item:hover {
    background-color: var(--chat-hover);
}

.chat-search-item-nome {
    font-weight: 500;
    font-size: 0.9rem;
}

.chat-search-item-email {
    font-size: 0.75rem;
    color: #6c757d;
}

/* =============================================================================
   CORPO DO CHAT
   ============================================================================= */

.chat-body {
    flex: 1;
    display: flex;
    overflow: hidden;
}

/* =============================================================================
   LISTA DE CONVERSAS
   =============================================================================
   Lista de conversas ativas do usuário.
*/

.chat-conversas-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.chat-conversas-list {
    flex: 1;
    overflow-y: auto;
}

/* Item de conversa na lista */
.chat-conversa-item {
    padding: 12px;
    border-bottom: 1px solid var(--chat-border);
    cursor: pointer;
    transition: background-color 0.15s ease;
}

.chat-conversa-item:hover {
    background-color: var(--chat-hover);
}

.chat-conversa-item.active {
    background-color: #e7f1ff;
}

.chat-conversa-nome {
    font-weight: 500;
    font-size: 0.9rem;
    margin-bottom: 2px;
}

.chat-conversa-preview {
    font-size: 0.8rem;
    color: #6c757d;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Badge de não lidas na conversa */
.chat-conversa-badge {
    background-color: var(--chat-primary);
    color: white;
    border-radius: 50%;
    padding: 2px 6px;
    font-size: 0.7rem;
    min-width: 20px;
    text-align: center;
}

/* =============================================================================
   ÁREA DE MENSAGENS
   =============================================================================
   Container onde as mensagens são exibidas.
*/

.chat-mensagens-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}

.chat-conversa-header {
    padding: 8px 12px;
    border-bottom: 1px solid var(--chat-border);
    background-color: var(--chat-hover);
    font-weight: 500;
    font-size: 0.9rem;
    flex-shrink: 0;
}

.chat-mensagens-list {
    flex: 1;
    overflow-y: auto;
    padding: 12px;
    display: flex;
    flex-direction: column;
    gap: 8px;
}

/* =============================================================================
   MENSAGENS
   =============================================================================
   Estilo dos balões de mensagem.
*/

.chat-mensagem {
    max-width: 80%;
    padding: 8px 12px;
    border-radius: 12px;
    word-wrap: break-word;
}

/* Mensagem enviada (pelo usuário atual) */
.chat-mensagem-enviada {
    background-color: var(--chat-message-sent);
    color: var(--chat-message-sent-text);
    align-self: flex-end;
    border-bottom-right-radius: 4px;
}

/* Mensagem recebida (de outro usuário) */
.chat-mensagem-recebida {
    background-color: var(--chat-message-received);
    color: var(--chat-message-received-text);
    align-self: flex-start;
    border-bottom-left-radius: 4px;
}

.chat-mensagem-texto {
    font-size: 0.875rem;
    line-height: 1.4;
}

.chat-mensagem-hora {
    font-size: 0.65rem;
    opacity: 0.7;
    text-align: right;
    margin-top: 4px;
}

/* =============================================================================
   FORMULÁRIO DE MENSAGEM
   ============================================================================= */

.chat-message-form {
    padding: 8px;
    border-top: 1px solid var(--chat-border);
    flex-shrink: 0;
}

/* =============================================================================
   SCROLLBAR CUSTOMIZADA
   =============================================================================
   Estilo mais discreto para barras de rolagem.
*/

.chat-conversas-list::-webkit-scrollbar,
.chat-mensagens-list::-webkit-scrollbar,
.chat-search-results::-webkit-scrollbar {
    width: 6px;
}

.chat-conversas-list::-webkit-scrollbar-track,
.chat-mensagens-list::-webkit-scrollbar-track,
.chat-search-results::-webkit-scrollbar-track {
    background: transparent;
}

.chat-conversas-list::-webkit-scrollbar-thumb,
.chat-mensagens-list::-webkit-scrollbar-thumb,
.chat-search-results::-webkit-scrollbar-thumb {
    background-color: #c1c1c1;
    border-radius: 3px;
}
```

### 8.3 JavaScript do Widget

#### static/js/chat-widget.js

```javascript
/**
 * =============================================================================
 * WIDGET DE CHAT - COMPONENTE INDEPENDENTE
 * =============================================================================
 * Implementa chat em tempo real usando Server-Sent Events (SSE).
 * Pode ser reutilizado em qualquer página que inclua o HTML e CSS necessários.
 *
 * Uso:
 *   1. Inclua chat-widget.css e chat-widget.js na página
 *   2. Inclua o HTML do widget (chat_widget.html)
 *   3. Chame chatWidget.init() após o DOM carregar
 */

const chatWidget = (() => {
    // ==========================================================================
    // ESTADO DA APLICAÇÃO
    // ==========================================================================

    let eventSource = null;      // Conexão SSE
    let conversaAtual = null;    // Conversa aberta atualmente
    let usuarioId = null;        // ID do usuário logado
    let mensagensOffset = 0;     // Offset para paginação de mensagens
    let conversasOffset = 0;     // Offset para paginação de conversas
    let buscaTimeout = null;     // Timeout para debounce da busca

    // Cache de elementos DOM para performance
    const elementos = {};

    // ==========================================================================
    // INICIALIZAÇÃO
    // ==========================================================================

    /**
     * Inicializa o widget de chat.
     * Deve ser chamado após o DOM estar carregado.
     */
    function init() {
        // Obtém ID do usuário do atributo data no body
        usuarioId = parseInt(document.body.dataset.usuarioId);
        if (!usuarioId) {
            console.error('[Chat] ID do usuário não encontrado');
            return;
        }

        // Cacheia referências aos elementos DOM
        cacheElementos();

        // Estabelece conexão SSE para mensagens em tempo real
        conectarSSE();

        // Carrega lista inicial de conversas
        carregarConversas(0);

        // Atualiza badge de mensagens não lidas
        atualizarContadorNaoLidas();

        // Configura todos os event listeners
        configurarEventListeners();

        console.log('[Chat] Widget inicializado para usuário', usuarioId);
    }

    /**
     * Cacheia referências aos elementos DOM para evitar buscas repetidas.
     */
    function cacheElementos() {
        elementos.toggleBtn = document.getElementById('chat-toggle-btn');
        elementos.panel = document.getElementById('chat-panel');
        elementos.closeBtn = document.getElementById('chat-close-btn');
        elementos.badge = document.getElementById('chat-badge');
        elementos.searchInput = document.getElementById('chat-search-input');
        elementos.searchResults = document.getElementById('chat-search-results');
        elementos.conversasContainer = document.getElementById('chat-conversas-container');
        elementos.conversasList = document.getElementById('chat-conversas-list');
        elementos.conversasEmpty = document.getElementById('chat-conversas-empty');
        elementos.mensagensContainer = document.getElementById('chat-mensagens-container');
        elementos.mensagensList = document.getElementById('chat-mensagens-list');
        elementos.conversaNome = document.getElementById('chat-conversa-nome');
        elementos.voltarBtn = document.getElementById('chat-voltar-btn');
        elementos.messageForm = document.getElementById('chat-message-form');
        elementos.messageInput = document.getElementById('chat-message-input');
    }

    /**
     * Configura todos os event listeners do widget.
     */
    function configurarEventListeners() {
        // Toggle do painel de chat
        elementos.toggleBtn.addEventListener('click', togglePanel);
        elementos.closeBtn.addEventListener('click', fecharPanel);

        // Busca de usuários com debounce
        elementos.searchInput.addEventListener('input', onSearchInput);
        elementos.searchInput.addEventListener('blur', () => {
            // Delay para permitir clique no resultado
            setTimeout(() => elementos.searchResults.classList.add('d-none'), 200);
        });

        // Voltar para lista de conversas
        elementos.voltarBtn.addEventListener('click', voltarParaConversas);

        // Envio de mensagem
        elementos.messageForm.addEventListener('submit', enviarMensagem);

        // Scroll infinito para carregar mais mensagens
        elementos.mensagensList.addEventListener('scroll', onMensagensScroll);
    }

    // ==========================================================================
    // SSE - SERVER-SENT EVENTS
    // ==========================================================================

    /**
     * Estabelece conexão SSE para receber mensagens em tempo real.
     * O EventSource reconecta automaticamente em caso de erro.
     */
    function conectarSSE() {
        eventSource = new EventSource('/chat/stream');

        // Recebe nova mensagem
        eventSource.onmessage = (event) => {
            const mensagem = JSON.parse(event.data);
            processarMensagemSSE(mensagem);
        };

        // Erro na conexão (EventSource reconecta automaticamente)
        eventSource.onerror = (error) => {
            console.error('[Chat SSE] Erro na conexão:', error);
        };

        // Conexão estabelecida
        eventSource.onopen = () => {
            console.log('[Chat SSE] Conexão estabelecida');
        };
    }

    /**
     * Processa mensagem recebida via SSE.
     * @param {Object} evento - Evento SSE com tipo e dados
     */
    function processarMensagemSSE(evento) {
        if (evento.tipo === 'nova_mensagem') {
            const mensagem = evento.mensagem;

            // Se estamos visualizando a conversa dessa mensagem
            if (conversaAtual && evento.sala_id === conversaAtual.sala_id) {
                // Adiciona mensagem na tela
                renderizarMensagem(mensagem, false);
                scrollParaFim();

                // Se é mensagem de outro usuário, marca como lida
                if (mensagem.usuario_id !== usuarioId) {
                    marcarMensagensComoLidas(evento.sala_id);
                }
            }

            // Atualiza lista de conversas (nova mensagem aparece no topo)
            carregarConversas(0);

            // Atualiza contador global de não lidas
            atualizarContadorNaoLidas();
        }
    }

    // ==========================================================================
    // PAINEL
    // ==========================================================================

    /**
     * Toggle (abre/fecha) o painel de chat.
     */
    function togglePanel() {
        elementos.panel.classList.toggle('d-none');
    }

    /**
     * Fecha o painel de chat.
     */
    function fecharPanel() {
        elementos.panel.classList.add('d-none');
    }

    // ==========================================================================
    // BUSCA DE USUÁRIOS
    // ==========================================================================

    /**
     * Handler para input de busca com debounce.
     * @param {Event} event - Evento de input
     */
    function onSearchInput(event) {
        const termo = event.target.value.trim();

        // Cancela busca anterior se existir
        if (buscaTimeout) {
            clearTimeout(buscaTimeout);
        }

        // Mínimo de 2 caracteres para buscar
        if (termo.length < 2) {
            elementos.searchResults.classList.add('d-none');
            return;
        }

        // Debounce de 300ms para não fazer muitas requisições
        buscaTimeout = setTimeout(() => buscarUsuarios(termo), 300);
    }

    /**
     * Busca usuários no servidor.
     * @param {string} termo - Termo de busca
     */
    async function buscarUsuarios(termo) {
        try {
            const response = await fetch(`/chat/usuarios/buscar?q=${encodeURIComponent(termo)}`);
            const data = await response.json();

            if (data.usuarios && data.usuarios.length > 0) {
                renderizarResultadosBusca(data.usuarios);
                elementos.searchResults.classList.remove('d-none');
            } else {
                elementos.searchResults.innerHTML = '<div class="p-2 text-muted small">Nenhum usuário encontrado</div>';
                elementos.searchResults.classList.remove('d-none');
            }
        } catch (error) {
            console.error('[Chat] Erro ao buscar usuários:', error);
        }
    }

    /**
     * Renderiza resultados da busca de usuários.
     * @param {Array} usuarios - Lista de usuários encontrados
     */
    function renderizarResultadosBusca(usuarios) {
        elementos.searchResults.innerHTML = usuarios.map(usuario => `
            <div class="chat-search-item" data-usuario-id="${usuario.id}">
                <div class="chat-search-item-nome">${escapeHtml(usuario.nome)}</div>
                <div class="chat-search-item-email">${escapeHtml(usuario.email)}</div>
            </div>
        `).join('');

        // Adiciona event listeners para clique nos resultados
        elementos.searchResults.querySelectorAll('.chat-search-item').forEach(item => {
            item.addEventListener('click', () => {
                const outroUsuarioId = parseInt(item.dataset.usuarioId);
                iniciarConversa(outroUsuarioId);
                elementos.searchInput.value = '';
                elementos.searchResults.classList.add('d-none');
            });
        });
    }

    // ==========================================================================
    // CONVERSAS
    // ==========================================================================

    /**
     * Carrega lista de conversas do servidor.
     * @param {number} offset - Offset para paginação
     */
    async function carregarConversas(offset) {
        try {
            const response = await fetch(`/chat/conversas?limite=20&offset=${offset}`);
            const data = await response.json();

            // Se offset 0, limpa lista existente
            if (offset === 0) {
                elementos.conversasList.innerHTML = '';
                conversasOffset = 0;
            }

            if (data.conversas && data.conversas.length > 0) {
                renderizarConversas(data.conversas);
                elementos.conversasEmpty.classList.add('d-none');
                conversasOffset += data.conversas.length;
            } else if (offset === 0) {
                elementos.conversasEmpty.classList.remove('d-none');
            }
        } catch (error) {
            console.error('[Chat] Erro ao carregar conversas:', error);
        }
    }

    /**
     * Renderiza lista de conversas no DOM.
     * @param {Array} conversas - Lista de conversas
     */
    function renderizarConversas(conversas) {
        const html = conversas.map(conversa => `
            <div class="chat-conversa-item ${conversaAtual && conversaAtual.sala_id === conversa.sala_id ? 'active' : ''}"
                 data-sala-id="${conversa.sala_id}"
                 data-outro-usuario-id="${conversa.outro_usuario.id}"
                 data-outro-usuario-nome="${escapeHtml(conversa.outro_usuario.nome)}">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1 overflow-hidden">
                        <div class="chat-conversa-nome">${escapeHtml(conversa.outro_usuario.nome)}</div>
                        <div class="chat-conversa-preview">${escapeHtml(conversa.ultima_mensagem || 'Sem mensagens')}</div>
                    </div>
                    ${conversa.nao_lidas > 0 ? `<span class="chat-conversa-badge">${conversa.nao_lidas}</span>` : ''}
                </div>
            </div>
        `).join('');

        elementos.conversasList.innerHTML = html;

        // Adiciona event listeners para clique nas conversas
        elementos.conversasList.querySelectorAll('.chat-conversa-item').forEach(item => {
            item.addEventListener('click', () => {
                const salaId = item.dataset.salaId;
                const outroUsuarioId = parseInt(item.dataset.outroUsuarioId);
                const outroUsuarioNome = item.dataset.outroUsuarioNome;
                abrirConversa(salaId, outroUsuarioId, outroUsuarioNome);
            });
        });
    }

    // ==========================================================================
    // MENSAGENS
    // ==========================================================================

    /**
     * Inicia nova conversa com um usuário.
     * @param {number} outroUsuarioId - ID do usuário
     */
    async function iniciarConversa(outroUsuarioId) {
        try {
            const formData = new FormData();
            formData.append('outro_usuario_id', outroUsuarioId);

            const response = await fetch('/chat/salas', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                abrirConversa(data.sala_id, data.outro_usuario.id, data.outro_usuario.nome);
                carregarConversas(0);
            } else {
                console.error('[Chat] Erro ao criar sala:', data.detail);
            }
        } catch (error) {
            console.error('[Chat] Erro ao iniciar conversa:', error);
        }
    }

    /**
     * Abre uma conversa existente.
     * @param {string} salaId - ID da sala
     * @param {number} outroUsuarioId - ID do outro usuário
     * @param {string} outroUsuarioNome - Nome do outro usuário
     */
    function abrirConversa(salaId, outroUsuarioId, outroUsuarioNome) {
        // Atualiza estado da conversa atual
        conversaAtual = {
            sala_id: salaId,
            outro_usuario_id: outroUsuarioId,
            outro_usuario_nome: outroUsuarioNome
        };

        // Atualiza UI
        elementos.conversaNome.textContent = outroUsuarioNome;
        elementos.mensagensList.innerHTML = '';
        mensagensOffset = 0;

        // Mostra container de mensagens, esconde lista de conversas
        elementos.conversasContainer.classList.add('d-none');
        elementos.mensagensContainer.classList.remove('d-none');

        // Carrega mensagens da conversa
        carregarMensagens(salaId, 0);

        // Marca mensagens como lidas
        marcarMensagensComoLidas(salaId);

        // Foca no input para digitar
        elementos.messageInput.focus();
    }

    /**
     * Volta para a lista de conversas.
     */
    function voltarParaConversas() {
        conversaAtual = null;
        elementos.mensagensContainer.classList.add('d-none');
        elementos.conversasContainer.classList.remove('d-none');
        carregarConversas(0);
    }

    /**
     * Carrega mensagens de uma sala.
     * @param {string} salaId - ID da sala
     * @param {number} offset - Offset para paginação
     */
    async function carregarMensagens(salaId, offset) {
        try {
            const response = await fetch(`/chat/mensagens/${salaId}?limite=50&offset=${offset}`);
            const data = await response.json();

            if (data.mensagens && data.mensagens.length > 0) {
                // Mensagens vêm em ordem DESC, precisamos inverter para exibir
                const mensagens = data.mensagens.reverse();

                if (offset === 0) {
                    // Primeira carga: adiciona no final
                    mensagens.forEach(msg => renderizarMensagem(msg, false));
                    scrollParaFim();
                } else {
                    // Scroll infinito: adiciona no início
                    mensagens.forEach(msg => renderizarMensagem(msg, true));
                }

                mensagensOffset += data.mensagens.length;
            }
        } catch (error) {
            console.error('[Chat] Erro ao carregar mensagens:', error);
        }
    }

    /**
     * Renderiza uma mensagem no DOM.
     * @param {Object} mensagem - Dados da mensagem
     * @param {boolean} prepend - Se true, adiciona no início (scroll infinito)
     */
    function renderizarMensagem(mensagem, prepend = false) {
        // Verifica se é mensagem enviada ou recebida
        const isEnviada = mensagem.usuario_id === usuarioId;
        const hora = formatarHora(mensagem.data_envio);

        const html = `
            <div class="chat-mensagem ${isEnviada ? 'chat-mensagem-enviada' : 'chat-mensagem-recebida'}">
                <div class="chat-mensagem-texto">${escapeHtml(mensagem.mensagem)}</div>
                <div class="chat-mensagem-hora">${hora}</div>
            </div>
        `;

        if (prepend) {
            elementos.mensagensList.insertAdjacentHTML('afterbegin', html);
        } else {
            elementos.mensagensList.insertAdjacentHTML('beforeend', html);
        }
    }

    /**
     * Envia uma mensagem.
     * @param {Event} event - Evento de submit do form
     */
    async function enviarMensagem(event) {
        event.preventDefault();

        if (!conversaAtual) return;

        const mensagem = elementos.messageInput.value.trim();
        if (!mensagem) return;

        try {
            const formData = new FormData();
            formData.append('sala_id', conversaAtual.sala_id);
            formData.append('mensagem', mensagem);

            const response = await fetch('/chat/mensagens', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                // Limpa input
                elementos.messageInput.value = '';
                // Mensagem será adicionada na tela via SSE
            } else {
                const data = await response.json();
                console.error('[Chat] Erro ao enviar mensagem:', data.detail);
            }
        } catch (error) {
            console.error('[Chat] Erro ao enviar mensagem:', error);
        }
    }

    /**
     * Marca mensagens de uma sala como lidas.
     * @param {string} salaId - ID da sala
     */
    async function marcarMensagensComoLidas(salaId) {
        try {
            await fetch(`/chat/mensagens/lidas/${salaId}`, {
                method: 'POST'
            });
            atualizarContadorNaoLidas();
        } catch (error) {
            console.error('[Chat] Erro ao marcar mensagens como lidas:', error);
        }
    }

    // ==========================================================================
    // CONTADOR DE NÃO LIDAS
    // ==========================================================================

    /**
     * Atualiza o badge com total de mensagens não lidas.
     */
    async function atualizarContadorNaoLidas() {
        try {
            const response = await fetch('/chat/mensagens/nao-lidas/total');
            const data = await response.json();

            const total = data.total || 0;

            if (total > 0) {
                // Exibe badge com número (máximo 99+)
                elementos.badge.textContent = total > 99 ? '99+' : total;
                elementos.badge.classList.remove('d-none');
            } else {
                // Esconde badge
                elementos.badge.classList.add('d-none');
            }
        } catch (error) {
            console.error('[Chat] Erro ao atualizar contador:', error);
        }
    }

    // ==========================================================================
    // UTILITÁRIOS
    // ==========================================================================

    /**
     * Rola a lista de mensagens para o final.
     */
    function scrollParaFim() {
        elementos.mensagensList.scrollTop = elementos.mensagensList.scrollHeight;
    }

    /**
     * Handler para scroll infinito de mensagens.
     */
    function onMensagensScroll() {
        // Quando chega no topo, carrega mais mensagens antigas
        if (elementos.mensagensList.scrollTop === 0 && conversaAtual) {
            carregarMensagens(conversaAtual.sala_id, mensagensOffset);
        }
    }

    /**
     * Formata data/hora para exibição.
     * @param {string} dataString - Data em formato ISO
     * @returns {string} Hora formatada (HH:MM)
     */
    function formatarHora(dataString) {
        if (!dataString) return '';
        const data = new Date(dataString);
        return data.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    }

    /**
     * Escapa HTML para prevenir XSS.
     * @param {string} text - Texto a escapar
     * @returns {string} Texto escapado
     */
    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Destrói o widget e fecha conexões.
     */
    function destruir() {
        if (eventSource) {
            eventSource.close();
            eventSource = null;
        }
    }

    // ==========================================================================
    // API PÚBLICA
    // ==========================================================================

    return {
        init,
        destruir,
        enviarMensagem,
        carregarMaisConversas: () => carregarConversas(conversasOffset)
    };
})();
```

---

## Arquivo Principal

### main.py

```python
# =============================================================================
# CHAT APP - ARQUIVO PRINCIPAL
# =============================================================================
# Ponto de entrada da aplicação FastAPI.
# Configura middleware, rotas e inicia o servidor.

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
```

---

## Executando a Aplicação

### 11.1 Passos para Execução

1. **Certifique-se de que o ambiente virtual está ativado:**
   ```bash
   # No macOS/Linux:
   source .venv/bin/activate

   # No Windows:
   .venv\Scripts\activate
   ```

2. **Instale as dependências (se ainda não instalou):**
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute a aplicação:**
   - Pelo VS Code: Pressione **F5** ou **Ctrl+F5**
   - Pelo terminal:
     ```bash
     python main.py
     ```

4. **Acesse no navegador:**
   ```
   http://localhost:8000
   ```

5. **Abra uma janela anônima e acesse novamente:**
    ```
   http://localhost:8000
   ```

### 11.2 Fluxo de Teste

1. **Cadastre dois usuários** em navegadores diferentes
2. **Faça login** com cada usuário
3. Na página home, **clique no botão de chat** (canto inferior direito)
4. **Busque o outro usuário** no campo de busca
5. **Clique no usuário** para iniciar uma conversa
6. **Envie mensagens** e observe o chat em tempo real

### 11.3 Características Implementadas

| Recurso | Descrição |
|---------|-----------|
| Autenticação por sessão | Login/logout sem refresh tokens |
| Cadastro de usuário | Com validação de dados |
| Chat em tempo real | Usando Server-Sent Events (SSE) |
| Múltiplas conversas | Lista de conversas com preview |
| Contador de não lidas | Badge no botão e por conversa |
| Busca de usuários | Autocomplete para iniciar chat |
| Widget independente | Componente reutilizável |
| Responsivo | Adaptado para mobile |

### 11.4 Enviando Atualizações para o GitHub

Após fazer a conclusão da atividade, faça o commit com a mensagem **versao final** e faça a sincronização com o GitHub.

---

## Conclusão

Este guia apresentou um passo a passo completo para criar uma aplicação de chat com autenticação básica. O sistema utiliza:

- **FastAPI** como framework web
- **Sessões** para autenticação (sem JWT/refresh tokens)
- **SSE** para comunicação em tempo real
- **SQLite** como banco de dados
- **Bootstrap 5** para interface

O componente de chat é independente e pode ser facilmente integrado em outras páginas, bastando incluir o HTML, CSS e JavaScript, e chamar `chatWidget.init()` após o carregamento da página.
