"""
components/dataset.py — UI da Gestão de dados (só admin).

Upload de vários CSVs, geração de dataset de exemplo, seleção de qual fica
ativo e prévia do arquivo em uso. Toda a persistência é na API (data/loader).
"""

import streamlit as st

from data import loader


def render_upload() -> None:
    arquivos = st.file_uploader(
        "Enviar datasets (CSV)",
        type="csv",
        accept_multiple_files=True,
        key="upload_csv",
    )

    col_enviar, col_gerar = st.columns(2)

    with col_enviar:
        if st.button("Enviar", width="stretch", disabled=not arquivos):
            resultado = loader.enviar_arquivos(arquivos)
            if resultado is None:
                st.error("Não foi possível enviar (API indisponível).")
            else:
                for ok in resultado["aceitos"]:
                    st.toast(f"Enviado: {ok['nome']}")
                for erro in resultado["erros"]:
                    st.warning(f"{erro['nome']}: {erro['motivo']}")
                st.rerun()

    with col_gerar:
        if st.button("Gerar dataset de exemplo", width="stretch"):
            gerado = loader.gerar_dataset()
            if gerado is None:
                st.error("Não foi possível gerar (API indisponível).")
            else:
                st.toast(f"Gerado: {gerado['nome']}")
                st.rerun()


def render_seletor() -> None:
    catalogo = loader.listar_catalogo()
    if not catalogo or not catalogo["arquivos"]:
        st.info("Nenhum dataset no catálogo ainda.")
        return

    arquivos = catalogo["arquivos"]
    ids = [a["id"] for a in arquivos]
    rotulos = {a["id"]: f"{a['nome']} ({a['fonte']})" for a in arquivos}
    ativo = catalogo["ativo"]

    escolhido = st.selectbox(
        "Dataset ativo",
        options=ids,
        index=ids.index(ativo) if ativo in ids else 0,
        format_func=lambda i: rotulos.get(i, i),
    )

    if escolhido != ativo:
        if loader.ativar_dataset(escolhido):
            st.rerun()
        else:
            st.error("Não foi possível trocar o dataset ativo.")

    entrada = next((a for a in arquivos if a["id"] == escolhido), None)
    if entrada and entrada["fonte"] != "local":
        if st.button("Remover este dataset"):
            if loader.remover_dataset(escolhido):
                st.rerun()
            else:
                st.error("Não foi possível remover o dataset.")


def render_previa(df, fonte: str, nome: str) -> None:
    st.caption(loader.descricao_fonte(fonte, nome))

    col1, col2, col3 = st.columns(3)
    col1.metric("Linhas", f"{len(df):,}".replace(",", "."))
    col2.metric("Colunas", len(df.columns))
    col3.metric(
        "Período",
        f"{df['data'].min():%d/%m/%Y} — {df['data'].max():%d/%m/%Y}",
    )

    st.dataframe(df, width="stretch", hide_index=True)
