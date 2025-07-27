document.addEventListener('DOMContentLoaded', function () {
      const modal = document.getElementById('modalDetalhes');
      modal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const codigo = button.getAttribute('data-codigo');
        const cliente = button.getAttribute('data-cliente');

        document.getElementById('clienteNome').innerText = cliente;

        fetch(`/getDadosVendaClienteId/${codigo}`)
          .then(response => response.json())
          .then(data => {
            const tabela = document.getElementById('tabelaProdutos');
            tabela.innerHTML = ''; // limpa
            data.forEach(produto => {
              tabela.innerHTML += `
                <tr>
                  <td>${produto.item}</td>
                  <td>${produto.descricao}</td>
                  <td>${produto.qtdVendida}</td>
                  <td>R$ ${produto.totalVendido} </td>
                  <td>${produto.ultimavenda}</td>
                </tr>
              `;
            });
          });
      });
    });