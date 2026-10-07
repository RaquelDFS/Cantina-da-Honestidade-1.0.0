import streamlit as st

from repositories.produto_repository import ProdutoRepository


def mostrar_produto_detalhes():

    repository = ProdutoRepository()

    id_produto = st.session_state.get("produto_id")

    if id_produto is None:
        st.error("Nenhum produto foi selecionado.")
        return

    produto = repository.buscar_por_id(id_produto)

    if produto is None:
        st.error("Produto não encontrado.")
        return

    st.title("Detalhes do Produto")

    st.write(f"ID: {produto.id}")
    st.write(f"Nome: {produto.nome}")
    st.write(f"Preço: R$ {produto.preco:.2f}")
    st.write(f"Estoque: {produto.quantidade_estoque}")
    st.write(
        f"Status: {'Ativo' if produto.ativo else 'Inativo'}"
    )
