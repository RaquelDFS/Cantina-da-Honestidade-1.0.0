
import streamlit as st

from database.inicializar import conectar
from controllers.usuario_controller import cadastrar_cliente


def tela_cadastro_cliente():

    st.title("Cantina da Honestidade")
    st.subheader("Cadastro de cliente")

    with st.form("form_cadastro"):

        nome = st.text_input("Nome completo")
        email = st.text_input("E-mail")
        matricula = st.text_input("Matrícula")
        senha = st.text_input("Senha", type="password")
        confirmar_senha = st.text_input(
            "Confirmar senha",
            type="password"
        )

        cadastrar = st.form_submit_button(
            "Cadastrar",
            use_container_width=True
        )

    if cadastrar:

        if not all([nome, email, matricula, senha, confirmar_senha]):
            st.warning("Preencha todos os campos.")

        elif senha != confirmar_senha:
            st.error("As senhas não coincidem.")

        else:
            conexao = conectar()

            if conexao:
                sucesso, mensagem = cadastrar_cliente(
                    conexao,
                    nome,
                    email,
                    senha,
                    matricula
                )

                conexao.close()

                if sucesso:
                    st.success(mensagem)
                    st.session_state.pagina = "login"
                    st.rerun()
                else:
                    st.error(mensagem)

    st.divider()

    if st.button("Voltar para login"):
        st.session_state.pagina = "login"
        st.rerun()
