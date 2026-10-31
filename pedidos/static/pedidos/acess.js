(function () {
  var html = document.documentElement;
  var CHAVE = "atbd-acessibilidade";
  var estado = { tamanho: 0, contraste: false };
  var botaoContraste;

  try {
    var salvo = JSON.parse(localStorage.getItem(CHAVE));
    if (salvo) {
      estado.tamanho = Math.min(2, Math.max(0, salvo.tamanho | 0));
      estado.contraste = !!salvo.contraste;
    }
  } catch (e) {}

  var regras = [
    ".acess{display:flex;flex-wrap:wrap;gap:8px;justify-content:flex-end;padding:12px 0 0}",
    "html.texto-1 .tela{zoom:1.25}",
    "html.texto-2 .tela{zoom:1.5}",
    "html.alto-contraste body,html.alto-contraste .tela{background:#000 !important;color:#fff !important}",
    "html.alto-contraste .tela *{color:#fff !important}",
    "html.alto-contraste .marca,html.alto-contraste .hero h1{color:#FFD400 !important}",
    "html.alto-contraste .btn,html.alto-contraste .opcao,html.alto-contraste .item,html.alto-contraste .campo{background:#000 !important;border:2px solid #FFD400 !important}",
    "html.alto-contraste .campo{border-color:#fff !important}",
    "html.alto-contraste .btn.principal,html.alto-contraste .opcao.destaque{background:#FFD400 !important}",
    "html.alto-contraste .btn.principal,html.alto-contraste .opcao.destaque,html.alto-contraste .opcao.destaque *{color:#000 !important}",
    "html.alto-contraste .erro{background:#7A0000 !important;border-left-color:#fff !important}",
    "html.alto-contraste .aviso{background:#000 !important;border:2px solid #FFD400 !important}",
    "html.alto-contraste :focus-visible{outline:3px solid #00E5FF !important}"
  ].join("\n");
  var estilo = document.createElement("style");
  estilo.textContent = regras;
  document.head.appendChild(estilo);

  function aplicar() {
    html.classList.remove("texto-1", "texto-2");
    if (estado.tamanho > 0) html.classList.add("texto-" + estado.tamanho);
    html.classList.toggle("alto-contraste", estado.contraste);
    if (botaoContraste) {
      botaoContraste.setAttribute("aria-pressed", String(estado.contraste));
      botaoContraste.textContent = estado.contraste
        ? "Alto contraste: ligado"
        : "Alto contraste: desligado";
    }
    try {
      localStorage.setItem(CHAVE, JSON.stringify(estado));
    } catch (e) {}
  }

  function criarBotao(texto, rotulo, acao) {
    var b = document.createElement("button");
    b.type = "button";
    b.className = "btn";
    b.textContent = texto;
    b.setAttribute("aria-label", rotulo);
    b.addEventListener("click", acao);
    return b;
  }

  var barra = document.createElement("div");
  barra.className = "acess";
  barra.setAttribute("role", "group");
  barra.setAttribute("aria-label", "Recursos de acessibilidade");

  var menos = criarBotao("A−", "Diminuir o tamanho do texto", function () {
    estado.tamanho = Math.max(0, estado.tamanho - 1);
    aplicar();
  });
  var mais = criarBotao("A+", "Aumentar o tamanho do texto", function () {
    estado.tamanho = Math.min(2, estado.tamanho + 1);
    aplicar();
  });
  botaoContraste = criarBotao("", "Alternar o modo de alto contraste", function () {
    estado.contraste = !estado.contraste;
    aplicar();
  });

  barra.append(menos, mais, botaoContraste);
  var tela = document.querySelector(".tela");
  if (tela) tela.insertBefore(barra, tela.firstChild);
  aplicar();
})();