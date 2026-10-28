import streamlit as st
from models.produto import Produto
from repositories.produto_repository import ProdutoRepository
from repositories.fornecedor_repository import FornecedorRepository

repository = ProdutoRepository()
fornecedor_repository = FornecedorRepository()

st.title("Estoque da Cantina da Honestidade")
st.subheader("Cadastrar produto")

with st.form("form_produto"):
    nome = st.text_input("Nome do produto *",
                         max_chars=30,
                         )

    preco = st.number_input(
        "Preço (R$) *",
        min_value=0.01,
        step=0.01,
        format="%.2f",
    )
    quantidade = st.number_input(
        "Quantidade em estoque *",
        min_value=1,
        step=1,

    )

    fornecedores = fornecedor_repository.listar()
    opcoes_fornecedor = {f.nome: f.id for f in fornecedores}
    fornecedor_selecionado = st.selectbox(
        "Fornecedor",
        options=opcoes_fornecedor.keys(),
        index=0 if opcoes_fornecedor else None
    )

    cadastrar = st.form_submit_button("Cadastrar")

if cadastrar:
    if not nome.strip():
        st.error("Informe o nome do produto.")
    elif len(nome.strip()) > 30:
        st.error("O nome do produto deve ter no máximo 30 caracteres.")
    elif preco <= 0:
        st.error("O preço deve ser maior que R$ 0,00.")
    elif quantidade <= 0:
        st.error("O estoque deve ser maior que zero.")
    else:
        produto = Produto(
            nome=nome.strip(),
            preco=preco,
            quantidade_estoque=quantidade,
            ativo=quantidade > 0,
            id_fornecedor=opcoes_fornecedor.get(fornecedor_selecionado)
        )

        repository.cadastrar(produto)
        st.success(
            f"Produto '{produto.nome}' cadastrado com sucesso!"
        )