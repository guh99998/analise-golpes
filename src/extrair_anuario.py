"""Extrai a tabela "Estelionato e Estelionato por meio eletrônico" (Brasil e UFs)
de cada edição do Anuário Brasileiro de Segurança Pública (xlsx).

Gera:
  data/processed/estelionato_bruto.csv        -> todas as edições, sem escolher nada
  data/processed/estelionato_consolidado.csv  -> 1 linha por UF/ano (edição mais recente)

Uso:  python src/extrair_anuario.py
"""
import re
from pathlib import Path

import numpy as np
import openpyxl
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
RAW = RAIZ / "data" / "raw" / "anuario"
OUT = RAIZ / "data" / "processed"

# arquivo -> (edição do Anuário, aba com a tabela de estelionato)
# O número no nome do arquivo é a edição "ano" do site, NÃO o ano dos dados.
EDICOES = {
    "anuario-2022.xlsx": (16, "T15"),  # dados 2018-2021 (anuario-2016.xlsx é cópia idêntica)
    "anuario-2023.xlsx": (17, "T15"),  # dados 2021-2022
    "anuario-2024.xlsx": (18, "T15"),  # dados 2022-2023
    "anuario-2025.xlsx": (19, "T19"),  # dados 2023-2024
    "anuario-2026.xlsx": (20, "T17"),  # dados 2024-2025
}


def num(v):
    """Converte célula em float; '...', '-' e vazio viram NaN."""
    if isinstance(v, (int, float)):
        return float(v)
    return np.nan


def limpa_nome(txt):
    notas = re.findall(r"\((\d+)\)", txt)
    nome = re.sub(r"\s*\(\d+\)", "", txt).strip()
    return nome, ",".join(notas)


def le_edicao(arquivo, edicao, aba):
    ws = openpyxl.load_workbook(RAW / arquivo, read_only=True, data_only=True)[aba]
    linhas = [list(r) for r in ws.iter_rows(values_only=True)]

    # linha de anos: contém células como 2021, '2021 (3)'
    ih = next(
        i for i, r in enumerate(linhas)
        if sum(1 for c in r if re.fullmatch(r"20\d\d( \(\d+\))?", str(c).strip() if c else "")) >= 4
    )
    cab = linhas[ih]
    col0 = next(j for j, c in enumerate(cab) if c is not None)
    anos, notas_ano = [], []
    for c in cab[col0:]:
        if c is None:
            continue
        m = re.match(r"(20\d\d)(?: \((\d+)\))?", str(c).strip())
        if m:
            anos.append(int(m.group(1)))
            notas_ano.append(m.group(2) or "")
    n = len(anos) // 4  # nº de anos por bloco (abs, taxa, abs_ele, taxa_ele)
    anos_bloco, notas_bloco = anos[:n], notas_ano[:n]

    # coluna do nome = a coluna anterior à primeira coluna de dado
    regs = []
    for r in linhas[ih + 1:]:
        nome_raw = next((c for c in r if isinstance(c, str)), None)
        if nome_raw is None:
            continue
        if nome_raw.startswith("Fonte"):
            break
        vals = [c for c in r[r.index(nome_raw) + 1:]]
        # tira colunas vazias do começo (células mescladas), mantém posições
        while vals and vals[0] is None:
            vals.pop(0)
        if not any(isinstance(v, (int, float)) for v in vals):
            continue
        nome, notas_uf = limpa_nome(nome_raw)
        # layout: abs[n] taxa[n] var[1] | abs_ele[n] taxa_ele[n] var_ele[1]
        v = [num(x) for x in vals]
        v += [np.nan] * (4 * n + 2 - len(v))
        for k, ano in enumerate(anos_bloco):
            regs.append({
                "edicao": edicao, "arquivo": arquivo, "uf": nome, "ano": ano,
                "estelionato": v[k],
                "estelionato_taxa_100mil": v[n + k],
                "eletronico": v[2 * n + 1 + k],
                "eletronico_taxa_100mil": v[3 * n + 1 + k],
                "revisao_da_edicao_anterior": notas_bloco[k] != "",  # nota no cabeçalho do ano = valor atualizado
                "notas_uf": notas_uf,
            })
    return pd.DataFrame(regs)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    bruto = pd.concat([le_edicao(a, e, s) for a, (e, s) in EDICOES.items()], ignore_index=True)
    bruto.to_csv(OUT / "estelionato_bruto.csv", index=False, encoding="utf-8")

    # consolidado: para cada UF/ano, vale a edição mais recente (traz a revisão dos números)
    cons = bruto.sort_values("edicao").drop_duplicates(["uf", "ano"], keep="last")  # linha inteira, sem misturar edições
    cons = cons.sort_values(["uf", "ano"])
    cons.to_csv(OUT / "estelionato_consolidado.csv", index=False, encoding="utf-8")
    print(f"bruto: {len(bruto)} linhas | consolidado: {len(cons)} linhas")


if __name__ == "__main__":
    main()
