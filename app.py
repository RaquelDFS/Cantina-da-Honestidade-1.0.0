
import streamlit as st

from database.inicializar import inicializar_banco


@st.cache_resource
def preparar_banco():
    inicializar_banco()


preparar_banco()

cadastro = st.Page(
    "pages/cadastro.py",
    title="Cadastro",
    default=True
)

produtos = st.Page(
    "pages/produtos.py",
    title="Produtos"
)

editar = st.Page(
    "pages/editar.py",
    title="Editar produto",
    visibility="hidden"
)

pg = st.navigation(
    {
        "Menu": [cadastro, produtos],
        "": [editar],
    },
    position="sidebar"
)

pg.run()
