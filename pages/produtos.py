import streamlit as st
from repositories.produto_repository import ProdutoRepository


def selecionar_produto(id_produto):
    st.session_state["produto_id"] = id_produto
    st.switch_page("pages/detalhes.py")


def listar_produtos():
    st.title("Produtos")

    repositorio = ProdutoRepository()
    produtos = repositorio.listar()

    if not produtos:
        st.info("Nenhum produto cadastrado.")
        return

    col_nome, col_preco, col_estoque, col_status, col_botao = st.columns(
        [3, 1, 1, 1, 2]
    )

    col_nome.write("**Nome**")
    col_preco.write("**Preço**")
    col_estoque.write("**Estoque**")
    col_status.write("**Status**")
    col_botao.write("**Ações**")

    for produto in produtos:
        col_nome, col_preco, col_estoque, col_status, col_botao = st.columns(
            [3, 1, 1, 1, 2]
        )

        col_nome.write(produto.nome)
        col_preco.write(f"R$ {produto.preco:.2f}")
        col_estoque.write(produto.quantidade_estoque)

        if produto.ativo:
            col_status.write("🟢")
        else:
            col_status.write("🔴")

        col_botao.button(
            "Ver detalhes",
            key=f"ver_{produto.id}",
            on_click=selecionar_produto,
            args=(produto.id,),
        )


listar_produtos()