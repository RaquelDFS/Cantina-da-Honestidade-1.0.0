
import streamlit as st
from database.inicializar import conectar


def tela_gerente_inicio():

    usuario = st.session_state.usuario

    # Verificação de acesso
    if not usuario or usuario["perfil"] != "gerente":
        st.error("Acesso não autorizado.")
        st.session_state.pagina = "login"
        st.rerun()
        return

    st.title("Painel do Gerente")
    st.write(f"Bem-vindo(a), {usuario['nome']}!")
    st.caption("Acompanhamento das operações da cantina")

    st.divider()

    st.subheader("Visão geral")
    st.caption("Colocar aqui os produtos que estão acabando")

    st.divider()

    st.subheader("Gerenciamento")
    st.caption("Oq falta fazer")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Consultar produtos", use_container_width=True):
            st.session_state.pagina = "produtos"
            st.rerun()

        if st.button("Consultar vendas", use_container_width=True):
            st.session_state.pagina = "vendas"
            st.rerun()

    with col2:
        if st.button("Movimentações de estoque", use_container_width=True):
            st.session_state.pagina = "estoque"
            st.rerun()

    st.divider()
