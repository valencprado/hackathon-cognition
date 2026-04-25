/* =============================================
   STUDY AI — MAIN SCRIPT
   Comportamento: pesquisa → POST /search → lista
   ============================================= */

// ---- DOM REFS ----
const heroSection      = document.getElementById('heroSection');
const searchInput      = document.getElementById('searchInput');
const searchBtn        = document.getElementById('searchBtn');
const resultsSection   = document.getElementById('resultsSection');
const resultsList      = document.getElementById('resultsList');
const resultsQueryText = document.getElementById('resultsQueryText');
const cardOverlay      = document.getElementById('cardOverlay');
const cardModal        = document.getElementById('cardModal');
const modalContent     = document.getElementById('modalContent');
const modalClose       = document.getElementById('modalClose');

// ---- HELPERS ----
function esc(str) {
  const el = document.createElement('span');
  el.textContent = str;
  return el.innerHTML;
}

function formatEmoji(formato) {
  const map = { livro: '\u{1F4D8}', revista: '\u{1F4F0}', hq: '\u{1F3A8}', dvd: '\u{1F3AC}' };
  return map[(formato || '').toLowerCase()] || '\u{1F4D8}';
}

// ---- MAP API BOOK → UI BOOK ----
function mapApiBook(apiBook, index) {
  const formato = (apiBook.formato || 'livro');
  return {
    id: index + 1,
    type: formato.charAt(0).toUpperCase() + formato.slice(1),
    emoji: formatEmoji(formato),
    title: apiBook.titulo || '',
    author: apiBook.autor || '',
    level: apiBook.faixa_etaria || '',
    year: apiBook.ano || null,
    location: apiBook.onde_encontrar || '',
    tags: apiBook.temas || [],
    description: apiBook.sinopse || '',
    resumo: apiBook.resumo || '',
    conexao_tema: apiBook.conexao_tema || '',
    topico_principal: apiBook.topico_principal || '',
  };
}

// ---- FETCH BOOKS FROM API ----
async function fetchBooks(query, formats) {
  const response = await fetch('/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, formats }),
  });

  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.error || 'Erro ao buscar recomenda\u00E7\u00F5es');
  }

  const data = await response.json();
  const books = (data.books || []).map(mapApiBook);
  return { books, analise: data.analise || '', topicos: data.topicos || [] };
}

// ---- RENDER SKELETON ----
function renderSkeletons() {
  resultsList.innerHTML = Array(4).fill(`
    <div class="skeleton-item">
      <div class="skel-cover"></div>
      <div class="skel-body">
        <div class="skel-line w-40"></div>
        <div class="skel-line w-80"></div>
        <div class="skel-line w-60"></div>
      </div>
    </div>
  `).join('');
}

// ---- RENDER RESULTS ----
function renderResults(books) {
  resultsList.innerHTML = books.map((b, i) => `
    <div class="result-item" style="animation-delay:${0.05 + i * 0.07}s">
      <div class="book-cover-placeholder">${b.emoji}</div>
      <div class="item-body">
        <div class="item-type">${esc(b.type)}</div>
        <div class="item-title">${esc(b.title)}</div>
        <div class="item-author">${esc(b.author)}</div>
        <div class="item-meta">
          ${b.level ? `<span class="avail avail-ok">${esc(b.level)}</span>` : ''}
        </div>
      </div>
      <button class="extend-btn" onclick="openModal(${b.id}, '${encodeURIComponent(JSON.stringify(books))}')">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
          <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
        <span>Expandir</span>
      </button>
    </div>
  `).join('');
}

// ---- RENDER ERROR ----
function renderError(message) {
  resultsList.innerHTML = `
    <div class="result-item" style="text-align:center;padding:32px;">
      <p style="color:var(--text-muted);font-size:15px;">${esc(message)}</p>
    </div>
  `;
}

