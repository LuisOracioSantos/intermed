document.addEventListener('DOMContentLoaded', function () {
  const modal = document.getElementById('modalDetalhes');
  const filtroInput = document.getElementById('filtroTabelaProdutos');
  const tabela = document.getElementById('tabelaProdutos');
  const btnAnterior = document.getElementById('btnAnterior');
  const btnProximo = document.getElementById('btnProximo');
  const infoPaginacao = document.getElementById('infoPaginacao');

  let dadosOriginais = []; // Todos os dados carregados do fetch
  let dadosFiltrados = []; // Dados filtrados pelo campo de busca
  let paginaAtual = 1;
  const itensPorPagina = 10;

  function renderTabela() {
    tabela.innerHTML = '';

    const inicio = (paginaAtual - 1) * itensPorPagina;
    const fim = inicio + itensPorPagina;
    const dadosPagina = dadosFiltrados.slice(inicio, fim);

    if (dadosPagina.length === 0) {
      tabela.innerHTML = `<tr><td colspan="5" class="text-center">Nenhum produto encontrado.</td></tr>`;
    } else {
      dadosPagina.forEach(produto => {
         const valorFormatado = Number(produto.totalVendido).toLocaleString('pt-BR', {
          style: 'currency',
          currency: 'BRL'
        });

        tabela.innerHTML += `
          <tr>
            <td>${produto.item}</td>
            <td>${produto.descricao}</td>
            <td>${produto.qtdVendida}</td>
            <td>${valorFormatado}  </td>
            <td>${produto.ultimavenda}</td>
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
      const tipoFiltro = document.getElementById('filtroVendaTipo').value;

      // 1️⃣ Filtro de texto (busca)
      if (!termo) {
        dadosFiltrados = [...dadosOriginais];
      } else {
        dadosFiltrados = dadosOriginais.filter(cliente =>
          Object.values(cliente).some(val =>
            String(val).toLowerCase().includes(termo)
          )
        );
      }


      if (tipoFiltro === 'mais_vendidos') {
        dadosFiltrados.sort((a, b) => b.qtdvendida - a.qtdvendida);
      } else if (tipoFiltro === 'menos_vendidos') {
        dadosFiltrados.sort((a, b) => a.qtdvendida - b.qtdvendida);
      }

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
    const cliente = button.getAttribute('data-cliente');

    document.getElementById('clienteNome').innerText = cliente;
    filtroInput.value = '';
    tabela.innerHTML = '';
    infoPaginacao.textContent = '';
    paginaAtual = 1;

    fetch(`/getDadosVendaClienteId/${codigo}`)
      .then(response => response.json())
      .then(data => {
        dadosOriginais = data;
        aplicarFiltro(); // Isso aplica filtro inicial e chama renderTabela()
      });
  });
});