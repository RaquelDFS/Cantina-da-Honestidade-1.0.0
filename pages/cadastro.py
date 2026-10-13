
import streamlit as st
from models.produto import Produto
from repositories.produto_repository import ProdutoRepository

repository = ProdutoRepository()

st.title("Estoque de Doces")
st.subheader("Cadastrar produto")

with st.form("form_produto"):
    nome = st.text_input("Nome do produto")

    preco = st.number_input(
        "Preço (R$)",
        min_value=0.01,
        step=0.01,
        format="%.2f"
    )

    quantidade = st.number_input(
        "Quantidade em estoque",
        min_value=0,
        step=1
    )

    cadastrar = st.form_submit_button("Cadastrar")

if cadastrar:
    if not nome.strip():
        st.error("Informe o nome do produto.")
    elif preco <= 0:
        st.error("O preço deve ser maior que R$ 0,00.")
    elif quantidade <= 0:
        st.error("O estoque deve ser maior que zero.")
    else:
        produto = Produto(
            nome=nome.strip(),
            preco=preco,
            quantidade_estoque=quantidade,
            ativo=quantidade > 0
        )

        repository.cadastrar(produto)
        st.success(
            f"Produto '{produto.nome}' cadastrado com sucesso!"
        )
