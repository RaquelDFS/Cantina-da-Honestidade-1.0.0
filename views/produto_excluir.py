
import streamlit as st
from repositories.produto_repository import ProdutoRepository


def exibir_confirmacao_exclusao(produto):
    st.subheader("Excluir produto")

    st.warning(
        f"Tem certeza de que deseja excluir '{produto.nome}'? "
        "Essa ação não poderá ser desfeita."
    )

    col_confirmar, col_cancelar = st.columns(2)

    if col_confirmar.button(
        "Confirmar exclusão",
        key="confirmar_exclusao"
    ):
        ProdutoRepository().excluir(produto.id)

        st.session_state["produto_id"] = None
        st.session_state["acao_produto"] = None

        st.success("Produto excluído com sucesso!")
        st.switch_page("pages/produtos.py")

    if col_cancelar.button(
        "Cancelar",
        key="cancelar_exclusao"
    ):
        st.session_state["acao_produto"] = None
        st.rerun()
