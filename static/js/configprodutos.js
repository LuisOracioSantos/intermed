window.addEventListener("load", function () {
    if (itemIdInicial) {
        document.getElementById("iditemprincipal").value = itemIdInicial;
        document.getElementById("item").value = itemInicial;
        document.getElementById("itemdescricao").value = descricaoInicial;

        console.log("Carregando relacionados para itemid:", itemIdInicial);
        carregarRelacionados(itemIdInicial);

        // Desabilitar botões se quiser
        const btnAdicionar = document.getElementById("btnAdicionar");
        const btnSalvar = document.getElementById("btnSalvar");
        if (btnAdicionar) btnAdicionar.setAttribute("disabled", "disabled");
        if (btnSalvar) btnSalvar.setAttribute("disabled", "disabled");
    }
});


 function carregarProdutos(pagina = 1) {
    const termoBusca = document.getElementById("campoBusca").value;

    fetch(`/getDadosProdutosCadastro?page=${pagina}&per_page=20&busca=${encodeURIComponent(termoBusca)}`)
        .then(res => res.json())
        .then(data => {
            const tabela = document.getElementById("tabelaProdutosCadastro");
            tabela.innerHTML = "";

            data.produtos.forEach(produto => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${produto.itemid}</td>
                    <td>${produto.item}</td>
                    <td>${produto.descricao}</td>
                `;

                // Evento de duplo clique para retornar os dados
               tr.addEventListener('dblclick', function () {
    // Preencher campos principais
    document.getElementById("iditemprincipal").value = produto.itemid;
    document.getElementById("item").value = produto.item;
    document.getElementById("itemdescricao").value = produto.descricao;

    const tabela = document.getElementById("tabelaProdutosRelacionados").querySelector("tbody");
        // Busca itens relacionados
        fetch(`/get-produtos-relacionados/${produto.itemid}`)
            .then(res => res.json())
                 .then(data => {
                        console.log("RETORNO COMPLETO:", data);
                          if (data.id) {
                                document.getElementById("idprod").value = data.id;
                            }

                      const relacionados = data.relacionados;
                      // Só limpa e preenche se houver relacionados
                       if (relacionados && relacionados.length > 0) {
                            tabela.innerHTML = ""; // ← Limpa a tabela

                            relacionados.forEach(rel => {
                                const trNovo = document.createElement("tr");
                                trNovo.innerHTML = `
                                    <td>${rel.itemid}</td>
                                    <td>${rel.item}</td>
                                    <td>${rel.descricao}</td>
                                    <td><input type="radio" name="produtoPrincipal" value="${rel.itemId}"></td>
                                    <td><button class="btn btn-sm btn-danger" onclick="removerLinha(this)">Remover</button></td>
                                `;
                                tabela.appendChild(trNovo);
                            });
                       }
                    })
                    .catch(error => {
                       console.error("Erro ao buscar produtos relacionados:", error);
                       // Opcional: exibir uma mensagem ao usuário
                 });

                // Fecha o modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('modalDetalhes'));
                modal.hide();
            });
                tabela.appendChild(tr);
        });
            renderizarPaginacao(data.pagina_atual, data.total_paginas, termoBusca);
    });
}



    let paginaAtual = 1;
    let termoBuscaLista = "";
   function carregarListaProdutos(page = 1) {
    paginaAtual = page;

    fetch(`/getProdutosCadastrado?page=${page}&per_page=10&busca=${termoBuscaLista}`)
        .then(res => res.json())
        .then(data => {

            const tabela = document.getElementById("tabelaListaProdutos");
            tabela.innerHTML = "";

           let html = "";

            data.produtos.forEach(p => {
                console.log(p);
                const botaoStatus = p.ativo
                  ? `<button class="btn btn-sm btn-outline-warning me-1"
                        onclick="inativarprodutoforecast(${p.idprodutoforecast})"
                        title="Inativar">
                        <i class="bi bi-pause-circle"></i>
                     </button>`
                  : `<button class="btn btn-sm btn-outline-success me-1"
                        onclick="inativarprodutoforecast(${p.idprodutoforecast})"
                        title="Ativar">
                        <i class="bi bi-check-circle"></i>
                     </button>`;

                html += `
                    <tr>
                        <td>${p.idprodutoforecast}</td>
                        <td>${p.item}</td>
                        <td>${p.descricao}</td>
                        <td>${p.ativo ? 'Ativo' : 'Inativo'}</td>
                        <td class="text-center">
                            ${botaoStatus}
                            <button class="btn btn-sm btn-outline-danger"
                                    onclick="deletarProduto(${p.idprodutoforecast})"
                                    title="Excluir">
                                <i class="bi bi-trash"></i>
                            </button>
                        </td>
                    </tr>
                `;
            });

            tabela.innerHTML = html;

            montarPaginacao(data.pagina_atual, data.total_paginas);
        });
}

function buscarListaProdutos() {
    termoBuscaLista = document.getElementById("buscaLista").value;
    carregarListaProdutos(1);
}

function montarPaginacao(paginaAtual, totalPaginas) {
    const paginacao = document.getElementById("paginacaoLista");
    paginacao.innerHTML = "";

    for (let i = 1; i <= totalPaginas; i++) {
        paginacao.innerHTML += `
            <button class="btn btn-sm ${i === paginaAtual ? 'btn-primary' : 'btn-outline-primary'} me-1"
                onclick="carregarListaProdutos(${i})">
                ${i}
            </button>
        `;
    }
}


function renderizarPaginacao(paginaAtual, totalPaginas, termoBusca = "") {
  const paginacao = document.getElementById("paginacao");
  paginacao.innerHTML = "";

  const criarBotao = (label, pagina, disabled = false, active = false) => {
    const btn = document.createElement("button");
    btn.innerText = label;
    btn.className = "btn btn-sm mx-1 " + (
      active ? "btn-primary" :
      disabled ? "btn-secondary disabled" :
      "btn-outline-secondary"
    );
    if (!disabled && !active) {
      btn.onclick = () => carregarProdutos(pagina);
    }
    return btn;
  };

  paginacao.appendChild(
    criarBotao("Anterior", paginaAtual - 1, paginaAtual === 1)
  );

  const intervalo = 2;
  const inicio = Math.max(1, paginaAtual - intervalo);
  const fim = Math.min(totalPaginas, paginaAtual + intervalo);

  if (inicio > 1) {
    paginacao.appendChild(criarBotao("1", 1));
    if (inicio > 2) {
      const dots = document.createElement("span");
      dots.innerText = "...";
      dots.className = "mx-1";
      paginacao.appendChild(dots);
    }
  }

  for (let i = inicio; i <= fim; i++) {
    paginacao.appendChild(criarBotao(i, i, false, i === paginaAtual));
  }

  if (fim < totalPaginas) {
    if (fim < totalPaginas - 1) {
      const dots = document.createElement("span");
      dots.innerText = "...";
      dots.className = "mx-1";
      paginacao.appendChild(dots);
    }
    paginacao.appendChild(criarBotao(totalPaginas, totalPaginas));
  }

  paginacao.appendChild(
    criarBotao("Próxima", paginaAtual + 1, paginaAtual === totalPaginas)
  );
}

function debounce(func, delay) {
    let timer;
    return function(...args) {
        clearTimeout(timer);
        timer = setTimeout(() => func.apply(this, args), delay);
    };
}

function adicionarProdutoRelacionado() {
    const idprincipal = document.getElementById("iditemprincipal").value.trim();
    const item = document.getElementById("item").value.trim();
    const descricao = document.getElementById("itemdescricao").value.trim();

    if (!idprincipal || !item || !descricao) {
        alert("Selecione um produto antes de adicionar.");
        return;
    }

    const tabela = document.getElementById("tabelaProdutosRelacionados").querySelector("tbody");

    const jaExiste = Array.from(tabela.rows).some(row => {
        return row.cells[0].textContent.trim() === idprincipal;
    });

    if (jaExiste) {
        alert("Este produto já foi adicionado.");
        return;
    }
    // Criação da nova linha
    const tr = document.createElement("tr");
    tr.innerHTML = `
        <td>${idprincipal}</td>
        <td>${item}</td>
        <td>${descricao}</td>
        <td><input type="radio" name="produtoPrincipal" value="${idprincipal}"></td>
        <td>
            <button class="btn btn-sm btn-danger" onclick="removerLinha(this)">Remover</button>
         </td>
    `;

    tabela.appendChild(tr);
}

function removerLinha(botao) {
    const linha = botao.closest("tr");
    if (linha) {
        linha.remove();
    }
}

function salvaProdutoForecast() {
    const tabela = document.getElementById("tabelaProdutosRelacionados");
    const linhas = tabela.querySelector("tbody").rows;
    const radioSelecionado = document.querySelector('input[name="produtoPrincipal"]:checked');

    if (!radioSelecionado) {
        alert("Selecione o produto principal.");
        return;
    }

    const idProdutoPrincipal = parseInt(radioSelecionado.value);
    let descricaoPrincipal = "";
    const produtosRelacionados = [];

     for (let i = 0; i < linhas.length; i++) {
        const row = linhas[i];
        const id = parseInt(row.cells[0].textContent.trim());
        const descricao = row.cells[2].textContent.trim();

        if (id === idProdutoPrincipal) {
            descricaoPrincipal = descricao;
        } else {
            produtosRelacionados.push(id);
        }
    }

    const payload = {
        descricao: descricaoPrincipal,
        idProdutoPrincipal: idProdutoPrincipal,
        produtosRelacionados: produtosRelacionados
    };

    console.log(JSON.stringify(payload)); // mostra a string JSON

    fetch('/cadastrar-produto-forecast', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        if (data.mensagem) {
            alert(data.mensagem);
            limparFormulario();
        } else {
            alert('Erro: ' + (data.erro || 'Erro desconhecido'));
        }
    })
    .catch(error => {
        alert('Erro na requisição: ' + error.message);
    });
}

function deletarProduto(id) {

    if (!id) {
        alert("ID inválido.");
        return;
    }

    if (!confirm("Tem certeza que deseja deletar este produto?")) {
        return;
    }

    fetch(`/deletaprodutoforecast/${id}`, {
        method: "DELETE"
    })
    .then(response => {
        if (response.status === 204) {
            alert("Produto deletado com sucesso!");
            carregarListaProdutos(paginaAtual);
        }
        else if (response.status === 404) {
            alert("Produto não encontrado.");
        }
        else {
            alert("Erro ao deletar produto.");
        }
    })
    .catch(error => {
        console.error("Erro:", error);
        alert("Erro de conexão com o servidor.");
    });
}

function inativarprodutoforecast(idproduto) {

    if (!confirm("Deseja alterar o status deste produto?")) {
        return;
    }

    fetch(`/inativarprodutoforecast/${idproduto}`, {
       method: "PATCH"
    })
    .then(response => {
        if (response.ok) {
            // ✅ Atualiza tabela
            carregarListaProdutos(paginaAtual);
        } else {
            alert("Erro ao alterar status");
        }
    })
    .catch(error => {
        console.error("Erro:", error);
        alert("Erro de conexão");
    });
}

function limparFormulario() {
    // Limpar campos de entrada
    document.getElementById("idprod").value = "";
    document.getElementById("item").value = "";
    document.getElementById("iditemprincipal").value = "";
    document.getElementById("itemdescricao").value = "";

    // Limpar tabela de produtos relacionados
    const tabela = document.getElementById("tabelaProdutosRelacionados").querySelector("tbody");
    tabela.innerHTML = "";
}

function carregarRelacionados(itemid) {
    // Pega o tbody da tabela já existente
    const tabela = document.getElementById("tabelaProdutosRelacionados");
    if (!tabela) {
        console.error("Tabela de relacionados não encontrada!");
        return;
    }

    const tbody = tabela.querySelector("tbody");
    tbody.innerHTML = ""; // Limpa linhas antigas

    fetch(`/get-produtos-relacionados/${itemid}`)
        .then(res => res.json())
        .then(data => {
            console.log("RETORNO COMPLETO:", data);

            if (data.id) {
                document.getElementById("idprod").value = data.id;
            }

            const relacionados = data.relacionados || [];

            relacionados.forEach(rel => {
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td>${rel.itemid}</td>
                    <td>${rel.item}</td>
                    <td>${rel.descricao}</td>
                    <td><input type="radio" name="produtoPrincipal" value="${rel.itemId}"></td>
                    <td><button class="btn btn-sm btn-danger" onclick="removerLinha(this)">Remover</button></td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(error => {
            console.error("Erro ao buscar produtos relacionados:", error);
        });
}

// Substitua o listener direto por isso:
document.getElementById("campoBusca").addEventListener("input", debounce(function () {
    carregarProdutos(1);
}, 300));

const modalElement = document.getElementById('modalDetalhes');

modalElement.addEventListener('shown.bs.modal', function () {
    carregarProdutos(1);
 });



