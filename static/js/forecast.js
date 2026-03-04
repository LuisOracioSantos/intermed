document.addEventListener('DOMContentLoaded', function () {
    // Elementos do DOM
    const botaoAbrirModal = document.getElementById('btnAbrirModal');
    const botaoBuscar = document.getElementById('btnBuscar');
    const campoBusca = document.getElementById('campoBusca');
    const tabela = document.getElementById('tabelaMesesForecast');
    const botaoCriar = document.getElementById('criarForecastBtn');
    const btnAtualizar = document.getElementById('btnAtualizar');
    const status = document.getElementById('status');  // status da atualização
    const bntFecharforecast = document.getElementById('btnFecharForecast');

    let dadosOriginais = [];

    function aplicarMeses(ids, meses, prefixo = "") {
    ids.forEach((id, index) => {
        const el = document.getElementById(id);
        if (!el) return;

        const span = el.querySelector("span"); // pega a seta se existir

        const texto = prefixo ? `${prefixo} ${meses[index]}` : meses[index];

        if (span) {
            el.innerHTML = texto + " ";
            el.appendChild(span); // recoloca a seta
        } else {
            el.textContent = texto;
        }
    });
}

    // Função para gerar lista de meses
    function gerarMeses(mesBase, ano, offsetInicial, quantidade) {
        const nomesMeses = [
            "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ];
        const meses = [];
        for (let i = 0; i < quantidade; i++) {
            const data = new Date(ano, mesBase - 1 + offsetInicial + i, 1);
            meses.push(nomesMeses[data.getMonth()]);
        }
        return meses;
    }

    // Atualiza os meses na tabela
    function atualizarNomesMesesComBase(mesNumero, ano) {
        aplicarMeses(
            ["mes1", "mes2", "mes3"],
            gerarMeses(mesNumero, ano, -3, 3)
        );

        const mesesFuturos = gerarMeses(mesNumero, ano, 0, 4);
        aplicarMeses(["chegada1","chegada2","chegada3","chegada4"], mesesFuturos, "Chegada");
        aplicarMeses(["prog1","prog2","prog3","prog4"], mesesFuturos, "Prog");
    }

    // Inicializa meses e título
    function inicializarMeses() {
        const params = new URLSearchParams(window.location.search);
        const hoje = new Date();
        const mesParam = parseInt(params.get("mes")) || hoje.getMonth() + 1;
        const anoParam = parseInt(params.get("ano")) || hoje.getFullYear();

        const nomesMeses = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"];
        const mesNome = nomesMeses[mesParam];

        const tituloPagina = document.getElementById("tituloPagina");
        if (tituloPagina) {
            tituloPagina.textContent = `Forecast - ${mesNome}/${anoParam}`;
            document.title = `Forecast - ${mesNome}/${anoParam}`;
        }

        atualizarNomesMesesComBase(mesParam, anoParam);
    }

    inicializarMeses();

    //Abrir modal e carregar lista de meses
    if (botaoAbrirModal) {
        botaoAbrirModal.addEventListener('click', function (e) {
            e.preventDefault();

            fetch('/getMesesForecast')
                .then(response => response.json())
                .then(data => {
                    dadosOriginais = data;
                    renderizarTabela(data);

                    const modalElement = document.getElementById('modalBuscaForecast');
                    const modal = new bootstrap.Modal(modalElement);
                    modal.show();
                })
                .catch(error => {
                    console.error('Erro ao buscar forecast:', error);
                });
        });
    }

    //Botão de busca
    if (botaoBuscar) {
        botaoBuscar.addEventListener('click', function () {
            const termo = campoBusca.value.trim().toLowerCase();

            const filtrados = dadosOriginais.filter(item =>
                item.mes.toLowerCase().includes(termo) || item.id.toString().includes(termo)
            );

            renderizarTabela(filtrados);
        });
    }

    // Criar novo forecast
    if (botaoCriar) {
        botaoCriar.addEventListener('click', function (e) {
            e.preventDefault();

            fetch('/cria_forecast_mes')
                .then(response => response.json())
                .then(data => {
                    if (data) {
                        alert(data.mensagem || data.erro || "Operação concluída.");
                    }
                })
                .catch(error => {
                    console.error("Erro ao criar Forecast:", error);
                    alert("Erro ao criar Forecast.");
                });
        });
    }

    // Renderizar tabela e adicionar evento de duplo clique
    function renderizarTabela(dados) {
        tabela.innerHTML = '';

        console.log("FUNÇÃO CHAMADA! Dados recebidos:", dados);

        if (dados.length === 0) {
            const tr = document.createElement('tr');
            const td = document.createElement('td');
            td.colSpan = 3;
            td.textContent = 'Nenhum registro encontrado.';
            tr.appendChild(td);
            tabela.appendChild(tr);
            return;
        }

        dados.forEach(item => {
            const tr = document.createElement('tr');

            const tdId = document.createElement('td');
            tdId.textContent = item.id;

            const tdMes = document.createElement('td');
            tdMes.textContent = item.mes;

            const tdSeqMes= document.createElement('td');
            tdSeqMes.textContent = item.seqmes;

            const tdFechado = document.createElement('td');
            tdFechado.textContent = item.fechado === true ? "Fechado" : "Aberto";

            tr.appendChild(tdId);
            tr.appendChild(tdMes);
            tr.appendChild(tdSeqMes);
            tr.appendChild(tdFechado);

            tr.addEventListener('dblclick', () => {
                selecionarForecast(item);
            });

            tabela.appendChild(tr);
        });
    }

    //Selecionar forecast
    function selecionarForecast(forecast) {
        const modal = bootstrap.Modal.getInstance(document.getElementById('modalBuscaForecast'));
        if (modal) modal.hide();

        const inputMes = document.getElementById('inputMesSelecionado');
        const inputId = document.getElementById('inputIdForecast');

        if (inputMes) inputMes.value = forecast.mes;
        if (inputId) inputId.value = forecast.id;

        if (!forecast.mes || !forecast.mes.includes('/')) return;

        const [mesNome, ano] = forecast.mes.split('/');
        const mesesMap = {
            'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5, 'junho': 6,
            'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
        };

        const mesNumero = mesesMap[mesNome.toLowerCase()];
        const seqMes = forecast.seqmes;

        if (!mesNumero || !ano) return;

        const tituloPagina = document.getElementById('tituloPagina');
        if (tituloPagina) tituloPagina.textContent = `Forecast - ${mesNome}/${ano} - (Seq. ${seqMes})`;

        atualizarNomesMesesComBase(mesNumero, ano);

        window.location.href = `/?mes=${mesNumero}&ano=${ano}&seq=${seqMes}`;
    }

        document.querySelectorAll('.salvar-observacao').forEach(function (botao) {
        botao.addEventListener('click', function () {
            const box = this.closest('.observacao-box');
            const textarea = box.querySelector('textarea');
            const observacao = textarea.value.trim();

            const linha = this.closest('tr'); // sobe até a linha da tabela
            const colunas = linha.querySelectorAll('td');

            const idforecast = colunas[1].textContent.trim(); // primeira coluna
            const item = colunas[3].textContent.trim();        // segunda coluna

            if (!observacao || !idforecast || !item) {
                alert("Informe uma descrição para salvar.");
                return;
            }

            fetch(`/gravar-observacao?idforecast=${idforecast}&item=${item}&obs=${encodeURIComponent(observacao)}`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.Mesagem) {
                    alert( data.Mesagem);
                    textarea.value = '';
                } else {
                    alert("Erro: " + (data.erro || "Erro ao salvar a observação"));
                }
            })
            .catch(err => {
                console.error(err);
                alert("Erro na comunicação com o servidor.");
            });
        });
    });


        document.querySelectorAll('.input-qtd-comprada').forEach(function (input) {
            input.addEventListener('keydown', function (event) {
                if (event.key === 'Enter') {
                    const id = this.getAttribute('data-id');
                    const qtdComprada = this.value;

                    // Encontra a linha inteira
                    const row = this.closest('tr');
                    const cells = row.querySelectorAll('td');

                    // Constrói o corpo com os valores da linha
                    const body = {
                        vendaMes1: parseFloat(cells[3].innerText.trim()),
                        vendaMes2: parseFloat(cells[4].innerText.trim()),
                        vendaMes3: parseFloat(cells[5].innerText.trim()),
                        mesAtual: parseFloat(cells[6].innerText.trim()),
                        trimestre: parseFloat(cells[7].innerText.trim()),
                        semestre: parseFloat(cells[8].innerText.trim()),
                        estoqueAtual: parseFloat(cells[10].innerText.trim()),
                        estoqueSeg: parseFloat(cells[11].innerText.trim()),
                        leadTime: parseFloat(cells[12].innerText.trim()),
                        qtdComprada: parseFloat(qtdComprada)
                    };

                     fetch(`/atualizar_dados_itens_forecast/${id}`, {
                        method: 'PUT',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(body)
                    })

                    .then(response => {
                        if (response.ok) {
                            alert('Atualizado com sucesso!');
                        } else {
                            alert('Erro ao atualizar!');
                        }
                    })
                    .catch(error => {
                        console.error('Erro:', error);
                        alert('Erro na requisição');
                    });
                }
            });
        });


        function abrirModalObservacao(observacoes) {
            const container = document.getElementById('conteudoObservacao');

            if (observacoes.length === 0) {
                container.innerHTML = '<p class="text-muted">Sem observações</p>';
            } else {
                let tabela = `
                    <table class="table table-bordered table-striped">
                      <thead>
                        <tr>
                          <th>Data</th>
                          <th>Observação</th>
                        </tr>
                      </thead>
                      <tbody>
                `;

                observacoes.forEach(obs => {
                    tabela += `
                      <tr>
                        <td>${obs.dataObs}</td>
                        <td>${obs.observacao}</td>
                      </tr>
                    `;
                });

                tabela += `</tbody></table>`;
                container.innerHTML = tabela;
            }

            // Garante que o modal está instanciado
            let modal = bootstrap.Modal.getInstance(document.getElementById('modalObservacao'));
            if (!modal) {
                modal = new bootstrap.Modal(document.getElementById('modalObservacao'));
            }

            modal.show();
        }

        document.querySelectorAll('.btn-observacao-ver').forEach(btn => {
          btn.addEventListener('click', () => {
            const id = btn.getAttribute('data-id'); // esse sim existe no HTML

            // Mostra carregando no modal
            document.getElementById('conteudoObservacao').innerHTML = '<p class="text-muted">Carregando...</p>';

            // Faz a requisição ao servidor
            fetch(`/listar_observacoes/${id}`)
              .then(response => response.json())
              .then(data => {
                if (data.error) {
                  document.getElementById('conteudoObservacao').innerHTML = `<p class="text-danger">${data.error}</p>`;
                } else {
                  abrirModalObservacao(data);
                }
              })
              .catch(err => {
                document.getElementById('conteudoObservacao').innerHTML = '<p class="text-danger">Erro ao carregar observações.</p>';
                console.error(err);
              });
          });
        });

         if (btnAtualizar) {
          btnAtualizar.addEventListener("click", async () => {
            console.log("Botão Atualizar clicado!");
            // Feedback visual de carregamento
            btnAtualizar.disabled = true;
            const originalHTML = btnAtualizar.innerHTML;
            btnAtualizar.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Atualizando...`;
            status.innerHTML = `<span class="text-info"><i class="fas fa-sync-alt fa-spin"></i> Atualizando registros...</span>`;

            // Coleta os dados da tabela
            const linhas = document.querySelectorAll("tbody tr");
            const dados = Array.from(linhas).map(linha => ({
              idMesForecast: parseInt(linha.querySelector("td:nth-child(1)")?.innerText.trim(), 10),
              iddadosforecast: parseInt(linha.querySelector("td:nth-child(2)")?.innerText.trim(), 10),
              idprodutoprincipal: parseInt(linha.querySelector("td:nth-child(3)")?.innerText.trim(), 10)
            })).filter(d => d.idMesForecast && d.iddadosforecast && d.idprodutoprincipal);

            if (dados.length === 0) {
              status.innerHTML = `<span class="text-warning"><i class="fas fa-exclamation-triangle"></i> Nenhum dado encontrado para atualizar.</span>`;
              btnAtualizar.innerHTML = originalHTML;
              btnAtualizar.disabled = false;
              return;
            }

              console.log(dados);

            try {
              const resp = await fetch("/atualizar_dados", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(dados)
              });

              if (resp.ok) {
                status.innerHTML = `<span class="text-success"><i class="fas fa-check-circle"></i> ✅ Todos os registros foram atualizados com sucesso!</span>`;
              } else {
                const erro = await resp.json();
                status.innerHTML = `<span class="text-danger"><i class="fas fa-times-circle"></i> Erro: ${erro.erro || "Falha na atualização"}</span>`;
              }
            } catch (err) {
              console.error("Erro ao enviar:", err);
              status.innerHTML = `<span class="text-danger"><i class="fas fa-exclamation-circle"></i> ❌ Erro na comunicação com o servidor.</span>`;
            } finally {
              // Restaura o botão
              btnAtualizar.innerHTML = originalHTML;
              btnAtualizar.disabled = false;
            }
          });
         }

        const params = new URLSearchParams(window.location.search);
        const mesParam = params.get("mes");
        const anoParam = params.get("ano");

        if (mesParam && anoParam) {
            const nomesMeses = [
                "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
            ];
            const mesNome = nomesMeses[parseInt(mesParam)];

            const tituloPagina = document.getElementById("tituloPagina");
            if (tituloPagina && mesNome) {
                tituloPagina.textContent = `Forecast - ${mesNome}/${anoParam}`;
                document.title = `Forecast - ${mesNome}/${anoParam}`;
            }
        }


       function getForecastSelecionado() {
            const tabela = document.getElementById('tabelaForecast');
            if (!tabela) return null;

            const primeiraLinha = tabela.querySelector('tbody tr');
            if (!primeiraLinha) return null;

            const colunas = primeiraLinha.querySelectorAll('td');
            if (colunas.length < 2) return null;

            return {
                idMesForecast: parseInt(colunas[0].innerText.trim(), 10),
                seqmes: parseInt(colunas[colunas.length - 1].innerText.trim(), 10)
            };
        }


        if (bntFecharforecast) {
            bntFecharforecast.addEventListener('click', function () {

                const forecast = getForecastSelecionado();

                if (!forecast || isNaN(forecast.idMesForecast) || isNaN(forecast.seqmes)) {
                    Swal.fire('Erro', 'Não foi possível identificar o Forecast selecionado.', 'error');
                    return;
                }

                Swal.fire({
                    title: 'Fechar Forecast',
                    text: `Deseja realmente fechar o Forecast (Seq. ${forecast.seqmes})?`,
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'Sim, fechar',
                    cancelButtonText: 'Cancelar',
                    confirmButtonColor: '#dc3545'
                }).then((result) => {
                    if (result.isConfirmed) {

                        fetch("/fecharforecast", {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json"
                            },
                            body: JSON.stringify({
                                idMesForecast: forecast.idMesForecast,
                                seqmes: forecast.seqmes
                            })
                        })
                        .then(response => {
                            if (!response.ok) throw new Error();
                            Swal.fire('Sucesso', 'Forecast fechado com sucesso!', 'success');
                        })
                        .catch(() => {
                            Swal.fire('Erro', 'Erro ao fechar forecast', 'error');
                        });
                    }
                });
            });
        }

    document.addEventListener("click", function (e) {

        if (!e.target.classList.contains("toggle-colunas")) return;

        const grupo = e.target.dataset.group;
        const expandido = e.target.dataset.expandido === "true";

        // pega todos os TH do grupo (exceto o primeiro)
        const colunasGrupo = document.querySelectorAll(`th[data-group="${grupo}"]`);

        colunasGrupo.forEach((th, index) => {

            if (index === 0) return; // não mexe na primeira coluna

            const colIndex = Array.from(th.parentNode.children).indexOf(th) + 1;

            // alterna cabeçalho
            if (expandido) {
                th.classList.add("oculta-coluna");
            } else {
                th.classList.remove("oculta-coluna");
            }

            // alterna células
            document.querySelectorAll(`#tabelaForecast tbody tr td:nth-child(${colIndex})`)
                .forEach(td => {
                    if (expandido) {
                        td.classList.add("oculta-coluna");
                    } else {
                        td.classList.remove("oculta-coluna");
                    }
                });

        });

        // controla estado
        e.target.dataset.expandido = (!expandido).toString();
        e.target.textContent = expandido ? "▼" : "▲";

    });



});
