"""Navegação e entrada do app."""

import streamlit as st

from utils.auth import restaurar_sessao
from views import dashboard, data_management, login, summary

st.set_page_config(page_title="Dashboard Tráfego Pago", page_icon="assets/favicon.ico", layout="wide")

restaurar_sessao()
autenticado = bool(st.session_state.get("autenticado"))

# Só no login/logout: senão a sidebar reabre a cada rerun.
if st.session_state.get("sidebar_sincronizada") != autenticado:
    st.session_state["sidebar_sincronizada"] = autenticado
    st.set_page_config(
        initial_sidebar_state="expanded" if autenticado else "collapsed"
    )

if autenticado:
    # url_path explícito: as views se chamam render().
    paginas = [
        st.Page(
            dashboard.render, title="Dashboard", icon="📊",
            url_path="dashboard", default=True,
        ),
        st.Page(summary.render, title="Resumo", icon="🧾", url_path="resumo"),
    ]
    # Gestão de dados só aparece para o admin. A view ainda chama exigir_admin()
    # para bloquear quem tentar o url_path na mão.
    if st.session_state.get("papel") == "admin":
        paginas.insert(
            1,
            st.Page(
                data_management.render, title="Gestão de dados", icon="📁",
                url_path="gestao-de-dados",
            ),
        )
    posicao_nav = "sidebar"
else:
    paginas = [st.Page(login.render, title="Login", icon="🔒")]
    posicao_nav = "hidden"

pagina_atual = st.navigation(paginas, position=posicao_nav)
pagina_atual.run()
