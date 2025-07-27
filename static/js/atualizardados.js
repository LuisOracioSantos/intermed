window.onload = function () {
  window.atualizarDados = function () {
    const loading = document.getElementById("loading");
    const msgBox = document.getElementById("mensagem");

    // Mostra o loading
    loading.classList.remove("d-none");
    msgBox.classList.add("d-none");

    fetch("/atualizarRegistros")
      .then((response) => response.json())
      .then((data) => {
        loading.classList.add("d-none"); // esconde loading
        msgBox.classList.remove("d-none", "alert-danger");
        msgBox.classList.add("alert-success");
        msgBox.innerText = data.mensagem;

        setTimeout(() => {
          msgBox.classList.add("d-none");
        }, 5000);
      })
      .catch((error) => {
        loading.classList.add("d-none"); // esconde loading
        msgBox.classList.remove("d-none", "alert-success");
        msgBox.classList.add("alert-danger");
        msgBox.innerText = "Erro ao atualizar os registros.";

        setTimeout(() => {
          msgBox.classList.add("d-none");
        }, 5000);
      });
  };
};