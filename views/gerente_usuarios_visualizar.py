import streamlit as st

from database.inicializar import conectar
from controllers.usuario_controller import listar_usuarios_gerente


def tela_gerente_usuarios_visualizar():

    usuario = st.session_state.get("usuario")

    if not usuario or usuario["perfil"] != "gerente":
        st.error("Acesso não autorizado.")
        return

    st.title("Consulta de Usuários")
    st.caption("Consulta de clientes e gerentes. Dados financeiros não são exibidos.")

    conexao = conectar()

    if not conexao:
        st.error("Não foi possível conectar ao banco de dados.")
        return

    try:
        sucesso, resultado = listar_usuarios_gerente(conexao)

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

        pesquisa = st.text_input(
            "Pesquisar usuário", placeholder="Nome, e-mail ou matrícula"
        )

        filtro_perfil = st.selectbox("Perfil", ["Todos", "Gerente", "Cliente"])

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

                st.subheader(item["nome"])

                st.write(f"**Matrícula:** {item['matricula']}")
                st.write(f"**E-mail:** {item['email']}")
                st.write(f"**Perfil:** {item['perfil'].capitalize()}")
                st.write(f"**Situação:** {item['status'].capitalize()}")

                if item["status"] == "inativo":
                    motivo = item["motivo_inativacao"] or "Não informado"
                    st.write(f"**Motivo da inativação:** {motivo}")

    finally:
        conexao.close()
