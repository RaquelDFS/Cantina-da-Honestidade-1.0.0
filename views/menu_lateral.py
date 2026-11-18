
import streamlit as st


def menu_lateral(cookies):

    usuario = st.session_state.usuario

    if usuario is None:
        return

    with st.sidebar:

        st.title(f"Olá, {usuario['nome']}!")

        if usuario["perfil"] in ["administrador", "gerente"]:
            st.caption(
                f"Perfil: {usuario['perfil'].capitalize()}"
            )

        st.divider()

        if st.button("Dashboard", use_container_width=True):
            st.session_state.pagina = "inicio"
            st.rerun()

        # Opções exclusivas de administrador
        if usuario["perfil"] == "administrador":

            st.subheader("Produtos")

            if st.button(
                "Cadastrar produto",
                use_container_width=True
            ):
                st.session_state.pagina = "produto_cadastro"
                st.rerun()

            if st.button(
                "Ver Produtos",
                use_container_width=True
            ):
                st.session_state.pagina = "admin_produtos_visualizar"
                st.rerun()

        # Opções exclusivas de gerente
        if usuario["perfil"] == "gerente":

            st.subheader("Produtos")

            if st.button(
                "Ver Produtos",
                use_container_width=True
            ):
                st.session_state.pagina = "gerente_produtos_visualizar"
                st.rerun()

            if st.button(
                "Editar produto",
                use_container_width=True
            ):
                st.session_state.pagina = "gerente_estoque_movimentar"
                st.rerun()

        # Opções de administrador e gerente
        if usuario["perfil"] in ["administrador", "gerente"]:

            st.subheader("Estoque")

            if st.button(
                "Movimentações de estoque",
                use_container_width=True
            ):
                st.session_state.pagina = "admin_estoque_visualizar"
                st.rerun()

        # Opções exclusivas de cliente
        if usuario["perfil"] == "cliente":

            if st.button(
                "Loja",
                use_container_width=True
            ):
                st.session_state.pagina = "cliente_loja"
                st.rerun()

            st.subheader("Minha carteira")

            if st.button(
                "Adicionar Crédito",
                use_container_width=True
            ):
                st.session_state.pagina = "cliente_adicionar_credito"
                st.rerun()

        st.divider()

        if st.button("Sair", use_container_width=True):
            cookies.remove("id_usuario")
            st.session_state.usuario = None
            st.session_state.pagina = "login"
            st.rerun()
