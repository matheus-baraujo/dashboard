# Dashboard de Tráfego Pago

Dashboard em Streamlit para acompanhar campanhas de tráfego pago (Google Ads e Meta Ads): gráficos, filtros e indicadores recalculados a partir das somas do período.

## Páginas

- **Login** — acesso autenticado ao app.
- **Dashboard** — desempenho ao longo do tempo, segmentação por público, comparativo por campanha e insights (CTR, CPC, CPA, ROAS) com variação em relação ao período anterior de mesmo tamanho.
- **Gestão de dados** — upload de CSV e prévia da tabela em uso.
- **Resumo** — cards de totais e destaques (melhor campanha, canal, dispositivo).

## Como executar

```bash
pip install -r requirements.txt
streamlit run app.py
```

Dependências usadas pelo app: `streamlit`, `pandas`, `plotly`, `requests`. O gerador do CSV de exemplo também usa `numpy`.

## Login de demonstração

| Usuário | Senha    |
| ------- | -------- |
| `admin` | `senha123` |

As credenciais estão em `utils/auth.py`.

## Fontes de dados

O app escolhe a origem nesta ordem:

1. **Upload** — CSV enviado em Gestão de dados (fica no `session_state`).
2. **API** — `GET http://localhost:8000/dados`.
3. **CSV local** — `data/dataset_trafego_pago.csv`.

Para (re)gerar o CSV de exemplo:

```bash
python data/gerar_dataset_trafego_pago.py
```

O script grava `dataset_trafego_pago.csv` no diretório atual. Coloque o arquivo em `data/` para o app encontrá-lo.

## Schema do CSV

Uma linha = uma campanha em um dia (e um dispositivo/segmento):

| Coluna              | Descrição                                      |
| ------------------- | ---------------------------------------------- |
| `data`              | Data da veiculação                             |
| `campanha_id`       | Identificador da campanha                      |
| `campanha_nome`     | Nome da campanha                               |
| `canal`             | `Google Ads` ou `Meta Ads`                     |
| `objetivo`          | `leads`, `vendas` ou `trafego`                 |
| `dispositivo`       | `Mobile`, `Desktop` ou `Tablet`                |
| `segmento_publico`  | Segmento (remarketing, lookalike, etc.)        |
| `investimento`      | Valor investido                                |
| `impressoes`        | Impressões                                     |
| `cliques`           | Cliques                                        |
| `ctr`               | Clique / impressão (no arquivo; o app recalcula) |
| `conversoes`        | Conversões                                     |
| `receita`           | Receita                                        |
| `cpc`               | Custo por clique (no arquivo; o app recalcula) |
| `cpa`               | Custo por aquisição (no arquivo; o app recalcula) |
| `roas`              | Retorno sobre o investimento (no arquivo; o app recalcula) |

## Métricas

- **Absolutas** (somadas nos gráficos): investimento, impressões, cliques, conversões, receita.
- **Derivadas** (recalculadas das somas do período filtrado): CTR, CPC, CPA, ROAS. Não entram nos gráficos porque somar razões não faz sentido.

## Filtros

A sidebar (compartilhada entre Dashboard e Resumo) filtra por canal, período, campanha, dispositivo e objetivo. A seleção permanece ao trocar de página.

## Estrutura

```
app.py                 # entrada e navegação
views/                 # páginas (login, dashboard, gestão, resumo)
components/            # gráficos, cards, sidebar, login, dataset
data/                  # loader, gerador e CSV de exemplo
utils/                 # auth, métricas, filtros, formatação, cores
assets/                # logo, ícones, fundo
.streamlit/            # tema
```
