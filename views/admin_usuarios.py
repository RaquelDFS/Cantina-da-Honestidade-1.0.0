import streamlit as st

from database.inicializar import conectar
from controllers.admin_usuario_controller import (
    listar_usuarios,
    cadastrar_usuario_administrativo,
    alterar_status_usuario,
)


def tela_admin_usuarios():

    usuario = st.session_state.get("usuario")

    if not usuario or usuario["perfil"] != "administrador":
        st.error("Acesso não autorizado.")
        return

    id_administrador = usuario["id_usuario"]

    st.title("Gestão de Usuários")
    st.caption("Consulta, cadastro e controle de acesso dos usuários.")

    conexao = conectar()

    if not conexao:
        st.error("Não foi possível conectar ao banco de dados.")
        return

    try:
        sucesso, resultado = listar_usuarios(conexao, id_administrador)

        if not sucesso:
            st.error(resultado)
            return

        usuarios = resultado

        total = len(usuarios)
        ativos = sum(u["status"] == "ativo" for u in usuarios)
        inativos = total - ativos

        coluna1, coluna2, coluna3 = st.columns(3)

        coluna1.metric("Total de usuários", total)
        coluna2.metric("Ativos", ativos)
        coluna3.metric("Inativos", inativos)

        st.divider()

        aba_consulta, aba_cadastro = st.tabs(
            ["Consultar usuários", "Cadastrar usuário"]
        )

        with aba_consulta:

            pesquisa = st.text_input(
                "Pesquisar usuário", placeholder="Nome, e-mail ou matrícula"
            )

            filtro_perfil = st.selectbox(
                "Perfil", ["Todos", "Administrador", "Gerente", "Cliente"]
            )

            filtro_status = st.selectbox("Situação", ["Todos", "Ativo", "Inativo"])

            usuarios_filtrados = []

            for item in usuarios:

                texto_pesquisa = pesquisa.strip().lower()

                corresponde_pesquisa = (
                    texto_pesquisa in item["nome"].lower()
                    or texto_pesquisa in item["email"].lower()
                    or texto_pesquisa in item["matricula"]
                )

                corresponde_perfil = (
                    filtro_perfil == "Todos" or item["perfil"] == filtro_perfil.lower()
                )

                corresponde_status = (
                    filtro_status == "Todos" or item["status"] == filtro_status.lower()
                )

                if corresponde_pesquisa and corresponde_perfil and corresponde_status:
                    usuarios_filtrados.append(item)

            st.write(f"**{len(usuarios_filtrados)} usuário(s) encontrado(s)**")

            for item in usuarios_filtrados:

                with st.container(border=True):

                    coluna_dados, coluna_acao = st.columns([4, 1])

                    with coluna_dados:

                        st.subheader(item["nome"])

                        st.write(f"**Matrícula:** {item['matricula']}")
                        st.write(f"**E-mail:** {item['email']}")
                        st.write(f"**Perfil:** {item['perfil'].capitalize()}")
                        st.write(f"**Situação:** {item['status'].capitalize()}")

                    with coluna_acao:

                        novo_status = (
                            "inativo" if item["status"] == "ativo" else "ativo"
                        )

                        texto_botao = (
                            "Desativar" if item["status"] == "ativo" else "Ativar"
                        )

                        if item["id_usuario"] == id_administrador:
                            st.caption("Sua conta")
                        elif st.button(
                            texto_botao,
                            key=f"status_usuario_{item['id_usuario']}",
                            use_container_width=True,
                        ):
                            sucesso, mensagem = alterar_status_usuario(
                                conexao,
                                id_administrador,
                                item["id_usuario"],
                                novo_status,
                            )

                            if sucesso:
                                st.success(mensagem)
                                st.rerun()
                            else:
                                st.error(mensagem)

        with aba_cadastro:

            st.subheader("Novo usuário administrativo")

            with st.form("form_usuario_administrativo", clear_on_submit=True):

                nome = st.text_input("Nome completo")
                email = st.text_input("E-mail")
                matricula = st.text_input("Matrícula")

                perfil = st.selectbox("Perfil", ["Gerente", "Administrador"])

                senha = st.text_input("Senha", type="password")

                confirmar_senha = st.text_input("Confirmar senha", type="password")

                cadastrar = st.form_submit_button(
                    "Cadastrar usuário", use_container_width=True
                )

            if cadastrar:

                if senha != confirmar_senha:
                    st.error("As senhas não coincidem.")

                else:
                    sucesso, mensagem = cadastrar_usuario_administrativo(
                        conexao,
                        id_administrador,
                        nome,
                        email,
                        matricula,
                        senha,
                        perfil.lower(),
                    )

                    if sucesso:
                        st.success(mensagem)
                        st.rerun()
                    else:
                        st.error(mensagem)

    finally:
        conexao.close()
