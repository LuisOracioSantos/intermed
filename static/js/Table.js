

document.addEventListener('DOMContentLoaded', function () {
    // Modal observação
    const modal = document.getElementById('modalObservacao');
    if (modal) {
        modal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const observacao = button.getAttribute('data-observacao') || 'Sem observação';
            document.getElementById('conteudoObservacao').innerText = observacao;
        });
    }

    // Filtro da tabela
    const filtroInput = document.getElementById('filtroTabela');
    if (filtroInput) {
        filtroInput.addEventListener('input', function () {
            const filtro = this.value.toLowerCase();
            const linhas = document.querySelectorAll('table tbody tr');

            linhas.forEach(linha => {
                const textoLinha = linha.innerText.toLowerCase();
                linha.style.display = textoLinha.includes(filtro) ? '' : 'none';
            });
        });
    }

    // Observação inline
    window.toggleObservacao = function (button) {
        const box = button.parentElement.querySelector('.observacao-box');
        box.classList.toggle('d-none');
    };
});
