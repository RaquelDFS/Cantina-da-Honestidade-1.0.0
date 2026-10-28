import streamlit as st
from repositories.produto_repository import ProdutoRepository
from repositories.fornecedor_repository import FornecedorRepository
from models.produto import Produto


def exibir_edicao_produto(produto):
    st.subheader("Editar produto")

    fornecedor_repo = FornecedorRepository()

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

        fornecedores = fornecedor_repo.listar()
        opcoes_fornecedor = {f.nome: f.id for f in fornecedores}

        fornecedor_atual = ""
        if produto.id_fornecedor:
            fornecedor_atual_obj = fornecedor_repo.buscar_por_id(produto.id_fornecedor)
            if fornecedor_atual_obj:
                fornecedor_atual = fornecedor_atual_obj.nome

        index_fornecedor = 0
        if fornecedor_atual in opcoes_fornecedor:
            index_fornecedor = list(opcoes_fornecedor.keys()).index(fornecedor_atual)

        fornecedor_selecionado = st.selectbox(
            "Fornecedor",
            options=opcoes_fornecedor.keys(),
            index=index_fornecedor
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
                ativo=quantidade > 0 and produto.ativo,
                id_fornecedor=opcoes_fornecedor.get(fornecedor_selecionado)
            )

            ProdutoRepository().editar(produto_atualizado)
            st.session_state["acao_produto"] = None
            st.success("Produto atualizado com sucesso!")
            st.rerun()

    if st.button("Cancelar edição"):
        st.session_state["acao_produto"] = None
        st.rerun()
