"""
app.py — entry point único do app.

Substitui o esquema anterior (Home.py + pages/1_Dashboard.py + CSS pra
esconder a navegação). Com st.navigation + st.Page, a lista de páginas
disponíveis é decidida em Python, então antes do login o Streamlit nem
sabe que a página "Dashboard" existe — não precisa esconder nada na marra.

Trocar de página após login/logout é só session_state + st.rerun(): o
app.py roda de novo, decide a lista de páginas de novo, pronto.
"""

import streamlit as st

from views import dashboard, data_management, login, summary

st.set_page_config(page_title="Dashboard Tráfego Pago", page_icon="assets/favicon.ico", layout="wide")

autenticado = bool(st.session_state.get("autenticado"))

# A segunda chamada de set_page_config é aditiva: mexe só no estado da sidebar.
# Ela só acontece quando o login/logout muda, senão a sidebar reabriria sozinha
# a cada rerun, desfazendo o colapso que o usuário fez na mão.
if st.session_state.get("sidebar_sincronizada") != autenticado:
    st.session_state["sidebar_sincronizada"] = autenticado
    st.set_page_config(
        initial_sidebar_state="expanded" if autenticado else "collapsed"
    )

if autenticado:
    # url_path explícito: as três views se chamam render(), e o Streamlit
    # inferiria o mesmo pathname pra todas ("render") — o que é erro.
    paginas = [
        st.Page(
            dashboard.render, title="Dashboard", icon="📊",
            url_path="dashboard", default=True,
        ),
        st.Page(
            data_management.render, title="Gestão de dados", icon="📁",
            url_path="gestao-de-dados",
        ),
        st.Page(summary.render, title="Resumo", icon="🧾", url_path="resumo"),
    ]
    # Com mais de uma página, a navegação nativa da sidebar passa a ser útil.
    posicao_nav = "sidebar"
else:
    paginas = [st.Page(login.render, title="Login", icon="🔒")]
    posicao_nav = "hidden"

pagina_atual = st.navigation(paginas, position=posicao_nav)
pagina_atual.run()
