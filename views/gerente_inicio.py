import streamlit as st
from database.inicializar import conectar
from views.admin_Mestoque_visualizar import tela_admin_estoque_visualizar
# Produtos com essa quantidade ou menos aparecem no aviso de estoque baixo.
LIMITE_ESTOQUE_BAIXO = 3


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

    st.subheader("Produtos acabando")
    mostrar_estoque_baixo()

    st.divider()
    st.subheader("Movimentação Estoque")
    tela_admin_estoque_visualizar()


def mostrar_estoque_baixo():
    conexao = conectar()

    if conexao is None:
        st.error("Não foi possível consultar o estoque.")
        return

    try:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("""
            SELECT nome, quantidade_estoque, status
            FROM produtos
            WHERE quantidade_estoque <= %s
            ORDER BY quantidade_estoque, nome
        """, (LIMITE_ESTOQUE_BAIXO,))
        produtos = cursor.fetchall()
        cursor.close()

    except Exception as erro:
        print(f"Erro ao consultar estoque baixo: {erro}")
        st.error("Não foi possível consultar o estoque.")
        return

    finally:
        conexao.close()

    if not produtos:
        st.success("Nenhum produto com estoque baixo.")
        return

    for produto in produtos:
        quantidade = produto["quantidade_estoque"]

        if quantidade == 0:
            st.warning(f"**{produto['nome']}**: sem estoque (produto inativo)")
        else:
            st.info(f"**{produto['nome']}**: restam {quantidade} unidade(s)")
