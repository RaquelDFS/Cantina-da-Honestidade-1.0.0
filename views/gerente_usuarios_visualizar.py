# O gerente vê clientes e gerentes, o status e o motivo da inativação.


import streamlit as st

from database.inicializar import conectar


# filtro de perfil
ROTULOS_PERFIL = {
    "todos": "Todos",
    "cliente": "Cliente",
    "gerente": "Gerente",
}

# filtro de status
ROTULOS_STATUS = {
    "todos": "Todos",
    "ativo": "Ativo",
    "inativo": "Inativo",
}


# Monta o SQL e os parâmetros conforme os filtros escolhidos

def montar_consulta(busca="", perfil="todos", status="todos"):

    sql = """
        SELECT
            nome,
            matricula,
            perfil,
            status,
            motivo_inativacao
        FROM usuarios
        WHERE perfil IN ('cliente', 'gerente')
    """
    parametros = []

    busca = (busca or "").strip()

    if busca:
        sql += " AND (nome LIKE %s OR matricula LIKE %s)"
        parametros += [f"%{busca}%", f"{busca}%"]

    if perfil in ("cliente", "gerente"):
        sql += " AND perfil = %s"
        parametros.append(perfil)

    if status in ("ativo", "inativo"):
        sql += " AND status = %s"
        parametros.append(status)

    sql += " ORDER BY status DESC, nome"   # inativos primeiro, depois por nome

    return sql, parametros


# Troca os valores do banco por textos para a tabela
def preparar_linhas(usuarios):
    linhas = []

    for usuario in usuarios:
        if usuario["status"] == "inativo":
            motivo = usuario["motivo_inativacao"] or "Não informado"
        else:
            motivo = "-"

        linhas.append({
            "Nome": usuario["nome"],
            "Matrícula": usuario["matricula"],
            "Perfil": ROTULOS_PERFIL.get(usuario["perfil"], usuario["perfil"]),
            "Status": ROTULOS_STATUS.get(usuario["status"], usuario["status"]),
            "Motivo da inativação": motivo,
        })

    return linhas


def tela_gerente_usuarios_visualizar():

    # Verificação de acesso 
    usuario = st.session_state.get("usuario")

    if not usuario or usuario.get("perfil") != "gerente":
        st.error("Acesso permitido somente para gerentes.")
        return

    st.title("Usuários")
    st.caption("Clientes e gerentes cadastrados. Dados financeiros não são exibidos.")

    st.divider()

   
    busca = st.text_input(
        "Buscar por nome ou matrícula",
        max_chars=100,
        key="usuarios_busca"
    )

    col_perfil, col_status = st.columns(2)

    with col_perfil:
        perfil = st.selectbox(
            "Perfil",
            options=list(ROTULOS_PERFIL),
            format_func=lambda opcao: ROTULOS_PERFIL[opcao],
            key="usuarios_perfil"
        )

    with col_status:
        status = st.selectbox(
            "Status",
            options=list(ROTULOS_STATUS),
            format_func=lambda opcao: ROTULOS_STATUS[opcao],
            key="usuarios_status"
        )

    #  Consulta 
    conexao = conectar()

    if conexao is None:
        st.error("Não foi possível conectar ao banco de dados.")
        return

    try:
        cursor = conexao.cursor(dictionary=True)
        sql, parametros = montar_consulta(busca, perfil, status)
        cursor.execute(sql, parametros)
        usuarios = cursor.fetchall()
        cursor.close()

    except Exception as erro:
        print(f"Erro ao consultar usuários: {erro}")
        st.error("Não foi possível carregar os usuários.")
        return

    finally:
        conexao.close()

    # Resultado 
    ativos = sum(1 for u in usuarios if u["status"] == "ativo")
    inativos = len(usuarios) - ativos

    col1, col2, col3 = st.columns(3)
    col1.metric("Encontrados", len(usuarios))
    col2.metric("Ativos", ativos)
    col3.metric("Inativos", inativos)

    if not usuarios:
        st.info("Nenhum usuário encontrado com esses filtros.")
        return

    st.dataframe(
        preparar_linhas(usuarios),
        hide_index=True,
        use_container_width=True,
        column_config={
            "Nome": st.column_config.TextColumn(width="medium"),
            "Matrícula": st.column_config.TextColumn(width="small"),
            "Motivo da inativação": st.column_config.TextColumn(width="large"),
        },
    )
