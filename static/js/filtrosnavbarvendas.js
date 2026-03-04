document.addEventListener('DOMContentLoaded', function () {
  const filtroInput = document.getElementById('filtroTabela');
  const filtroContainer = document.getElementById('filtrosVendas');
  const tabela = document.querySelector('table tbody');
  const linhasOriginais = Array.from(tabela.querySelectorAll('tr'));
  let filtroTipo = 'todos';

  // Função que renderiza linhas filtradas e/ou ordenadas
  function aplicarFiltros() {
    let linhas = [...linhasOriginais];

    // 🔍 Filtro por texto
    const termo = filtroInput.value.toLowerCase();
    if (termo) {
      linhas = linhas.filter(linha =>
        linha.innerText.toLowerCase().includes(termo)
      );
    }

    // 📊 Ordenação: mais ou menos vendidos
    if (filtroTipo === 'mais_vendidos' || filtroTipo === 'menos_vendidos') {
      linhas.sort((a, b) => {
        const qtdA = parseFloat(a.children[3].innerText.replace(',', '.')) || 0;
        const qtdB = parseFloat(b.children[3].innerText.replace(',', '.')) || 0;
        return filtroTipo === 'mais_vendidos' ? qtdB - qtdA : qtdA - qtdB;
      });
    }

    // 🔄 Atualiza tabela
    tabela.innerHTML = '';
    linhas.forEach(linha => tabela.appendChild(linha));
  }

  // Evento: digitar no campo de filtro
  filtroInput.addEventListener('input', aplicarFiltros);

  // Evento: clicar nos botões da navbar
  filtroContainer.addEventListener('click', (e) => {
    e.preventDefault();
    const link = e.target.closest('.nav-link');
    if (!link) return;

    // Remove destaque dos outros
    filtroContainer.querySelectorAll('.nav-link').forEach(a => a.classList.remove('active'));

    // Marca o botão clicado
    link.classList.add('active');

    // Atualiza tipo de filtro
    filtroTipo = link.dataset.filtro;

    aplicarFiltros();
  });
});
