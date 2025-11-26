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