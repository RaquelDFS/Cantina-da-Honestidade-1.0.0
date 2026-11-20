import streamlit as st

from database.inicializar import conectar
from controllers.usuario_controller import cadastrar_cliente
from views.mensagens import avisar
from controllers.validacoes import (
    SENHA_MAXIMO,
    SENHA_MINIMO,
    TAMANHO_EMAIL,
    TAMANHO_MATRICULA,
    TAMANHO_NOME_USUARIO,
)


def tela_cadastro_cliente():

    st.title("Cantina da Honestidade")
    st.subheader("Cadastro de cliente")
    st.caption("Todos os campos são obrigatórios.")

    with st.form("form_cadastro"):

        nome = st.text_input(
            "Nome completo",
            max_chars=TAMANHO_NOME_USUARIO,
            placeholder="Ex.: Maria da Silva"
        )
        email = st.text_input(
            "E-mail",
            max_chars=TAMANHO_EMAIL,
            placeholder="Ex.: maria@email.com"
        )
        matricula = st.text_input(
            "Matrícula",
            max_chars=TAMANHO_MATRICULA,
            placeholder="7 números",
            help="Você vai usar a matrícula para entrar no sistema."
        )
        senha = st.text_input(
            "Senha",
            type="password",
            max_chars=SENHA_MAXIMO,
            help=f"Entre {SENHA_MINIMO} e {SENHA_MAXIMO} caracteres."
        )
        confirmar_senha = st.text_input(
            "Confirmar senha",
            type="password",
            max_chars=SENHA_MAXIMO
        )

        cadastrar = st.form_submit_button(
            "Cadastrar",
            use_container_width=True
        )

    if cadastrar:

        if not all([nome.strip(), email.strip(), matricula.strip(), senha, confirmar_senha]):
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
                    # A mensagem é mostrada na tela de login, depois do rerun.
                    avisar(f"{mensagem} Faça login com sua matrícula.")
                    st.session_state.pagina = "login"
                    st.rerun()
                else:
                    st.error(mensagem)

            else:
                st.error("Não foi possível conectar ao banco de dados.")

    st.divider()

    if st.button("Voltar para login"):
        st.session_state.pagina = "login"
        st.rerun()
