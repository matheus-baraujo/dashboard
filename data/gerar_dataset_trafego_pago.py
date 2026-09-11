"""
Gerador de dataset sintético de tráfego pago (Google Ads / Meta Ads).

Schema (uma linha = uma campanha em um dia):
    data, campanha_id, campanha_nome, canal, objetivo,
    dispositivo, segmento_publico,
    investimento, impressoes, cliques, ctr,
    conversoes, receita, cpc, cpa, roas

Ideia geral da simulação:
- Cada campanha tem um período de veiculação (flight) e um orçamento diário base.
- Impressões variam com o orçamento, dia da semana (fins de semana mais fracos
  para B2B, mais fortes para e-commerce/varejo) e uma leve tendência sazonal
  ao longo dos meses.
- O CTR começa num patamar "saudável" e sofre fadiga de criativo: cai aos
  poucos quanto mais dias a campanha está no ar (efeito bem conhecido em
  tráfego pago).
- CPC varia por canal e por objetivo (leads costuma custar mais que tráfego).
- Conversões e receita dependem do objetivo da campanha; campanhas de
  "vendas" geram receita e ROAS, campanhas de "leads"/"trafego" não.

Ajuste as constantes em CONFIG e a lista CAMPANHAS para modelar seu cenário.
"""

import numpy as np
import pandas as pd
from datetime import timedelta

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

SEED = 42
DATA_INICIO = "2025-01-01"
DATA_FIM = "2025-06-30"

DISPOSITIVOS = ["Mobile", "Desktop", "Tablet"]
DISPOSITIVOS_PROB = [0.65, 0.30, 0.05]

SEGMENTOS_PUBLICO = [
    "Remarketing", "Lookalike", "Interesses", "Busca ativa", "Geral"
]

# Cada campanha: id, nome, canal, objetivo, orçamento diário base (R$),
# data de início e fim (flight), ticket médio (só usado se objetivo = vendas)
CAMPANHAS = [
    dict(id="C001", nome="Google Search - Marca",      canal="Google Ads", objetivo="leads",   orcamento_base=80,  inicio="2025-01-01", fim="2025-06-30", ticket_medio=None),
    dict(id="C002", nome="Google Search - Genérico",    canal="Google Ads", objetivo="leads",   orcamento_base=60,  inicio="2025-02-01", fim="2025-05-31", ticket_medio=None),
    dict(id="C003", nome="Meta - Remarketing Vendas",   canal="Meta Ads",   objetivo="vendas",  orcamento_base=50,  inicio="2025-01-15", fim="2025-06-30", ticket_medio=180),
    dict(id="C004", nome="Meta - Prospecção Vendas",    canal="Meta Ads",   objetivo="vendas",  orcamento_base=100, inicio="2025-03-01", fim="2025-06-30", ticket_medio=150),
    dict(id="C005", nome="Google Display - Tráfego",    canal="Google Ads", objetivo="trafego", orcamento_base=40,  inicio="2025-01-01", fim="2025-04-30", ticket_medio=None),
    dict(id="C006", nome="Meta - Lançamento Produto",   canal="Meta Ads",   objetivo="vendas",  orcamento_base=120, inicio="2025-04-01", fim="2025-06-30", ticket_medio=210),
]

# Parâmetros base por canal/objetivo (ponto de partida antes do ruído)
CPC_BASE = {
    ("Google Ads", "leads"):   4.50,
    ("Google Ads", "trafego"): 1.80,
    ("Meta Ads", "vendas"):    1.20,
    ("Meta Ads", "leads"):     2.00,
}
CTR_BASE = {
    "Google Ads": 0.035,
    "Meta Ads":   0.012,
}
TAXA_CONVERSAO_BASE = {
    "leads":   0.06,   # % dos cliques que viram lead
    "vendas":  0.03,   # % dos cliques que viram venda
    "trafego": 0.0,    # campanha de tráfego não conta conversão de negócio
}

# ---------------------------------------------------------------------------
# GERAÇÃO
# ---------------------------------------------------------------------------

