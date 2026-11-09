/* Golpes e Pix no Brasil: gráficos interativos. Dados em dados.json (gerado por src/gerar_site.py). */
(function () {
  "use strict";

  var ERAS = [
    { nome: "Pré-Pix", de: 2018, ate: 2019, cor: "--band-pre" },
    { nome: "Transição", de: 2020, ate: 2020, cor: "--band-trans" },
    { nome: "Pix", de: 2021, ate: 2022, cor: "--band-pix" },
    { nome: "Pix + IA", de: 2023, ate: 2025, cor: "--band-ia" }
  ];
  var fmt = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 });
  var fmt1 = new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1 });
  var estado = { uf: "Brasil", medida: "taxa", soEle: false, compBr: true };
  var dados, grafPrincipal, grafPix, grafMed;

  function css(v) { return getComputedStyle(document.documentElement).getPropertyValue(v).trim(); }
  function $(id) { return document.getElementById(id); }

  // Plugin: faixas coloridas por era no fundo do gráfico
  var faixasEras = {
    id: "faixasEras",
    beforeDatasetsDraw: function (chart) {
      var x = chart.scales.x, y = chart.scales.y, ctx = chart.ctx;
      var anos = chart.data.labels.map(Number);
      var passo = anos.length > 1 ? (x.getPixelForValue(1) - x.getPixelForValue(0)) : 40;
      ctx.save();
      ERAS.forEach(function (e) {
        var i0 = anos.indexOf(e.de), i1 = anos.indexOf(e.ate);
        if (i0 < 0 || i1 < 0) return;
        var xa = x.getPixelForValue(i0) - passo / 2, xb = x.getPixelForValue(i1) + passo / 2;
        ctx.fillStyle = css(e.cor);
        ctx.fillRect(Math.max(xa, x.left), y.top, Math.min(xb, x.right) - Math.max(xa, x.left), y.bottom - y.top);
        // nome da era no topo da faixa (a cor sozinha não identifica a era)
        ctx.fillStyle = css("--muted");
        ctx.font = '500 11px "JetBrains Mono", monospace';
        ctx.textAlign = "center";
        var largura = Math.min(xb, x.right) - Math.max(xa, x.left);
        if (ctx.measureText(e.nome).width + 8 <= largura) { // só escreve se couber; a legenda acima cobre o resto
          ctx.fillText(e.nome, (Math.max(xa, x.left) + Math.min(xb, x.right)) / 2, y.top + 14);
        }
      });
      ctx.restore();
    }
  };

  function base() {
    Chart.defaults.font.family = '"Inter", system-ui, sans-serif';
    Chart.defaults.font.size = 13;
    Chart.defaults.color = css("--muted");
  }

  function serie(uf, medida, ele) {
    var d = dados.ufs[uf];
    if (medida === "pix") return dados.painel.estelionato_por_milhao_pix;
    if (medida === "abs") return ele ? d.eletronico : d.estelionato;
    return ele ? d.taxa_eletronico : d.taxa;
  }

  function rotuloMedida() {
    return { taxa: "por 100 mil habitantes", abs: "registros", pix: "por milhão de transações Pix" }[estado.medida];
  }

  function desenhar() {
    base();
    var anos = dados.anos, uf = estado.uf, ds = [];
    var nomeSerie = (uf === "Brasil" ? "Brasil" : uf) + (estado.soEle && estado.medida !== "pix" ? " (eletrônico)" : "");
    ds.push({
      label: nomeSerie, data: serie(uf, estado.medida, estado.soEle),
      borderColor: css(estado.soEle ? "--alt" : "--accent"), backgroundColor: css(estado.soEle ? "--alt" : "--accent"),
      borderWidth: 3, pointRadius: 5, pointHoverRadius: 7, spanGaps: false, tension: 0.15
    });
    if (uf !== "Brasil" && estado.compBr && estado.medida !== "pix") {
      ds.push({
        label: "Brasil" + (estado.soEle ? " (eletrônico)" : ""), data: serie("Brasil", estado.medida, estado.soEle),
        borderColor: css("--muted"), backgroundColor: css("--muted"), borderWidth: 2, borderDash: [6, 5],
        pointRadius: 4, pointStyle: "rect", spanGaps: false, tension: 0.15
      });
    }
    var cfg = {
      type: "line", data: { labels: anos, datasets: ds },
      options: {
        responsive: true, maintainAspectRatio: false, interaction: { mode: "index", intersect: false },
        scales: {
          x: { grid: { display: false } },
          y: { beginAtZero: true, grid: { color: css("--line") }, ticks: { callback: function (v) { return fmt.format(v); } },
               title: { display: true, text: rotuloMedida() } }
        },
        plugins: {
          legend: { position: "bottom", labels: { usePointStyle: true, boxWidth: 10 } },
          tooltip: { callbacks: { label: function (c) {
            var v = c.parsed.y; return c.dataset.label + ": " + (v == null ? "sem dado" : fmt1.format(v)); } } }
        }
      },
      plugins: [faixasEras]
    };
    if (grafPrincipal) grafPrincipal.destroy();
    grafPrincipal = new Chart($("g-principal"), cfg);
    $("g-principal").setAttribute("aria-label", "Gráfico de " + nomeSerie + ", " + rotuloMedida() + ", 2018 a 2025");
    kpis(); tabela(); aviso();
  }

  function primeiroUltimo(arr) {
    var a = null, b = null, i;
    for (i = 0; i < arr.length; i++) if (arr[i] != null) { a = i; break; }
    for (i = arr.length - 1; i >= 0; i--) if (arr[i] != null) { b = i; break; }
    return [a, b];
  }

  // Razões só fazem sentido com base não desprezível (evita "3.228×" quando a base é ~0)
  function baseOk(v) {
    if (v == null) return false;
    var minimo = estado.medida === "abs" ? 500 : 5;
    return v >= minimo;
  }
  function pct(v) { return (v >= 0 ? "+" : "") + fmt.format(v * 100) + "%"; }

  function kpis() {
    var s = serie(estado.uf, estado.medida, estado.soEle), anos = dados.anos, pu = primeiroUltimo(s), h = "";
    if (pu[0] == null || pu[0] === pu[1]) { $("kpis").innerHTML = '<div class="kpi"><b>Sem série</b><span>Dados insuficientes para esta seleção.</span></div>'; return; }
    var v0 = s[pu[0]], v1 = s[pu[1]];
    if (baseOk(v0)) h += '<div class="kpi"><b>' + fmt1.format(v1 / v0) + '×</b><span>de ' + anos[pu[0]] + ' para ' + anos[pu[1]] + '</span></div>';
    else h += '<div class="kpi"><b>—</b><span>sem razão: o valor de ' + anos[pu[0]] + ' é pequeno demais para comparar</span></div>';
    h += '<div class="kpi"><b>' + fmt1.format(v0) + '</b><span>em ' + anos[pu[0]] + ' (' + rotuloMedida() + ')</span></div>';
    h += '<div class="kpi"><b>' + fmt1.format(v1) + '</b><span>em ' + anos[pu[1]] + '</span></div>';
    var iPix = anos.indexOf(2020), i25 = anos.indexOf(2025);
    if (baseOk(s[iPix - 1]) && s[iPix] != null) {
      h += '<div class="kpi"><b>' + pct(s[iPix] / s[iPix - 1] - 1) + '</b><span>variação em 2020 (pandemia, Pix só em nov e dez)</span></div>';
    }
    if (baseOk(s[i25 - 1]) && s[i25] != null) {
      h += '<div class="kpi"><b>' + pct(s[i25] / s[i25 - 1] - 1) + '</b><span>variação em 2025</span></div>';
    }
    $("kpis").innerHTML = h;
  }

  function aviso() {
    var uf = estado.uf, d = dados.ufs[uf], msgs = [];
    var s = serie(uf, estado.medida, estado.soEle), faltam = [];
    dados.anos.forEach(function (a, i) { if (s[i] == null) faltam.push(a); });
    if (estado.medida === "pix") msgs.push("Estelionato total (com e sem Pix) dividido pelas transações Pix. Não é a taxa de golpes dentro do Pix. Só há anos completos de Pix de 2021 a 2025.");
    else if (faltam.length) msgs.push("Sem dado informado para " + (uf === "Brasil" ? "o Brasil" : uf) + " em: " + faltam.join(", ") + (estado.soEle ? ". Vários estados não informam o estelionato eletrônico, então o total do Brasil subestima o fenômeno." : "."));
    if (d.notas.length && estado.medida !== "pix") msgs.push("Este estado tem notas de rodapé no Anuário (mudança de critério ou cobertura). Veja a metodologia.");
    if (uf !== "Brasil" && estado.medida !== "pix") msgs.push("Diferenças entre estados também refletem como cada um registra e classifica o crime.");
    $("aviso").textContent = msgs.join(" ");
  }

  function tabela() {
    var anos = dados.anos, d = dados.ufs[estado.uf], br = dados.ufs.Brasil;
    var cab = ["Ano", "Estelionato (" + (estado.medida === "abs" ? "registros" : "por 100 mil") + ")", "Eletrônico", "Brasil"];
    var h = "<thead><tr>" + cab.map(function (c) { return "<th scope='col'>" + c + "</th>"; }).join("") + "</tr></thead><tbody>";
    var ct = estado.medida === "abs" ? d.estelionato : d.taxa, ce = estado.medida === "abs" ? d.eletronico : d.taxa_eletronico;
    var cb = estado.medida === "abs" ? br.estelionato : br.taxa;
    anos.forEach(function (a, i) {
      function f(v) { return v == null ? "—" : fmt1.format(v); }
      h += "<tr><td>" + a + "</td><td>" + f(ct[i]) + "</td><td>" + f(ce[i]) + "</td><td>" + f(cb[i]) + "</td></tr>";
    });
    $("tabela").innerHTML = h + "</tbody>";
  }

  function simples(id, tipo, labels, datasets, fmtTick) {
    return new Chart($(id), {
      type: tipo, data: { labels: labels, datasets: datasets },
      options: {
        responsive: true, maintainAspectRatio: false,
        scales: { x: { grid: { display: false } }, y: { beginAtZero: true, grid: { color: css("--line") }, ticks: { callback: fmtTick } } },
        plugins: { legend: { display: datasets.length > 1, position: "bottom", labels: { usePointStyle: true, boxWidth: 10 } },
          tooltip: { callbacks: { label: function (c) { return c.dataset.label + ": " + fmt1.format(c.parsed.y); } } } }
      }
    });
  }

  function graficosPix() {
    var anos = dados.anos, p = dados.painel;
    var pixAnos = [], pixVals = [], medAnos = [], cont = [], ace = [];
    anos.forEach(function (a, i) {
      if (p.pix_transacoes[i] != null) { pixAnos.push(a); pixVals.push(p.pix_transacoes[i] / 1e9); }
      if (p.med_contestados[i] != null) { medAnos.push(a); cont.push(p.med_contestados[i] / 1e6); ace.push(p.med_aceitos[i] / 1e6); }
    });
    if (grafPix) grafPix.destroy();
    if (grafMed) grafMed.destroy();
    grafPix = simples("g-pix", "bar", pixAnos, [{ label: "Transações (bilhões)", data: pixVals, backgroundColor: css("--accent"), borderRadius: 6 }], function (v) { return fmt1.format(v); });
    grafMed = simples("g-med", "bar", medAnos, [
      { label: "Contestados", data: cont, backgroundColor: css("--muted"), borderRadius: 6 },
      { label: "Aceitos", data: ace, backgroundColor: css("--alt"), borderRadius: 6 }
    ], function (v) { return fmt1.format(v); });
  }

  function ligarControles() {
    var sel = $("uf"), nomes = Object.keys(dados.ufs).sort(function (a, b) {
      if (a === "Brasil") return -1; if (b === "Brasil") return 1; return a.localeCompare(b, "pt-BR");
    });
    sel.innerHTML = nomes.map(function (n) { return "<option>" + n + "</option>"; }).join("");
    sel.addEventListener("change", function () { estado.uf = sel.value; sincronizar(); desenhar(); });
    document.querySelectorAll("[data-medida]").forEach(function (b) {
      b.addEventListener("click", function () { estado.medida = b.dataset.medida; sincronizar(); desenhar(); });
    });
    $("ck-ele").addEventListener("change", function (e) { estado.soEle = e.target.checked; desenhar(); });
    $("ck-br").addEventListener("change", function (e) { estado.compBr = e.target.checked; desenhar(); });
  }

  function sincronizar() {
    var ehBr = estado.uf === "Brasil";
    // "por milhão de Pix" só existe para o Brasil
    $("btn-pix").disabled = !ehBr;
    if (!ehBr && estado.medida === "pix") estado.medida = "taxa";
    document.querySelectorAll("[data-medida]").forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.medida === estado.medida)); });
    $("ck-ele").disabled = estado.medida === "pix";
    $("ck-br").disabled = ehBr || estado.medida === "pix";
  }

  function iniciar() {
    fetch("dados.json").then(function (r) { return r.json(); }).then(function (d) {
      dados = d; ligarControles(); sincronizar(); desenhar(); graficosPix();
    }).catch(function () {
      $("aviso").textContent = "Não foi possível carregar os dados. Recarregue a página.";
    });
  }
  iniciar();
})();
