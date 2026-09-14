# Dashboard de Tráfego Pago

Dashboard em Streamlit para acompanhar campanhas de tráfego pago (Google Ads e Meta Ads): gráficos, filtros e indicadores recalculados a partir das somas do período.

## Decisões

- **API** - Queria alcançar um ambiente próximo do real com chamadas de API, não utilizei banco de dados pois já estava encontrando dificiuldades suficientes no uso do Streamlit (principalmente no visual e comportamento das páginas). 
- **Persistencia de login** - Utilizei JWT para realizar a persistência de login, nada muito complicado, mas não consegui resolver a lentidão no carregamento dos dados e login.
- **Layout e gráficos** - Utilizei alguns gráficos do Plotly (mesmo querendo usar os do Streamlit para exercitar o uso da ferramenta) devido à modificações para melhorar a visualização das labels dos gráficos devido ao tamanho do texto e tamanho dos gráficos.  
- **Escolha de dataset** - Eu preferi permitir a escolha do dataset na página de dados para evitar problemas de tratamento de dataset, pois eles poderiam conter inconsistências ou duplicatas que poderiam causar problemas na análise.



## Páginas

- **Login** — acesso autenticado ao app.
- **Dashboard** — desempenho ao longo do tempo, segmentação por público, comparativo por campanha e insights (CTR, CPC, CPA, ROAS) com variação em relação ao período anterior de mesmo tamanho.
- **Gestão de dados** — upload de CSV e prévia da tabela em uso.
- **Resumo** — cards de totais e destaques (melhor campanha, canal, dispositivo).



## Como executar

O projeto tem dois processos: a API (FastAPI) e o frontend (Streamlit). Rode os dois a partir da raiz do repositório.

```bash
pip install -r requirements.txt

# terminal 1 — backend (porta 8000)
uvicorn api.main:app --reload --port 8000

# terminal 2 — frontend (porta 8501)
streamlit run app.py
```

A API traz docs interativas em `http://localhost:8000/docs`.

## Usuários de demonstração


| Usuário    | Senha      | Papel      | Acesso                              |
| ---------- | ---------- | ---------- | ----------------------------------- |
| `admin`    | `senha123` | `admin`    | Dashboard, Resumo e Gestão de dados |
| `analista` | `senha123` | `analista` | apenas Dashboard e Resumo           |


As credenciais e os papéis vivem em `api/auth.py`. O login é feito pela API (`POST /login`), que devolve um JWT. O frontend guarda esse token em um cookie (7 dias): recarregar o navegador, fechar a aba ou reiniciar o Streamlit não pede login de novo. Em produção, defina a variável de ambiente `AUTH_SECRET` (a mesma nos dois processos).

## Fontes de dados

O backend mantém um **catálogo** de datasets e serve sempre **um único arquivo ativo** em `GET /dados` — Dashboard e Resumo nunca misturam fontes. O admin gerencia o catálogo na página Gestão de dados:

- **CSV de exemplo** — `data/dataset_trafego_pago.csv` (fixo, não é removível).
- **Upload** — envio de um ou vários CSVs de uma vez (gravados em `data/uploads/`).
- **Gerado** — botão que gera um dataset novo em `data/dataset_trafego_pago_{timestamp}.csv`.

Se a API estiver fora depois do login, o frontend cai no CSV de exemplo local como rede de segurança.

### Contrato da API


| Método   | Rota              | Quem        | Função                                                            |
| -------- | ----------------- | ----------- | ----------------------------------------------------------------- |
| `POST`   | `/login`          | público     | `{usuario, senha}` → `{access_token, token_type, usuario, papel}` |
| `GET`    | `/dados`          | autenticado | envelope do arquivo ativo: `{fonte, id, nome, registros}`         |
| `GET`    | `/dados/catalogo` | admin       | `{ativo, arquivos}`                                               |
| `POST`   | `/dados`          | admin       | multipart com vários CSVs; resume `{aceitos, erros}`              |
| `PUT`    | `/dados/ativo`    | admin       | `{id}` marca o arquivo ativo                                      |
| `DELETE` | `/dados/{id}`     | admin       | apaga um upload ou gerado                                         |
| `POST`   | `/dados/gerar`    | admin       | gera um CSV novo em `data/`                                       |


Para (re)gerar o CSV de exemplo canônico pela linha de comando:

```bash
python data/gerar_dataset_trafego_pago.py
```

O script grava `data/dataset_trafego_pago.csv`.

## Schema do CSV

Uma linha = uma campanha em um dia (e um dispositivo/segmento):


| Coluna             | Descrição                                                  |
| ------------------ | ---------------------------------------------------------- |
| `data`             | Data da veiculação                                         |
| `campanha_id`      | Identificador da campanha                                  |
| `campanha_nome`    | Nome da campanha                                           |
| `canal`            | `Google Ads` ou `Meta Ads`                                 |
| `objetivo`         | `leads`, `vendas` ou `trafego`                             |
| `dispositivo`      | `Mobile`, `Desktop` ou `Tablet`                            |
| `segmento_publico` | Segmento (remarketing, lookalike, etc.)                    |
| `investimento`     | Valor investido                                            |
| `impressoes`       | Impressões ou Visualizações                                |
| `cliques`          | Cliques                                                    |
| `ctr`              | Clique / impressão (no arquivo; o app recalcula)           |
| `conversoes`       | Conversões                                                 |
| `receita`          | Receita                                                    |
| `cpc`              | Custo por clique (no arquivo; o app recalcula)             |
| `cpa`              | Custo por aquisição (no arquivo; o app recalcula)          |
| `roas`             | Retorno sobre o investimento (no arquivo; o app recalcula) |




## Métricas

- **Absolutas** (somadas nos gráficos): investimento, impressões, cliques, conversões, receita.
- **Derivadas** (recalculadas das somas do período filtrado): CTR, CPC, CPA, ROAS. Não entram nos gráficos porque somar razões não faz sentido.



## Filtros

A sidebar (compartilhada entre Dashboard e Resumo) filtra por canal, período, campanha, dispositivo e objetivo. A seleção permanece ao trocar de página.

## Estrutura

```
app.py                 # entrada e navegação
api/                   # backend FastAPI (main, auth, dados)
views/                 # páginas (login, dashboard, gestão, resumo)
components/            # gráficos, cards, sidebar, login, dataset
data/                  # loader, gerador, CSV de exemplo e uploads
utils/                 # api, auth, métricas, filtros, formatação, cores
assets/                # logo, ícones, fundo
.streamlit/            # tema
```

