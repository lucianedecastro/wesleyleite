function registrarTreinoMar() {
  var resposta = prompt("Realizou treino no mar hoje? (sim/não)");
  if (resposta.toLowerCase() === "sim") {
    // Enviar dados para o servidor usando AJAX
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/registrar-treino-mar"); 
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("data=" + new Date().toISOString()); // Enviar data do treino

    // Mostrar mensagem após resposta do servidor
    xhr.onload = function() {
      if (xhr.status === 200) {
        mostrarMensagem("Treino no mar registrado com sucesso.");
      } else {
        mostrarMensagem("Erro ao registrar treino no mar.");
      }
    };
  } else {
    // Enviar dados para o servidor usando AJAX
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/registrar-treino-mar"); 
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("data=" + prompt("Descreva o treino no mar:")); // Enviar descrição do treino

    // Mostrar mensagem após resposta do servidor
    xhr.onload = function() {
      if (xhr.status === 200) {
        mostrarMensagem("Treino no mar registrado com sucesso.");
      } else {
        mostrarMensagem("Erro ao registrar treino no mar.");
      }
    };
  }
}

function registrarTreinoAcademia() {
  var resposta = prompt("Realizou treino na academia hoje? (sim/não)");
  if (resposta.toLowerCase() === "sim") {
    // Enviar dados para o servidor usando AJAX
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/registrar-treino-academia"); 
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("data=" + new Date().toISOString()); // Enviar data do treino

    // Mostrar mensagem após resposta do servidor
    xhr.onload = function() {
      if (xhr.status === 200) {
        mostrarMensagem("Treino na academia registrado com sucesso.");
      } else {
        mostrarMensagem("Erro ao registrar treino na academia.");
      }
    };
  } else {
    // Enviar dados para o servidor usando AJAX
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/registrar-treino-academia"); 
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send("data=" + prompt("Descreva o treino na academia:")); // Enviar descrição do treino

    // Mostrar mensagem após resposta do servidor
    xhr.onload = function() {
      if (xhr.status === 200) {
        mostrarMensagem("Treino na academia registrado com sucesso.");
      } else {
        mostrarMensagem("Erro ao registrar treino na academia.");
      }
    };
  }
}

function adicionarInformacoesEtapa() {
  var etapa = prompt("Digite o número da etapa (1-4):");
  var nota = prompt("Digite a nota:");
  var colocacao = prompt("Digite a colocação:");
  if (etapa.length > 0 && !isNaN(etapa) && etapa >= 1 && etapa <= 4 && 
      nota.length > 0 && !isNaN(nota) && 
      colocacao.length > 0 && !isNaN(colocacao)) {
    // Enviar dados para o servidor usando AJAX
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/adicionar-informacoes-etapa"); 
    xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    xhr.send(`etapa=${etapa}¬a=${nota}&colocacao=${colocacao}`);

    // Mostrar mensagem após resposta do servidor
    xhr.onload = function() {
      if (xhr.status === 200) {
        mostrarMensagem("Informações da etapa registradas com sucesso.");
      } else {
        mostrarMensagem("Erro ao registrar informações da etapa.");
      }
    };
  } else {
    mostrarMensagem("Dados inválidos.");
  }
}

function obterPrognostico() {
  // Enviar dados para o servidor usando AJAX
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/obter-prognostico"); 
  xhr.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhr.send();

  // Mostrar mensagem após resposta do servidor
  xhr.onload = function() {
    if (xhr.status === 200) {
      mostrarMensagem("Prognóstico: " + xhr.responseJSON.prognostico); 
    } else {
      mostrarMensagem("Erro ao obter prognóstico.");
    }
  };
}

function sair() {
  // Implementar lógica para sair
  window.close();
}

// Exemplo de como atualizar o conteúdo da div #conteudo:
function mostrarMensagem(mensagem) {
  document.getElementById("conteudo").innerHTML = mensagem;
}