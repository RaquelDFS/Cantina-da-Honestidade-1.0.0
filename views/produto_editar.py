
import streamlit as st
from repositories.produto_repository import ProdutoRepository
from models.produto import Produto


def exibir_edicao_produto():
    st.title("Editar produto")

    if st.session_state.pop("edicao_salva", False):
        st.success("Produto atualizado com sucesso!")

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

        if st.button("Voltar para produtos"):
            st.switch_page("pages/produtos.py")

        return

    st.write(f"**Código do produto:** {produto.id}")

    with st.form("form_editar_produto"):
        nome = st.text_input(
            "Nome do produto",
            value=produto.nome
        )

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

        ativo = st.checkbox(
            "Produto ativo",
            value=produto.ativo
        )

        col_salvar, col_voltar = st.columns(2)

        with col_salvar:
            salvar = st.form_submit_button(
                "Salvar alterações",
                use_container_width=True
            )

        with col_voltar:
            voltar = st.form_submit_button(
                "Voltar aos produtos",
                use_container_width=True
            )

    if voltar:
        st.session_state["produto_id"] = None
        st.switch_page("pages/produtos.py")

    if salvar:
        if not nome.strip():
            st.error("Informe o nome do produto.")

        elif preco <= 0:
            st.error("O preço deve ser maior que R$ 0,00.")

        elif not ativo and quantidade > 0:
            st.warning(
                "Não é possível desativar um produto "
                "com estoque disponível."
            )

        else:
            produto_atualizado = Produto(
                id=produto.id,
                nome=nome.strip(),
                preco=preco,
                quantidade_estoque=quantidade,
                ativo=ativo
            )

            try:
                repositorio.editar(produto_atualizado)

            except Exception:
                st.error(
                    "Não foi possível salvar as alterações. "
                    "Verifique os dados ou a conexão com o banco."
                )

            else:
                st.session_state["edicao_salva"] = True
                st.rerun()
