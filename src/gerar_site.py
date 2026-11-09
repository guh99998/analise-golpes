"""Gera os dados do site (site/dados.json e site/dados/*.csv) a partir de data/processed/.

Uso:  python src/gerar_site.py   (depois de extrair_anuario.py e processar_bcb.py)
"""
import json
import shutil
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
P = RAIZ / "data" / "processed"
SITE = RAIZ / "site"


def lista(s):
    return [None if pd.isna(v) else round(float(v), 2) for v in s]


def main():
    (SITE / "dados").mkdir(parents=True, exist_ok=True)
    c = pd.read_csv(P / "estelionato_consolidado.csv")
    anos = sorted(c.ano.unique().tolist())

    ufs = {}
    for uf, g in c.groupby("uf"):
        g = g.set_index("ano").reindex(anos)
        ufs[uf] = {
            "estelionato": lista(g.estelionato),
            "taxa": lista(g.estelionato_taxa_100mil),
            "eletronico": lista(g.eletronico),
            "taxa_eletronico": lista(g.eletronico_taxa_100mil),
            "notas": sorted({n for s in g.notas_uf.dropna() for n in str(s).split(",")}),
        }

    pn = pd.read_csv(P / "painel_brasil_anual.csv").set_index("ano").reindex(anos)
    painel = {
        "pix_transacoes": lista(pn.pix_transacoes),
        "estelionato_por_milhao_pix": lista(pn.estelionato_por_milhao_pix),
        "med_contestados": lista(pn.med_contestados),
        "med_aceitos": lista(pn.med_contestacoes_aceitas),
        "med_valor_aceitos": lista(pn.med_valor_aceitos),
    }
    out = {"anos": anos, "ufs": ufs, "painel": painel}
    json.dump(out, open(SITE / "dados.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))

    # CSVs para download
    for nome in ["estelionato_consolidado.csv", "estelionato_bruto.csv",
                 "painel_brasil_anual.csv", "med_mensal.csv", "pix_mensal.csv"]:
        shutil.copy(P / nome, SITE / "dados" / nome)
    print("site/dados.json:", (SITE / "dados.json").stat().st_size, "bytes;", len(ufs), "entidades")


if __name__ == "__main__":
    main()
