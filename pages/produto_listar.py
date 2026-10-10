# PARTE DA CAMILE
# A LISTA PODE ESTAR EM APP.PY OU PODE ESTAR EM UMA PÁGINA SEPARADA
# VOCÊ PODE ESCOLHER ONDE FICA MELHOR
# Se em APP, coloque o produto_listar.py na pasta view. Se for criar uma pagina separada deixe aqui em pages

# Você precisa implementar o listar() no ProdutoRepository e criar a lista.
# Lembrando que a lista precisa ter botões que levem a descrição do produto. É uma função, não é uma página (views/produto_detalhes.py)
# Ao clicar, salve o ID em st.session_state['produto_id']. A página produto_detalhes.py já está pronta para receber esse ID e buscar o produto.

import streamlit as st
from repositories.produto_repository import ProdutoRepository


def selecionar_produto(id_produto):
    # Guarda o ID para a página produto_detalhes.py usar
    st.session_state['produto_id'] = id_produto


def listar_produtos():
    st.title("Produtos")

    repositorio = ProdutoRepository()
    produtos = repositorio.listar()

    if not produtos:
        st.info("Nenhum produto cadastrado.")
        return

    for produto in produtos:
        col_nome, col_preco, col_botao = st.columns([3, 1, 2])
        col_nome.write(produto.nome)
        col_preco.write(f"R$ {produto.preco:.2f}")
        col_botao.button(
            "Ver descrição",
            key=f"ver_{produto.id}",
            on_click=selecionar_produto,
            args=(produto.id,),
        )