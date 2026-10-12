# PARTE DA NICOLE
# O botão desta página deve estar dentro da página produto_detalhes.py
# CAMINHO:
# PÁGINA INICIAL > LISTA > DETALHE DO PRODUTO > EDITAR

import streamlit as st

from repositories.produto_repository import ProdutoRepository


def mostrar_produto_editar():

    repository = ProdutoRepository()

    id_produto = st.session_state.get("produto_id")

    if id_produto is None:
        st.error("Nenhum produto foi selecionado.")
        return

    produto = repository.buscar_por_id(id_produto)

    if produto is None:
        st.error("Produto não encontrado.")
        return

    st.subheader("Editar produto")

    with st.form("form_editar_produto"):

        nome = st.text_input(
            "Nome do produto",
            value=produto.nome
        )

        preco = st.number_input(
            "Preço",
            min_value=0.0,
            step=0.01,
            format="%.2f",
            value=float(produto.preco)
        )

        quantidade = st.number_input(
            "Quantidade em estoque",
            min_value=0,
            step=1,
            value=int(produto.quantidade_estoque)
        )

        ativo = st.checkbox(
            "Produto ativo",
            value=produto.ativo
        )

        salvar = st.form_submit_button("Salvar alterações")

        if salvar:

            produto.nome = nome
            produto.preco = preco
            produto.quantidade_estoque = quantidade
            produto.ativo = ativo

            repository.editar(produto)

            st.success(
                f"Produto '{produto.nome}' atualizado com sucesso!"
            )
