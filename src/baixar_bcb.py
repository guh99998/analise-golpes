"""Baixa os dados do Banco Central (API Olinda, Pix_DadosAbertos) para data/raw/bcb/.

  - EstatisticasFraudesPix   -> fraudes_med.json              (MED, total nacional por mês)
  - EstatisticasTransacoesPix -> transacoes_pix_agregado.csv  (baixado mês a mês e somado)

Particularidades da API (descobertas na prática):
  * o parâmetro `Database` é o MÊS INICIAL (AAAAMM); a API devolve dali até o mais recente;
  * `$skip` não funciona (erro 500), e uma chamada devolve no máximo 100 mil linhas;
    por isso as transações são baixadas mês a mês com `$filter=AnoMes eq AAAAMM`;
  * cada mês de transações tem cerca de 2,4 MB em JSON, então o script soma
    por mês, tipo de pagador, região, faixa etária e natureza antes de salvar.

Uso:  python src/baixar_bcb.py              (tudo; leva uns 15 minutos)
      python src/baixar_bcb.py --so-med     (só o MED, é rápido)
"""
import argparse
import csv
import json
import time
import urllib.request
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RAW = RAIZ / "data" / "raw" / "bcb"
BASE = "https://olinda.bcb.gov.br/olinda/servico/Pix_DadosAbertos/versao/v1/odata"
INICIO = 202011  # o Pix foi lançado em 16/11/2020


def get(url, tentativas=3):
    for i in range(tentativas):
        try:
            return json.load(urllib.request.urlopen(url, timeout=300))["value"]
        except Exception:
            if i == tentativas - 1:
                raise
            time.sleep(3)


def baixar_med():
    url = (f"{BASE}/EstatisticasFraudesPix(Database=@d)?@d='{INICIO}'"
           "&%24format=json&%24top=100000")
    dados = get(url)
    RAW.mkdir(parents=True, exist_ok=True)
    json.dump({"value": dados}, open(RAW / "fraudes_med.json", "w", encoding="utf-8"))
    meses = sorted(x["AnoMes"] for x in dados)
    print(f"MED: {len(dados)} meses ({meses[0]} a {meses[-1]})")
    return meses[-1]


def baixar_transacoes(ultimo_mes):
    meses = [a * 100 + m for a in range(2020, 2028) for m in range(1, 13) if INICIO <= a * 100 + m <= ultimo_mes + 1]
    agg = defaultdict(lambda: [0.0, 0])
    for ym in meses:
        url = (f"{BASE}/EstatisticasTransacoesPix(Database=@d)?@d='{INICIO}'"
               f"&%24format=json&%24top=100000&%24filter=AnoMes%20eq%20{ym}")
        v = get(url)
        if not v:  # mês ainda não publicado
            continue
        if len(v) >= 100000:
            raise RuntimeError(f"{ym}: atingiu o limite de 100 mil linhas; dados truncados")
        for x in v:
            k = (x["AnoMes"], x["PAG_PFPJ"], x["PAG_REGIAO"], x["PAG_IDADE"], x["NATUREZA"])
            agg[k][0] += x["VALOR"] or 0
            agg[k][1] += x["QUANTIDADE"] or 0
        print(ym, len(v), flush=True)
    with open(RAW / "transacoes_pix_agregado.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["AnoMes", "PAG_PFPJ", "PAG_REGIAO", "PAG_IDADE", "NATUREZA", "VALOR", "QUANTIDADE"])
        for k, (valor, qtd) in sorted(agg.items(), key=lambda i: tuple(str(z) for z in i[0])):
            w.writerow([*k, round(valor, 2), int(qtd)])
    print(f"Transações: {len(agg)} linhas agregadas")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--so-med", action="store_true")
    args = ap.parse_args()
    ultimo = baixar_med()
    if not args.so_med:
        baixar_transacoes(ultimo)
