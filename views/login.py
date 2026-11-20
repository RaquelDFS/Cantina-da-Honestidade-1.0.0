import streamlit as st
import time

from database.inicializar import conectar
from controllers.usuario_controller import autenticar_usuario
from views.mensagens import mostrar_aviso


def tela_login(cookies):

    st.title("Cantina da Honestidade")
    st.subheader("Faça seu login")

    mostrar_aviso()

    matricula = st.text_input("Matrícula", max_chars=7, placeholder="7 números")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar", use_container_width=True):

        if not matricula or not senha:
            st.warning("Preencha a matrícula e a senha.")

        else:
            conexao = conectar()

            if conexao:
                sucesso, resultado = autenticar_usuario(
                    conexao,
                    matricula.strip(),
                    senha
                )

                conexao.close()

                if sucesso:
                    st.session_state.usuario = resultado
                    st.session_state.pagina = "inicio"

                    cookies.set(
                        "id_usuario",
                        str(resultado["id_usuario"]),
                        max_age=86400
                    )

                    time.sleep(1)
                    st.rerun()

                else:
                    st.error(resultado)

            else:
                st.error("Não foi possível conectar ao banco de dados.")

    st.divider()

    st.write("Ainda não possui uma conta?")

    if st.button("Cadastrar", use_container_width=True):
        st.session_state.pagina = "cadastro"
        st.rerun()