def gerar_dataset(seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    linhas = []

    for camp in CAMPANHAS:
        datas = pd.date_range(camp["inicio"], camp["fim"], freq="D")
        cpc_base = CPC_BASE.get((camp["canal"], camp["objetivo"]), 2.5)
        ctr_base = CTR_BASE.get(camp["canal"], 0.02)
        taxa_conv_base = TAXA_CONVERSAO_BASE.get(camp["objetivo"], 0.0)

        for dia_idx, data in enumerate(datas):
            # --- efeito dia da semana (fim de semana mais fraco) ---
            fator_dia_semana = 0.75 if data.weekday() >= 5 else 1.0

            # --- leve tendência sazonal ao longo do período (seno suave) ---
            fator_sazonal = 1 + 0.15 * np.sin(2 * np.pi * dia_idx / 90)

            # --- fadiga de criativo: CTR cai ~0.3% ao dia, com piso ---
            fator_fadiga = max(0.4, 1 - 0.003 * dia_idx)

            # --- orçamento investido no dia (com ruído em torno do base) ---
            investimento = max(
                5, rng.normal(camp["orcamento_base"], camp["orcamento_base"] * 0.15)
            ) * fator_dia_semana * fator_sazonal

            # --- CPC do dia (com ruído) ---
            cpc = max(0.3, rng.normal(cpc_base, cpc_base * 0.20))

            # --- cliques derivados do investimento / cpc ---
            cliques = max(0, int(round(investimento / cpc)))

            # --- CTR do dia (com fadiga + ruído) e impressões derivadas ---
            ctr = max(0.001, rng.normal(ctr_base, ctr_base * 0.15) * fator_fadiga)
            impressoes = int(round(cliques / ctr)) if ctr > 0 else 0

            # --- conversões ---
            taxa_conv = max(0, rng.normal(taxa_conv_base, taxa_conv_base * 0.25 + 1e-6))
            conversoes = int(round(cliques * taxa_conv))

            # --- receita (só campanhas de vendas) ---
            if camp["objetivo"] == "vendas" and conversoes > 0:
                ticket = rng.normal(camp["ticket_medio"], camp["ticket_medio"] * 0.25)
                receita = round(max(0, ticket) * conversoes, 2)
            else:
                receita = 0.0

            linhas.append(dict(
                data=data.date(),
                campanha_id=camp["id"],
                campanha_nome=camp["nome"],
                canal=camp["canal"],
                objetivo=camp["objetivo"],
                dispositivo=rng.choice(DISPOSITIVOS, p=DISPOSITIVOS_PROB),
                segmento_publico=rng.choice(SEGMENTOS_PUBLICO),
                investimento=round(investimento, 2),
                impressoes=impressoes,
                cliques=cliques,
                conversoes=conversoes,
                receita=receita,
            ))

    df = pd.DataFrame(linhas)

    # --- métricas derivadas (calculadas depois, evitando divisão por zero) ---
    df["ctr"] = np.where(df["impressoes"] > 0, df["cliques"] / df["impressoes"], 0).round(4)
    df["cpc"] = np.where(df["cliques"] > 0, df["investimento"] / df["cliques"], 0).round(2)
    df["cpa"] = np.where(df["conversoes"] > 0, df["investimento"] / df["conversoes"], np.nan).round(2)
    df["roas"] = np.where(df["investimento"] > 0, df["receita"] / df["investimento"], 0).round(2)

    ordem_colunas = [
        "data", "campanha_id", "campanha_nome", "canal", "objetivo",
        "dispositivo", "segmento_publico",
        "investimento", "impressoes", "cliques", "ctr",
        "conversoes", "receita", "cpc", "cpa", "roas",
    ]
    return df[ordem_colunas].sort_values(["data", "campanha_id"]).reset_index(drop=True)


if __name__ == "__main__":
    df = gerar_dataset()
    saida = "dataset_trafego_pago.csv"
    df.to_csv(saida, index=False)
    print(f"Dataset gerado com {len(df)} linhas -> {saida}")
    print(df.head(10).to_string(index=False))
