# Análise de golpes no Brasil: antes do Pix, Pix e Pix + IA

Pergunta: como evoluíram os golpes (estelionato) no Brasil depois do Pix, e o que mudou na era da IA generativa?

## Como este projeto foi feito

A pergunta, o recorte (2018 em diante, as três eras), as decisões sobre quais fontes usar e a interpretação são de Gustavo Rodrigues Lopes. O código de download, extração e análise, o site e este README foram escritos com o apoio do **Claude Code** (IA da Anthropic), com revisão do autor.

## Site interativo

A pasta `site/` é um site estático (HTML, CSS e JS, com Chart.js) que permite explorar o estelionato por estado, comparar com o Brasil e ver os dados do Pix e do MED. Os dados do site vêm de `site/dados.json`, gerado por `src/gerar_site.py`.

- Para ver localmente: `cd site` e `python -m http.server 8000`, depois abra `http://localhost:8000`.
- Para publicar na Vercel: crie um projeto apontando para este repositório com o **Root Directory** em `site` (sem build), e associe o subdomínio desejado.

## Estado atual

| Etapa | Status |
|---|---|
| Coleta dos dados (Anuário FBSP e BCB) | feita |
| Extração e consolidação (`src/`) | feita e validada |
| Site interativo (`site/`) | pronto |
| Análise estatística mais aprofundada | a fazer |

## Estrutura

```
data/raw/anuario/       xlsx originais do Anuário (NÃO versionados; veja o LEIAME da pasta)
data/raw/bcb/           dados do Banco Central (API Olinda)
data/processed/         tabelas limpas geradas pelos scripts (veja data/README.md)
src/baixar_bcb.py       baixa Pix e MED do Banco Central
src/extrair_anuario.py  estelionato por UF e ano, a partir dos xlsx
src/processar_bcb.py    Pix, MED e painel anual do Brasil
src/analise.py          resultados por era e por UF
src/gerar_site.py       gera os dados do site
site/                   site interativo (estático)
```

## Como reproduzir

1. `pip install -r requirements.txt`
2. Baixe os xlsx do Anuário e salve em `data/raw/anuario/` (instruções em `data/raw/anuario/LEIAME.md`).
3. `python src/baixar_bcb.py` (leva cerca de 15 minutos; use `--so-med` para baixar só o MED).
4. `python src/extrair_anuario.py`
5. `python src/processar_bcb.py`
6. `python src/analise.py` e `python src/gerar_site.py`

Os arquivos já tratados estão em `data/processed/`, então dá para explorar sem rodar nada.

## Fontes

- **Anuário Brasileiro de Segurança Pública (FBSP)**, tabela "Estelionato e Estelionato por meio eletrônico" (Brasil + 27 UFs). Cobre **2018 a 2025**, vindo das edições 16 a 20.
- **BCB, Estatísticas de transações Pix** (`EstatisticasTransacoesPix`): quantidade e valor por mês, de nov/2020 a out/2026. Serve de denominador.
- **BCB, Estatísticas de fraudes Pix / MED** (`EstatisticasFraudesPix`): contestações por suspeita de fraude, de **jan/2022 a set/2026**, só total nacional.

Recorte da análise: **2018 em diante**. Antes disso o Anuário não tem estelionato por UF (ver abaixo), e misturar outra fonte quebraria a série.

## Inconsistências e fatos que precisam constar no trabalho

### Arquivos do Anuário

1. **O número no nome do arquivo não é o ano dos dados.** O nome vem da edição no site. O que vale é o conteúdo:

   | Arquivo | Edição | Dados da tabela de estelionato |
   |---|---|---|
   | anuario-2022 (e anuario-2016) | 16ª | 2018-2021 |
   | anuario-2023 | 17ª | 2021-2022 |
   | anuario-2024 | 18ª | 2022-2023 |
   | anuario-2025 | 19ª | 2023-2024 |
   | anuario-2026 | 20ª | 2024-2025 |

2. **`anuario-2016.xlsx` é cópia idêntica de `anuario-2022.xlsx`** (mesmo hash MD5). Só a segunda é usada.
3. **Os arquivos `anuario-2018` a `anuario-2021` (edições 12ª a 15ª) não têm tabela de estelionato.** Não fazem falta, porque a 16ª edição já cobre 2018-2021.
4. **Os PDFs (`anuario-2015`, `anuario-2017`) não servem.** Estelionato aparece só em tabelas isoladas de 1 a 3 estados (SP em 2017; PA e DF em 2015), sem série nacional. **O Anuário não permite medir estelionato por UF antes de 2018.**

### Revisões de números

5. **A primeira coluna de cada edição é uma revisão do ano anterior** (nota "Atualização das informações publicadas no Anuário anterior"). Por isso o mesmo ano muda de valor entre edições. Exemplo, Brasil 2021: 1.265.073 (16ª ed.) → 1.312.964 (17ª ed.). Na tabela consolidada vale **sempre a edição mais recente** que traz o ano. Os valores originais ficam em `estelionato_bruto.csv`.
6. A edição 20 marca "2024 (5)", mas a nota (5) **não existe no arquivo**. Pelos números é uma revisão: o Brasil 2024 passou de 2.166.552 (19ª) para 2.193.122 (20ª). Foi tratada como revisão, não como quebra de metodologia. Vale confirmar com o FBSP se for citar.

### Mudanças de definição ao longo da série

