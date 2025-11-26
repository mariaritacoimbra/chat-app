// Wrapper IIFE para evitar poluição global
const chatWidget = (() => {
    let eventSource = null;
    let conversaAtual = null;
    let usuarioId = null;
    let mensagensOffset = 0;
    let conversasOffset = 0;
    let buscaTimeout = null;
    const elementos = {};

    function init() {
        usuarioId = parseInt(document.body.dataset.usuarioId);
        if (!usuarioId) { console.error('[Chat] ID do usuário não encontrado'); return; }
        cacheElementos();
        conectarSSE();
        carregarConversas(0);
        atualizarContadorNaoLidas();
        configurarEventListeners();
        console.log('[Chat] Widget inicializado para usuário', usuarioId);
    }

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

    function configurarEventListeners() {
        elementos.toggleBtn.addEventListener('click', togglePanel);
        elementos.closeBtn.addEventListener('click', fecharPanel);
        elementos.searchInput.addEventListener('input', onSearchInput);
        elementos.searchInput.addEventListener('blur', () => setTimeout(() => elementos.searchResults.classList.add('d-none'), 200));
        elementos.voltarBtn.addEventListener('click', voltarParaConversas);
        elementos.messageForm.addEventListener('submit', enviarMensagem);
        elementos.mensagensList.addEventListener('scroll', onMensagensScroll);
    }

    function conectarSSE() {
        eventSource = new EventSource('/chat/stream');
        eventSource.onmessage = (event) => {
            const mensagem = JSON.parse(event.data); processarMensagemSSE(mensagem);
        };
        eventSource.onerror = (err) => console.error('[Chat SSE] Erro:', err);
        eventSource.onopen = () => console.log('[Chat SSE] Conexão estabelecida');
    }

    function processarMensagemSSE(evento) {
        if (evento.tipo === 'nova_mensagem') {
            const mensagem = evento.mensagem;
            if (conversaAtual && evento.sala_id === conversaAtual.sala_id) {
                renderizarMensagem(mensagem, false); scrollParaFim();
                if (mensagem.usuario_id !== usuarioId) marcarMensagensComoLidas(evento.sala_id);
            }
            carregarConversas(0);
            atualizarContadorNaoLidas();
        }
    }

    function togglePanel() { elementos.panel.classList.toggle('d-none'); }
    function fecharPanel() { elementos.panel.classList.add('d-none'); }

    function onSearchInput(e) {
        const termo = e.target.value.trim();
        if (buscaTimeout) clearTimeout(buscaTimeout);
        if (termo.length < 2) { elementos.searchResults.classList.add('d-none'); return; }
        buscaTimeout = setTimeout(() => buscarUsuarios(termo), 300);
    }

    async function buscarUsuarios(termo) {
        try {
            const resp = await fetch(`/chat/usuarios/buscar?q=${encodeURIComponent(termo)}`);
            const data = await resp.json();
            if (data.usuarios && data.usuarios.length) {
                renderizarResultadosBusca(data.usuarios); elementos.searchResults.classList.remove('d-none');
            } else {
                elementos.searchResults.innerHTML = '<div class="p-2 text-muted small">Nenhum usuário encontrado</div>';
                elementos.searchResults.classList.remove('d-none');
            }
        } catch (e) { console.error('[Chat] Erro busca usuários:', e); }
    }

    function renderizarResultadosBusca(usuarios) {
        elementos.searchResults.innerHTML = usuarios.map(u => `
            <div class="chat-search-item" data-usuario-id="${u.id}">
                <div class="chat-search-item-nome">${escapeHtml(u.nome)}</div>
                <div class="chat-search-item-email">${escapeHtml(u.email)}</div>
            </div>`).join('');
        elementos.searchResults.querySelectorAll('.chat-search-item').forEach(item => {
            item.addEventListener('click', () => {
                const outroUsuarioId = parseInt(item.dataset.usuarioId);
                iniciarConversa(outroUsuarioId); elementos.searchInput.value=''; elementos.searchResults.classList.add('d-none');
            });
        });
    }

    async function carregarConversas(offset) {
        try {
            const resp = await fetch(`/chat/conversas?limite=20&offset=${offset}`);
            const data = await resp.json();
            if (offset === 0) { elementos.conversasList.innerHTML=''; conversasOffset = 0; }
            if (data.conversas && data.conversas.length) {
                renderizarConversas(data.conversas); elementos.conversasEmpty.classList.add('d-none'); conversasOffset += data.conversas.length;
            } else if (offset === 0) { elementos.conversasEmpty.classList.remove('d-none'); }
        } catch(e){ console.error('[Chat] Erro carregar conversas:', e); }
    }

    function renderizarConversas(conversas) {
        elementos.conversasList.innerHTML = conversas.map(c => `
            <div class="chat-conversa-item ${conversaAtual && conversaAtual.sala_id === c.sala_id ? 'active' : ''}" data-sala-id="${c.sala_id}" data-outro-usuario-id="${c.outro_usuario.id}" data-outro-usuario-nome="${escapeHtml(c.outro_usuario.nome)}">
                <div class="d-flex justify-content-between align-items-start">
                    <div class="flex-grow-1 overflow-hidden">
                        <div class="chat-conversa-nome">${escapeHtml(c.outro_usuario.nome)}</div>
                        <div class="chat-conversa-preview">${escapeHtml(c.ultima_mensagem || 'Sem mensagens')}</div>
                    </div>
                    ${c.nao_lidas > 0 ? `<span class="chat-conversa-badge">${c.nao_lidas}</span>` : ''}
                </div>
            </div>`).join('');
        elementos.conversasList.querySelectorAll('.chat-conversa-item').forEach(item => {
            item.addEventListener('click', () => abrirConversa(item.dataset.salaId, parseInt(item.dataset.outroUsuarioId), item.dataset.outroUsuarioNome));
        });
    }

    async function iniciarConversa(outroUsuarioId) {
        try {
            const fd = new FormData(); fd.append('outro_usuario_id', outroUsuarioId);
            const resp = await fetch('/chat/salas', { method:'POST', body: fd });
            const data = await resp.json();
            if (resp.ok) { abrirConversa(data.sala_id, data.outro_usuario.id, data.outro_usuario.nome); carregarConversas(0); }
            else { console.error('[Chat] Erro criar sala:', data.detail); }
        } catch(e){ console.error('[Chat] Erro iniciar conversa:', e); }
    }

    function abrirConversa(salaId, outroUsuarioId, outroUsuarioNome) {
        conversaAtual = { sala_id: salaId, outro_usuario_id: outroUsuarioId, outro_usuario_nome: outroUsuarioNome };
        elementos.conversaNome.textContent = outroUsuarioNome;
        elementos.mensagensList.innerHTML=''; mensagensOffset=0;
        elementos.conversasContainer.classList.add('d-none');
        elementos.mensagensContainer.classList.remove('d-none');
        carregarMensagens(salaId,0); marcarMensagensComoLidas(salaId); elementos.messageInput.focus();
    }

    function voltarParaConversas() { conversaAtual=null; elementos.mensagensContainer.classList.add('d-none'); elementos.conversasContainer.classList.remove('d-none'); carregarConversas(0); }

    async function carregarMensagens(salaId, offset) {
        try {
            const resp = await fetch(`/chat/mensagens/${salaId}?limite=50&offset=${offset}`);
            const data = await resp.json();
            if (data.mensagens && data.mensagens.length) {
                const mensagens = data.mensagens.reverse();
                if (offset === 0) { mensagens.forEach(m => renderizarMensagem(m,false)); scrollParaFim(); }
                else { mensagens.forEach(m => renderizarMensagem(m,true)); }
                mensagensOffset += data.mensagens.length;
            }
        } catch(e){ console.error('[Chat] Erro carregar mensagens:', e); }
    }

    function renderizarMensagem(mensagem, prepend=false) {
        const isEnviada = mensagem.usuario_id === usuarioId;
        const hora = formatarHora(mensagem.data_envio);
        const html = `<div class="chat-mensagem ${isEnviada ? 'chat-mensagem-enviada' : 'chat-mensagem-recebida'}"><div class="chat-mensagem-texto">${escapeHtml(mensagem.mensagem)}</div><div class="chat-mensagem-hora">${hora}</div></div>`;
        if (prepend) elementos.mensagensList.insertAdjacentHTML('afterbegin', html); else elementos.mensagensList.insertAdjacentHTML('beforeend', html);
    }

    async function enviarMensagem(e) {
        e.preventDefault(); if (!conversaAtual) return;
        const mensagem = elementos.messageInput.value.trim(); if (!mensagem) return;
        try {
            const fd = new FormData(); fd.append('sala_id', conversaAtual.sala_id); fd.append('mensagem', mensagem);
            const resp = await fetch('/chat/mensagens', { method:'POST', body: fd });
            if (resp.ok) { elementos.messageInput.value=''; } else { const data = await resp.json(); console.error('[Chat] Erro enviar mensagem:', data.detail); }
        } catch(e){ console.error('[Chat] Erro enviar mensagem:', e); }
    }

    async function marcarMensagensComoLidas(salaId) {
        try { await fetch(`/chat/mensagens/lidas/${salaId}`, { method:'POST' }); atualizarContadorNaoLidas(); } catch(e){ console.error('[Chat] Erro marcar lidas:', e); }
    }

    async function atualizarContadorNaoLidas() {
        try { const resp = await fetch('/chat/mensagens/nao-lidas/total'); const data = await resp.json(); const total = data.total || 0; if (total>0){ elementos.badge.textContent = total>99?'99+':total; elementos.badge.classList.remove('d-none'); } else { elementos.badge.classList.add('d-none'); } } catch(e){ console.error('[Chat] Erro contador não lidas:', e); }
    }

    function scrollParaFim(){ elementos.mensagensList.scrollTop = elementos.mensagensList.scrollHeight; }
    function onMensagensScroll(){ if (elementos.mensagensList.scrollTop === 0 && conversaAtual) carregarMensagens(conversaAtual.sala_id, mensagensOffset); }
    function formatarHora(dataString){ if(!dataString) return ''; const d=new Date(dataString); return d.toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'}); }
    function escapeHtml(text){ if(!text) return ''; const div=document.createElement('div'); div.textContent=text; return div.innerHTML; }
    function destruir(){ if(eventSource){ eventSource.close(); eventSource=null; } }

    return { init, destruir, enviarMensagem, carregarMaisConversas: () => carregarConversas(conversasOffset) };
})();
