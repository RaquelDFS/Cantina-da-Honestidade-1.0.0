
import streamlit as st
from repositories.produto_repository import ProdutoRepository
from views.produto_editar import exibir_edicao_produto


def exibir_produto_detalhes():
    st.title("Detalhes do produto")

    id_produto = st.session_state.get("produto_id")

    if id_produto is None:
        st.warning("Nenhum produto foi selecionado.")

        if st.button("Voltar para produtos"):
            st.switch_page("pages/produtos.py")

        return

    repositorio = ProdutoRepository()
    produto = repositorio.buscar_por_id(id_produto)

    if produto is None:
        st.error("Produto não encontrado.")
        return

    st.subheader(produto.nome)
    st.write(f"**ID:** {produto.id}")
    st.write(f"**Preço:** R$ {produto.preco:.2f}")
    st.write(f"**Quantidade em estoque:** {produto.quantidade_estoque}")

    st.write(
        f"**Status:** {'Ativo' if produto.ativo else 'Inativo'}"
    )

    texto_botao = (
        "Desativar produto" if produto.ativo
        else "Ativar produto"
    )

    if st.button(texto_botao, key=f"toggle_ativo_{produto.id}"):

        if produto.ativo and produto.quantidade_estoque > 0:
            st.warning(
                "Não é possível desativar um produto com estoque disponível."
            )
        else:
            alterado = repositorio.toggle_ativo(produto.id)

            if alterado:
                st.success("Status do produto atualizado com sucesso!")
                st.rerun()
            else:
                st.warning(
                    "Não foi possível alterar o status. "
                    "Verifique a quantidade em estoque."
                )

    st.divider()

    col_editar, col_voltar = st.columns(2)

    if col_editar.button("Editar", use_container_width=True):
        st.session_state["acao_produto"] = "editar"
        st.rerun()

    if col_voltar.button("Voltar", use_container_width=True):
        st.session_state["acao_produto"] = None
        st.switch_page("pages/produtos.py")

    acao = st.session_state.get("acao_produto")

    if acao == "editar":
        exibir_edicao_produto(produto)
