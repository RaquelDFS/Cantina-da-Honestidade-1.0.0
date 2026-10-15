import streamlit as st
from repositories.produto_repository import ProdutoRepository
from models.produto import Produto


def exibir_edicao_produto(produto):
    st.subheader("Editar produto")

    with st.form("form_editar_produto"):
        nome = st.text_input("Nome do produto", value=produto.nome)

        preco = st.number_input(
            "Preço",
            min_value=0.0,
            value=float(produto.preco),
            step=0.01,
            format="%.2f"
        )

        quantidade = st.number_input(
            "Quantidade em estoque",
            min_value=0,
            value=int(produto.quantidade_estoque),
            step=1
        )

        salvar = st.form_submit_button("Salvar alterações")

    if salvar:
        if not nome.strip():
            st.error("Informe o nome do produto.")
        elif preco <= 0:
            st.error("O preço deve ser maior que R$ 0,00.")
        else:
            produto_atualizado = Produto(
                id=produto.id,
                nome=nome.strip(),
                preco=preco,
                quantidade_estoque=quantidade,
                ativo=quantidade > 0 and produto.ativo
            )

            ProdutoRepository().editar(produto_atualizado)
            st.session_state["acao_produto"] = None
            st.success("Produto atualizado com sucesso!")
            st.rerun()

    if st.button("Cancelar edição"):
        st.session_state["acao_produto"] = None
        st.rerun()
