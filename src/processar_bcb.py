"""Processa os dados do BCB (Pix) e monta o painel anual do Brasil.

Entradas (data/raw/bcb/):
  transacoes_pix_agregado.csv  -> EstatisticasTransacoesPix, agregado por mês/pagador/região/idade/natureza
  fraudes_med.json             -> EstatisticasFraudesPix (MED), total nacional por mês

Saídas (data/processed/):
  pix_mensal.csv, pix_faixa_etaria_mensal.csv, med_mensal.csv, painel_brasil_anual.csv

Uso:  python src/processar_bcb.py   (rode antes src/extrair_anuario.py)
"""
import json
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
RAW = RAIZ / "data" / "raw" / "bcb"
OUT = RAIZ / "data" / "processed"


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    tr = pd.read_csv(RAW / "transacoes_pix_agregado.csv")
    tr["ano"] = tr.AnoMes // 100
    pix_mes = tr.groupby("AnoMes", as_index=False)[["QUANTIDADE", "VALOR"]].sum()
    pix_mes.to_csv(OUT / "pix_mensal.csv", index=False)

    faixa = (tr.groupby(["AnoMes", "PAG_IDADE"], as_index=False)[["QUANTIDADE", "VALOR"]].sum())
    faixa.to_csv(OUT / "pix_faixa_etaria_mensal.csv", index=False)

    med = pd.DataFrame(json.load(open(RAW / "fraudes_med.json", encoding="utf-8"))["value"])
    med.to_csv(OUT / "med_mensal.csv", index=False)

    # ---- painel anual (Brasil): estelionato (Anuário) + Pix + MED
    est = pd.read_csv(OUT / "estelionato_consolidado.csv")
    est = est[est.uf == "Brasil"].set_index("ano")[
        ["estelionato", "estelionato_taxa_100mil", "eletronico", "eletronico_taxa_100mil"]]
    pix_ano = (pix_mes.assign(ano=pix_mes.AnoMes // 100).groupby("ano")
               .agg(pix_transacoes=("QUANTIDADE", "sum"), pix_valor=("VALOR", "sum"),
                    pix_meses_com_dado=("AnoMes", "count")))
    med["ano"] = med.AnoMes // 100
    med_ano = med.groupby("ano").agg(
        med_contestados=("QtdePixcontestados", "sum"),
        med_contestacoes_aceitas=("Qtdecontestacoesaceitas", "sum"),
        med_valor_aceitos=("ValorPixcontestadosaceitos", "sum"),
        med_meses_com_dado=("AnoMes", "count"))
    painel = est.join(pix_ano, how="left").join(med_ano, how="left")
    painel["estelionato_por_milhao_pix"] = painel.estelionato / painel.pix_transacoes * 1e6
    # só é comparável se o ano do Pix estiver completo (2020 tem 2 meses; 2026 vai só até out)
    painel.loc[painel.pix_meses_com_dado.fillna(0) < 12, "estelionato_por_milhao_pix"] = float("nan")
    painel.reset_index().to_csv(OUT / "painel_brasil_anual.csv", index=False)
    print(painel.round(2).to_string())


if __name__ == "__main__":
    main()
