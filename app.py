# CRIEI UM ARQUIVO REQUERIMENTS, BASTA USAR O COMANDO pip install -r requirements.txt PARA BAIXAR TODAS AS BIBLIOTECAS NECESSÁRIAS PARA RODAR O PROJETO
# editem um pouco o streamlit, mudar cores, tamanho das fontes, botoes etc.
import streamlit as st
from models.produto import Produto
from repositories.produto_repository import ProdutoRepository

repository = ProdutoRepository()


st.title("Estoque de Doces")

st.subheader("Cadastrar produto")

with st.form("form_produto"):

    nome = st.text_input("Nome do produto")

    preco = st.number_input(
        "Preço",
        min_value=0.0,
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

        produto = Produto(
            nome=nome,
            preco=preco,
            quantidade_estoque=quantidade
        )

        repository.cadastrar(produto)

        st.success(
            f"Produto '{produto.nome}' cadastrado com sucesso!"
        )
