# Arquivos do Anuário (não versionados)

Os xlsx do **Anuário Brasileiro de Segurança Pública** (Fórum Brasileiro de Segurança Pública, FBSP) não estão no repositório: são pesados (cerca de 30 MB) e pertencem ao FBSP. Baixe as planilhas no site do FBSP (forumseguranca.org.br, página do Anuário) e salve **nesta pasta** com estes nomes:

| Arquivo | Edição do Anuário | Dados da tabela de estelionato | Usado? |
|---|---|---|---|
| `anuario-2022.xlsx` | 16ª (publicada em 2022) | 2018–2021 | sim |
| `anuario-2023.xlsx` | 17ª | 2021–2022 | sim |
| `anuario-2024.xlsx` | 18ª | 2022–2023 | sim |
| `anuario-2025.xlsx` | 19ª | 2023–2024 | sim |
| `anuario-2026.xlsx` | 20ª | 2024–2025 | sim |

O número no nome do arquivo é a edição como aparece no site, **não** o ano dos dados. Confira o número da edição no índice de cada planilha ("ÍNDICE - 16º ANUÁRIO...").

As edições 12ª a 15ª não têm tabela de estelionato, e os PDFs das edições mais antigas (2015 e 2017) só trazem estelionato de poucos estados. Não são necessários.

A tabela usada fica na aba `T15` (edições 16, 17 e 18), `T19` (19ª) e `T17` (20ª), com o título "Estelionato e Estelionato por meio eletrônico".

Depois de salvar os arquivos: `python src/extrair_anuario.py`.
