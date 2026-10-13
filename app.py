
import streamlit as st

cadastro = st.Page(
    "pages/cadastro.py",
    title="Cadastro",
    default=True
)

produtos = st.Page(
    "pages/produtos.py",
    title="Produtos"
)

detalhes = st.Page(
    "pages/detalhes.py",
    title="Detalhes do produto",
    visibility="hidden"
)

pg = st.navigation(
    {
        "Menu": [cadastro, produtos],
        "": [detalhes],
    },
    position="sidebar"
)

pg.run()
