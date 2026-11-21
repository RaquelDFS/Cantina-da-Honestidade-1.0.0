
import mysql.connector
import streamlit as st

from database.inicializar import conectar
from controllers.usuario_controller import gerar_hash, verificar_senha
from controllers.validacoes import (
    TAMANHO_EMAIL,
    email_valido,
    senha_valida,
)


def tela_perfil():

    usuario = st.session_state.get("usuario")

    if not usuario:
        st.error("Usuário não autenticado.")
        return

    st.title("Meu Perfil")
    st.write("Consulte seus dados cadastrais e gerencie suas informações.")

    conexao = conectar()

    if not conexao:
        st.error("Não foi possível conectar ao banco de dados.")
        return

    cursor = conexao.cursor(dictionary=True)

    try:
        cursor.execute(
            """
            SELECT id_usuario, nome, email, perfil, status, matricula
            FROM usuarios
            WHERE id_usuario = %s
            """,
            (usuario["id_usuario"],),
        )

        dados_usuario = cursor.fetchone()

        if not dados_usuario:
            st.error("Usuário não encontrado.")
            return

        st.subheader("Dados cadastrais")

        st.text_input("Nome", value=dados_usuario["nome"], disabled=True)
        st.text_input(
            "Matrícula",
            value=dados_usuario["matricula"],
            disabled=True,
        )
        st.text_input(
            "Perfil",
            value=dados_usuario["perfil"].capitalize(),
            disabled=True,
        )
        st.text_input(
            "Status",
            value=dados_usuario["status"].capitalize(),
            disabled=True,
        )

        if dados_usuario["perfil"] == "cliente":

            cursor.execute(
                """
                SELECT saldo_atual
                FROM carteiras
                WHERE id_usuario = %s
                """,
                (dados_usuario["id_usuario"],),
            )

            carteira = cursor.fetchone()

            st.subheader("Minha carteira")

            if carteira:
                st.metric(
                    "Saldo disponível",
                    f"R$ {carteira['saldo_atual']:.2f}".replace(".", ","),
                )
            else:
                st.warning("Nenhuma carteira encontrada para este usuário.")

        st.divider()
        st.subheader("Alterar e-mail")

        with st.form("form_alterar_email"):

            novo_email = st.text_input(
                "Novo e-mail",
                value=dados_usuario["email"],
                max_chars=TAMANHO_EMAIL,
            )

            alterar_email = st.form_submit_button(
                "Salvar novo e-mail",
                use_container_width=True,
            )

        if alterar_email:

            novo_email = novo_email.strip().lower()

            if not email_valido(novo_email):
                st.error("Informe um e-mail válido.")

            elif novo_email == dados_usuario["email"]:
                st.warning("O novo e-mail é igual ao atual.")

            else:
                try:
                    cursor.execute(
                        """
                        UPDATE usuarios
                        SET email = %s
                        WHERE id_usuario = %s
                        """,
                        (novo_email, dados_usuario["id_usuario"]),
                    )

                    conexao.commit()

                    st.success("E-mail alterado com sucesso!")
                    st.rerun()

                except mysql.connector.IntegrityError as erro:
                    conexao.rollback()

                    if erro.errno == 1062:
                        st.error("Este e-mail já está cadastrado.")
                    else:
                        st.error("Não foi possível alterar o e-mail.")

                except mysql.connector.Error:
                    conexao.rollback()
                    st.error("Não foi possível alterar o e-mail.")

        st.divider()
        st.subheader("Alterar senha")

        with st.form("form_alterar_senha"):

            senha_atual = st.text_input(
                "Senha atual",
                type="password",
            )

            nova_senha = st.text_input(
                "Nova senha",
                type="password",
            )

            confirmar_senha = st.text_input(
                "Confirmar nova senha",
                type="password",
            )

            alterar_senha = st.form_submit_button(
                "Alterar senha",
                use_container_width=True,
            )

        if alterar_senha:

            if not senha_atual or not nova_senha or not confirmar_senha:
                st.error("Preencha todos os campos.")

            elif nova_senha != confirmar_senha:
                st.error("A confirmação da nova senha não corresponde.")

            elif nova_senha == senha_atual:
                st.error("A nova senha deve ser diferente da senha atual.")

            else:
                valido, mensagem = senha_valida(nova_senha)

                if not valido:
                    st.error(mensagem)

                else:
                    cursor.execute(
                        """
                        SELECT senha
                        FROM usuarios
                        WHERE id_usuario = %s
                        """,
                        (dados_usuario["id_usuario"],),
                    )

                    resultado = cursor.fetchone()

                    if resultado and verificar_senha(
                        senha_atual,
                        resultado["senha"],
                    ):

                        senha_hash = gerar_hash(nova_senha)

                        cursor.execute(
                            """
                            UPDATE usuarios
                            SET senha = %s
                            WHERE id_usuario = %s
                            """,
                            (
                                senha_hash,
                                dados_usuario["id_usuario"],
                            ),
                        )

                        conexao.commit()

                        st.success("Senha alterada com sucesso!")

                    else:
                        st.error("A senha atual está incorreta.")

    except mysql.connector.Error:
        conexao.rollback()
        st.error("Erro ao consultar ou atualizar os dados do perfil.")

    finally:
        cursor.close()
        conexao.close()
