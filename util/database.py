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