
import unicodedata

import streamlit as st


# Com essa quantidade ou menos, o produto conta como "estoque baixo".
ESTOQUE_BAIXO = 3

OPCOES_STATUS = {
    "todos": "Todos",
    "ativo": "Ativo",
    "inativo": "Inativo",
}

OPCOES_ESTOQUE = {
    "todos": "Todos",
    "disponivel": "Com estoque",
    "baixo": f"Estoque baixo (até {ESTOQUE_BAIXO})",
    "zerado": "Sem estoque",
}

OPCOES_ORDEM = {
    "recentes": "Mais recentes",
    "nome": "Nome (A-Z)",
    "estoque_menor": "Menor estoque",
    "preco_menor": "Menor preço",
    "preco_maior": "Maior preço",
}


# Deixa o texto em minúsculas e sem acentos, pra norlizar busca

def normalizar(texto):
    if not texto:
        return ""

    decomposto = unicodedata.normalize("NFKD", str(texto))
    sem_acento = "".join(
        letra for letra in decomposto
        if not unicodedata.combining(letra)
    )

    return sem_acento.casefold().strip()


# Devolve só os produtos que combinam com a busca e os filtros
def filtrar_produtos(produtos, termo="", status="todos", estoque="todos"):
    termo = normalizar(termo)
    resultado = []

    for produto in produtos:

        # procura o termo no nome, na descrição e no fornecedor

        if termo:
            texto_produto = " ".join([
                normalizar(produto.get("nome")),
                normalizar(produto.get("descricao")),
                normalizar(produto.get("fornecedor_atual")),
            ])

            if termo not in texto_produto:
                continue

        
        if status != "todos" and produto.get("status") != status:
            continue

        
        quantidade = int(produto.get("quantidade_estoque") or 0)

        if estoque == "disponivel" and quantidade <= 0:
            continue

        if estoque == "baixo" and not (0 < quantidade <= ESTOQUE_BAIXO):
            continue

        if estoque == "zerado" and quantidade != 0:
            continue

        resultado.append(produto)

    return resultado


# Devolve uma nova lista pelo critério escolhido
def ordenar_produtos(produtos, criterio="recentes"):
    if criterio == "nome":
        return sorted(produtos, key=lambda p: normalizar(p.get("nome")))

    if criterio == "estoque_menor":
        return sorted(produtos, key=lambda p: int(p.get("quantidade_estoque") or 0))

    if criterio == "preco_menor":
        return sorted(produtos, key=lambda p: p.get("preco_minimo_contribuicao") or 0)

    if criterio == "preco_maior":
        return sorted(
            produtos,
            key=lambda p: p.get("preco_minimo_contribuicao") or 0,
            reverse=True,
        )

    #  maior id primeiro
    return sorted(produtos, key=lambda p: p.get("id_produto") or 0, reverse=True)


# Volta todos os campos de filtro ao valor padrão

def _limpar_filtros(prefixo):
    st.session_state[f"{prefixo}_busca"] = ""
    st.session_state[f"{prefixo}_status"] = "todos"
    st.session_state[f"{prefixo}_estoque"] = "todos"
    st.session_state[f"{prefixo}_ordem"] = "recentes"


# lista filtrada.

def filtros_produtos(produtos, prefixo):
    busca = st.text_input(
        "Buscar produto",
        placeholder="Digite nome, descrição ou fornecedor...",
        max_chars=50,
        key=f"{prefixo}_busca",
    )

    col_status, col_estoque, col_ordem = st.columns(3)

    with col_status:
        status = st.selectbox(
            "Status",
            options=list(OPCOES_STATUS),
            format_func=lambda opcao: OPCOES_STATUS[opcao],
            key=f"{prefixo}_status",
        )

    with col_estoque:
        estoque = st.selectbox(
            "Estoque",
            options=list(OPCOES_ESTOQUE),
            format_func=lambda opcao: OPCOES_ESTOQUE[opcao],
            key=f"{prefixo}_estoque",
        )

    with col_ordem:
        ordem = st.selectbox(
            "Ordenar por",
            options=list(OPCOES_ORDEM),
            format_func=lambda opcao: OPCOES_ORDEM[opcao],
            key=f"{prefixo}_ordem",
        )

    st.button(
        "Limpar filtros",
        on_click=_limpar_filtros,
        args=(prefixo,),
        key=f"{prefixo}_limpar",
    )

    filtrados = filtrar_produtos(produtos, busca, status, estoque)
    filtrados = ordenar_produtos(filtrados, ordem)

    st.caption(f"Mostrando {len(filtrados)} de {len(produtos)} produtos")

    return filtrados
