function validarFormulario() {
  var email = document.getElementById('utilizador').value;
  var senha = document.getElementById('password').value;
  var confirmarSenha = document.getElementById('confirm-password').value;
  var aviso = document.getElementById('aviso');
  var campoVazio = document.getElementById('campo-vazio');

  if (email === "" || senha === "" || confirmarSenha === "") {
      campoVazio.style.display = 'block'; //Aviso de campo vazio
      return false; //Impede o envio do formulário
  } else {
      campoVazio.style.display = 'none'; //Esconde o aviso de campo vazio
  }

  // Verifica se a palavra passe são iguais
  if (senha !== confirmarSenha) {
      aviso.style.display = 'block'; //Aviso se as palavras passes não coincidirem
      return false; //Impede o envio do formulário
  } else {
      aviso.style.display = 'none'; //Esconde o aviso se as senhas coincidirem
      return true; //Permite o envio do formulário
  }
}
