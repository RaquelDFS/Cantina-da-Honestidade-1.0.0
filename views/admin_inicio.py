import streamlit as st
from database.inicializar import conectar


def tela_admin_inicio():

    usuario = st.session_state.usuario

    if not usuario or usuario["perfil"] != "administrador":
        st.error("Acesso não autorizado.")
        st.session_state.pagina = "login"
        st.rerun()
        return

    st.title("Painel Administrativo")
    st.write(f"Bem-vindo(a), {usuario['nome']}!")
    st.caption("Visão geral da Cantina da Honestidade")

    st.divider()

    st.subheader("Gerenciamento")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Gerenciar usuários", use_container_width=True):
            st.info("Módulo de gerenciamento de usuários em desenvolvimento.")

        if st.button("Gerenciar produtos", use_container_width=True):
            st.session_state.pagina = "admin_produtos_visualizar"
            st.rerun()

    with col2:
        if st.button("Gerenciar orçamentos", use_container_width=True):
            st.info("Módulo de gerenciamento de orçamentos em desenvolvimento.")

        if st.button("Visualizar relatórios", use_container_width=True):
            st.info("Módulo de relatórios em desenvolvimento.")

    st.divider()
