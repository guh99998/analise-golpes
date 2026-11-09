"""Calcula os resultados principais e salva data/processed/resultados_*.csv"""
from pathlib import Path
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
P = RAIZ / "data" / "processed"
ERA = {2018: "Pré-Pix", 2019: "Pré-Pix", 2020: "Transição", 2021: "Pix", 2022: "Pix",
       2023: "Pix + IA", 2024: "Pix + IA", 2025: "Pix + IA"}

c = pd.read_csv(P / "estelionato_consolidado.csv")
br = c[c.uf == "Brasil"].set_index("ano")
pn = pd.read_csv(P / "painel_brasil_anual.csv").set_index("ano")

# 1) Brasil por era: média anual da taxa por 100 mil
t = br[["estelionato", "estelionato_taxa_100mil", "eletronico", "eletronico_taxa_100mil"]].copy()
t["era"] = t.index.map(ERA)
t["var_ano_%"] = t.estelionato.pct_change() * 100
t["eletronico_%_do_total"] = t.eletronico / t.estelionato * 100
print(t.round(1).to_string())
era = t.groupby("era", sort=False).estelionato_taxa_100mil.mean().round(1)
print("\nTaxa média por 100 mil, por era:\n", era.to_string())

# 2) por UF: variação 2019 -> 2025 da taxa por 100 mil (exclui UFs sem dado)
u = c[c.uf != "Brasil"].pivot(index="uf", columns="ano", values="estelionato_taxa_100mil")
u["mult_2019_2025"] = u[2025] / u[2019]
print("\nUFs: taxa 2019, 2025, multiplicador 2019->2025")
print(u[[2019, 2025, "mult_2019_2025"]].sort_values("mult_2019_2025", ascending=False).round(1).to_string())
u.to_csv(P / "resultados_uf_taxa.csv")

# 3) Pix e MED
print("\nPainel Pix/MED:")
print(pn[["pix_transacoes", "estelionato_por_milhao_pix", "med_contestados",
          "med_contestacoes_aceitas", "med_valor_aceitos"]].dropna(how="all").round(1).to_string())
t.to_csv(P / "resultados_brasil_era.csv")