// ---- OPEN MODAL ----
function openModal(id, encodedBooks) {
  const books = JSON.parse(decodeURIComponent(encodedBooks));
  const b = books.find(x => x.id === id);
  if (!b) return;

  modalContent.innerHTML = `
    <div class="modal-cover-wrap">
      <div class="modal-cover">${b.emoji}</div>
      <div class="modal-meta-block">
        <div class="modal-type">${esc(b.type)}</div>
        <h2 class="modal-title">${esc(b.title)}</h2>
        <p class="modal-author">${esc(b.author)}</p>
        <div class="modal-badges">
          ${b.level ? `<span class="modal-badge">${esc(b.level)}</span>` : ''}
        </div>
      </div>
    </div>

    <div class="modal-section">
      <div class="modal-section-title">Sobre</div>
      <p class="modal-description">${esc(b.description)}</p>
    </div>

    ${b.resumo ? `
    <div class="modal-section">
      <div class="modal-section-title">Por que ler</div>
      <p class="modal-description">${esc(b.resumo)}</p>
    </div>
    ` : ''}

    ${b.conexao_tema ? `
    <div class="modal-section">
      <div class="modal-section-title">Conex\u00E3o com o tema</div>
      <p class="modal-description">${esc(b.conexao_tema)}</p>
    </div>
    ` : ''}

    <div class="modal-section">
      <div class="modal-section-title">Assuntos</div>
      <div class="modal-topics">
        ${b.tags.map(t => `<span class="topic-tag">${esc(t)}</span>`).join('')}
      </div>
    </div>

    <div class="modal-section">
      <div class="modal-section-title">Onde Encontrar</div>
      <div class="location-card">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
          <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" stroke="currentColor" stroke-width="2"/>
          <circle cx="12" cy="9" r="2.5" stroke="currentColor" stroke-width="2"/>
        </svg>
        <div>
          <span class="location-main">${esc(b.location)}</span>
        </div>
      </div>
    </div>

    <div class="modal-section">
      <div class="modal-section-title">Informa\u00E7\u00F5es</div>
      <div class="modal-info-grid">
        ${b.level ? `
        <div class="info-cell">
          <span class="info-label">Faixa et\u00E1ria</span>
          <span class="info-value">${esc(b.level)}</span>
        </div>
        ` : ''}
        ${b.year ? `
        <div class="info-cell">
          <span class="info-label">Publica\u00E7\u00E3o</span>
          <span class="info-value">${b.year}</span>
        </div>
        ` : ''}
        ${b.topico_principal ? `
        <div class="info-cell">
          <span class="info-label">T\u00F3pico</span>
          <span class="info-value">${esc(b.topico_principal)}</span>
        </div>
        ` : ''}
      </div>
    </div>
  `;

  cardOverlay.classList.add('is-open');
  cardOverlay.setAttribute('aria-hidden', 'false');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  cardOverlay.classList.remove('is-open');
  cardOverlay.setAttribute('aria-hidden', 'true');
  document.body.style.overflow = '';
}

// ---- SEARCH FLOW ----
async function triggerSearch() {
  const query = searchInput.value.trim();
  if (!query) { searchInput.focus(); return; }

  // Collect selected format filters
  const checked = document.querySelectorAll('input[name="format"]:checked');
  const formats = Array.from(checked).map(cb => cb.value.toLowerCase());

  heroSection.classList.add('is-collapsed');
  resultsSection.classList.add('is-visible');
  resultsQueryText.textContent = query;
  renderSkeletons();

  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      resultsSection.classList.add('is-animated');
    });
  });

  try {
    const { books } = await fetchBooks(query, formats);
    renderResults(books);
  } catch (err) {
    renderError(err.message || 'Erro inesperado. Tente novamente.');
  }
}

function resetSearch() {
  heroSection.classList.remove('is-collapsed');
  resultsSection.classList.remove('is-visible', 'is-animated');
  resultsList.innerHTML = '';
  searchInput.value = '';
  searchInput.focus();
}

// ---- EVENTS ----
searchBtn.addEventListener('click', triggerSearch);

searchInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') triggerSearch();
});

modalClose.addEventListener('click', closeModal);

cardOverlay.addEventListener('click', (e) => {
  if (e.target === cardOverlay) closeModal();
});

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeModal();
});
