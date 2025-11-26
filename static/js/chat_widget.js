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