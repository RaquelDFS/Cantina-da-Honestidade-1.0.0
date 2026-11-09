
import streamlit as st
import unicodedata
from repositories.produto_repository import ProdutoRepository


def selecionar_produto(id_produto):
    st.session_state["produto_id"] = id_produto
    st.switch_page("pages/detalhes.py")


def normalizar_texto(texto):
    texto = texto.lower()
    texto = unicodedata.normalize("NFD", texto)

    texto = "".join(
        letra for letra in texto
        if unicodedata.category(letra) != "Mn"
    )

    return texto


def listar_produtos():
    st.title("Produtos")

    repositorio = ProdutoRepository()
    produtos = repositorio.listar()

    busca = st.text_input("Buscar produto pelo nome")

    col_filtro, col_ordem = st.columns(2)

    with col_filtro:
        status = st.selectbox(
            "Filtrar por status",
            ["Ativos", "Inativos", "Todos"]
        )

    with col_ordem:
        ordenacao = st.selectbox(
            "Ordenar produtos por",
            [
                "Menor estoque primeiro",
                "Maior estoque primeiro",
                "Nome (A-Z)",
                "Nome (Z-A)"
            ]
        )

    produtos_filtrados = []

    for produto in produtos:
        nome_encontrado = (
            normalizar_texto(busca) in normalizar_texto(produto.nome)
        )

        if status == "Ativos":
            status_encontrado = produto.ativo
        elif status == "Inativos":
            status_encontrado = not produto.ativo
        else:
            status_encontrado = True

        if nome_encontrado and status_encontrado:
            produtos_filtrados.append(produto)

    produtos = produtos_filtrados

    if ordenacao == "Menor estoque primeiro":
        produtos.sort(
            key=lambda produto: produto.quantidade_estoque
        )

    elif ordenacao == "Maior estoque primeiro":
        produtos.sort(
            key=lambda produto: produto.quantidade_estoque,
            reverse=True
        )

    elif ordenacao == "Nome (A-Z)":
        produtos.sort(
            key=lambda produto: normalizar_texto(produto.nome)
        )

    elif ordenacao == "Nome (Z-A)":
        produtos.sort(
            key=lambda produto: normalizar_texto(produto.nome),
            reverse=True
        )

    if not produtos:
        st.info("Nenhum produto encontrado.")
        return

    col_nome, col_preco, col_estoque, col_status, col_botao = st.columns(
        [3, 1, 1, 1, 2]
    )

    col_nome.write("**Nome**")
    col_preco.write("**Preço**")
    col_estoque.write("**Estoque**")
    col_status.write("**Status**")
    col_botao.write("**Ações**")

    for produto in produtos:
        col_nome, col_preco, col_estoque, col_status, col_botao = st.columns(
            [3, 1, 1, 1, 2]
        )

        col_nome.write(produto.nome)
        col_preco.write(f"R$ {produto.preco:.2f}")
        col_estoque.write(produto.quantidade_estoque)

        if produto.ativo:
            col_status.write("🟢")
        else:
            col_status.write("🔴")

        col_botao.button(
            "Ver detalhes",
            key=f"ver_{produto.id}",
            on_click=selecionar_produto,
            args=(produto.id,),
        )


listar_produtos()
