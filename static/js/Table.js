

document.addEventListener('DOMContentLoaded', function () {

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
