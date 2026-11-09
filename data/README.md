# Dados

## `raw/`: dados originais
| Arquivo | Origem | Observação |
|---|---|---|
| `raw/bcb/fraudes_med.json` | Banco Central, API Olinda, `EstatisticasFraudesPix` | MED, total nacional por mês, jan/2022 em diante. Gerado por `src/baixar_bcb.py`. |
| `raw/bcb/transacoes_pix_agregado.csv` | Banco Central, API Olinda, `EstatisticasTransacoesPix` | Baixado mês a mês e somado por mês, tipo de pagador, região, faixa etária do pagador e natureza. Gerado por `src/baixar_bcb.py`. |
| `raw/anuario/*.xlsx` | Anuário Brasileiro de Segurança Pública (FBSP) | **Não versionado.** Veja `raw/anuario/LEIAME.md`. |

## `processed/`: tabelas geradas pelos scripts
| Arquivo | Conteúdo | Script |
|---|---|---|
| `estelionato_bruto.csv` | Todas as edições do Anuário, uma linha por UF, ano e edição | `extrair_anuario.py` |
| `estelionato_consolidado.csv` | Uma linha por UF e ano (edição mais recente), Brasil + 27 UFs | `extrair_anuario.py` |
| `pix_mensal.csv` | Transações e valor do Pix por mês | `processar_bcb.py` |
| `pix_faixa_etaria_mensal.csv` | Idem, por faixa etária do **pagador** (não da vítima) | `processar_bcb.py` |
| `med_mensal.csv` | Série do MED | `processar_bcb.py` |
| `painel_brasil_anual.csv` | Estelionato + Pix + MED por ano, com estelionato por milhão de Pix | `processar_bcb.py` |
| `resultados_*.csv` | Saídas de `analise.py` (variação por era e por UF) | `analise.py` |

## Dicionário: `estelionato_consolidado.csv`
| Coluna | Significado |
|---|---|
| `uf`, `ano` | Unidade da federação (ou "Brasil") e ano dos dados |
| `edicao`, `arquivo` | Edição do Anuário de onde veio o valor (a mais recente que traz o ano) |
| `estelionato` | Registros de estelionato (total, inclui fraude eletrônica a partir de 2021) |
| `estelionato_taxa_100mil` | Taxa por 100 mil habitantes |
| `eletronico`, `eletronico_taxa_100mil` | Estelionato por meio eletrônico (subconjunto do total). Vazio quando o estado não informou |
| `revisao_da_edicao_anterior` | `True` se o ano é uma atualização do que a edição anterior publicou |
| `notas_uf` | Números das notas de rodapé que se aplicam à UF naquela edição |

As ressalvas completas sobre estes dados estão no `README.md` da raiz.
