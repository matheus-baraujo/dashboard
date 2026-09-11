"""
components/dataset.py — upload e prévia do dataset (página Gestão de dados).

O upload mora aqui (e não na sidebar) e é guardado no session_state por
data.loader.registrar_upload, então as outras páginas usam o mesmo dataset.
"""

import streamlit as st

from data import loader


def render_upload() -> None:
    arquivo = st.file_uploader("Upload dataset (CSV)", type="csv")

    if arquivo is not None:
        nome_atual = st.session_state.get(loader.CHAVE_NOME_UPLOAD)
        if nome_atual != arquivo.name:
            loader.registrar_upload(arquivo)
            st.rerun()

    if loader.tem_upload():
        if st.button("Remover upload e voltar para a origem padrão"):
            loader.limpar_upload()
            st.rerun()


def render_previa(df, fonte: str) -> None:
    st.caption(loader.descricao_fonte(fonte))

    col1, col2, col3 = st.columns(3)
    col1.metric("Linhas", f"{len(df):,}".replace(",", "."))
    col2.metric("Colunas", len(df.columns))
    col3.metric(
        "Período",
        f"{df['data'].min():%d/%m/%Y} — {df['data'].max():%d/%m/%Y}",
    )

    st.dataframe(df, width="stretch", hide_index=True)