7. **Lei 14.155/2021:** a partir de 2021, o estelionato (art. 171 do CP) **passou a incluir a fraude eletrônica**. A coluna "Estelionato" é, portanto, o total (comum + eletrônico), e "Estelionato por meio eletrônico" é um **subconjunto**, não uma soma.
8. **A "era Pix" começa junto com a pandemia (2020) e com a nova lei (2021).** O salto de 2019 para 2021 (524 mil → 1,31 milhão no Brasil) não pode ser atribuído só ao Pix.

### Lacunas e quebras por UF

9. **Estelionato por meio eletrônico tem muitos valores ausentes** (`NaN`) em vários estados e anos. Ceará, Rio de Janeiro e São Paulo ficam sem dado de eletrônico em **todos** os anos (2018-2025), e São Paulo é o maior estado. O total Brasil dessa coluna **subestima** a realidade e não é totalmente comparável entre anos. A série de "estelionato total" é bem mais completa. Para listar os vazios: `estelionato_consolidado.csv`, linhas com `eletronico` vazio.
10. **Maranhão** não informou estelionato em 2018 e 2019.
11. **Amapá 2018-2019:** os números são só da capital (nota 3 da 16ª ed.).
12. **Pará:** na 19ª ed., o eletrônico de 2023 caiu de 16.884 para 1.686 por mudança de metodologia. Há quebra de série nessa UF.
13. **Rio Grande do Sul:** eletrônico só passou a ser registrado em 27/07/2023, então 2023 cobre cerca de 5 meses.
14. **Pernambuco:** fraude eletrônica só passou a ser contada a partir de dez/2024.
15. **Pará (16ª ed.):** os dados incluem registros da delegacia virtual sem supervisão e podem ter sobrenotificação por duplicidade.
16. **São Paulo** registra casos tentados e consumados juntos (nota 7 da 16ª ed.; nota 4 da 17ª). Pode haver diferença de critério entre estados.
17. **Espírito Santo e Rondônia (16ª ed.):** em alguns campos não distinguem estelionato comum de eletrônico (nota 5).
18. A população usada nas taxas por 100 mil muda entre edições (estimativas do IBGE nas antigas, Censo 2022 nas recentes). Isso afeta as taxas, não os números absolutos.

### Dados do BCB

19. **O MED só existe na API a partir de jan/2022** (e não dez/2021). Antes disso não há série de fraudes no Pix.
20. **O MED é nacional e sem tipo de golpe.** Não dá para cruzar por UF nem por modalidade.
21. **"Contestados" não é igual a "golpes".** O número de Pix contestados cresceu muito (2,1 mi em 2022 → 22,2 mi em 2025), mas as contestações *aceitas* ficaram entre 1,6 mi e 4,9 mi. Use as aceitas como medida mais próxima de fraude confirmada e explique a escolha.
22. As transações Pix **não incluem** Pix liquidados dentro da própria instituição (fora do SPI). O denominador é, portanto, um pouco menor que o total real.
23. **2020 tem só 2 meses de Pix** (nov e dez) e **2026 vai só até out**. Por isso `estelionato_por_milhao_pix` só é calculado para anos completos (2021-2025).
24. A API usa `Database` como **mês inicial**, não como filtro de um mês, e `$skip` não funciona. Os dados foram baixados mês a mês com `$filter`. O arquivo `transacoes_pix_agregado.csv` já soma as linhas por mês, tipo de pagador, região, **faixa etária do pagador** e natureza.

### O que os dados NÃO medem

25. **Nenhum dado separa golpe por meio de pagamento** (dinheiro, Pix, boleto). O Anuário classifica por crime, não por meio. A comparação "dinheiro vs Pix" só aparece de forma indireta, pela coluna eletrônico e pelo MED.
26. **A faixa etária do BCB é do pagador (usuário do Pix), não da vítima.** Mostra quem usa o Pix, não quem cai em golpe.
27. **Nenhum dado diz se houve uso de IA.** A "era IA" é um corte temporal (a partir de 2023), definido antes de ver os dados. Mostra correlação, não causa.
28. **Subnotificação:** os dados são de boletins de ocorrência, e nem todo golpe vira BO.
29. **O "antes do Pix" tem só 2 anos (2018-2019).** A tendência de base é fraca. Use taxas por 100 mil habitantes e trate o resultado como indício.

## Eras da análise

| Era | Período | Dados disponíveis |
|---|---|---|
| Pré-Pix | 2018-2019 | Anuário |
| Transição | 2020 | Anuário (Pix só em nov/dez) |
| Pix | 2021-2022 | Anuário, Pix, MED (2022) |
| Pix + IA | 2023-2025 | Anuário, Pix, MED |

## Tabelas geradas (`data/processed/`)

| Arquivo | Conteúdo |
|---|---|
| `estelionato_bruto.csv` | todas as edições, uma linha por UF/ano/edição |
| `estelionato_consolidado.csv` | uma linha por UF/ano (edição mais recente); Brasil + 27 UFs por ano |
| `pix_mensal.csv` | transações e valor do Pix por mês |
| `pix_faixa_etaria_mensal.csv` | idem, por faixa etária do pagador |
| `med_mensal.csv` | série do MED |
| `painel_brasil_anual.csv` | estelionato + Pix + MED por ano, com estelionato por milhão de Pix |

Validação feita: a soma das 27 UFs bate com o total Brasil em todos os anos (2018-2025).
