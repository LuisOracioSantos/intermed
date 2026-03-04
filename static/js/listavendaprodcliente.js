document.addEventListener('DOMContentLoaded', function () {
  const modal = document.getElementById('modalDetalhes');
  const filtroInput = document.getElementById('filtroTabelaClientes');
  const tabela = document.getElementById('tabelaClientes');
  const btnAnterior = document.getElementById('btnAnterior');
  const btnProximo = document.getElementById('btnProximo');
  const infoPaginacao = document.getElementById('infoPaginacao');
  const filtroContainer = document.getElementById('filtrosVendas');


  let dadosOriginais = []; // Todos os dados carregados do fetch
  let dadosFiltrados = []; // Dados filtrados pelo campo de busca
  let paginaAtual = 1;
  const itensPorPagina = 10;
  let filtroTipo = 'todos';

  function renderTabela() {
    tabela.innerHTML = '';

    const inicio = (paginaAtual - 1) * itensPorPagina;
    const fim = inicio + itensPorPagina;
    const dadosPagina = dadosFiltrados.slice(inicio, fim);

    if (dadosPagina.length === 0) {
      tabela.innerHTML = `<tr><td colspan="5" class="text-center">Nenhum cliente encontrado.</td></tr>`;
    } else {
      dadosPagina.forEach(clientes => {
         const valorFormatado = Number(clientes.vlrtotalitem).toLocaleString('pt-BR', {
          style: 'currency',
          currency: 'BRL'
        });

        const dataFormatada = new Date(clientes.datavenda).toLocaleDateString('pt-BR');

        tabela.innerHTML += `
          <tr>
            <td>${clientes.apelido}</td>
            <td>${dataFormatada} </td>
            <td>${clientes.qtdvendida}</td>
            <td>${valorFormatado}  </td>
          </tr>
        `;
      });
    }

    const totalPaginas = Math.ceil(dadosFiltrados.length / itensPorPagina);
    infoPaginacao.textContent = `Página ${paginaAtual} de ${totalPaginas}`;
    btnAnterior.disabled = paginaAtual === 1;
    btnProximo.disabled = paginaAtual === totalPaginas || totalPaginas === 0;
  }


  function aplicarFiltro() {
    const termo = filtroInput.value.toLowerCase();
    dadosFiltrados = dadosOriginais.filter(clientes =>
      Object.values(clientes).some(val =>
        String(val).toLowerCase().includes(termo)
      )
    );
    paginaAtual = 1;
    renderTabela();
  }

  filtroInput.addEventListener('input', aplicarFiltro);

  btnAnterior.addEventListener('click', () => {
    if (paginaAtual > 1) {
      paginaAtual--;
      renderTabela();
    }
  });

  btnProximo.addEventListener('click', () => {
    const totalPaginas = Math.ceil(dadosFiltrados.length / itensPorPagina);
    if (paginaAtual < totalPaginas) {
      paginaAtual++;
      renderTabela();
    }
  });

  modal.addEventListener('show.bs.modal', function (event) {
    const button = event.relatedTarget;
    const codigo = button.getAttribute('data-codigo');
    const descricao = button.getAttribute('data-produto');

    document.getElementById('produto_descricao').innerText = descricao;
    filtroInput.value = '';
    tabela.innerHTML = '';
    infoPaginacao.textContent = '';
    paginaAtual = 1;

    fetch(`/getDadosVendaClienteProdutoId/${codigo}`)
      .then(response => response.json())
      .then(data => {
        dadosOriginais = data;
        aplicarFiltro(); // Isso aplica filtro inicial e chama renderTabela()
      });
  });
});