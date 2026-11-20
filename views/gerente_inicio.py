import streamlit as st
from database.inicializar import conectar


# Produtos com essa quantidade ou menos aparecem no aviso de estoque baixo.
LIMITE_ESTOQUE_BAIXO = 5


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

    st.subheader("Atalhos")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Consultar produtos", use_container_width=True):
            st.session_state.pagina = "gerente_produtos_visualizar"
            st.rerun()

        if st.button("Movimentar estoque", use_container_width=True):
            st.session_state.pagina = "gerente_estoque_movimentar"
            st.rerun()

    with col2:
        if st.button("Histórico de movimentações", use_container_width=True):
            st.session_state.pagina = "admin_estoque_visualizar"
            st.rerun()

        st.button(
            "Consultar vendas",
            use_container_width=True,
            disabled=True,
            help="Disponível quando o módulo de relatórios (P07) for concluído."
        )


# Lista os produtos com estoque baixo ou zerado (os que mais precisam de reposição).
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
