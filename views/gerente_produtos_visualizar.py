import streamlit as st
from database.inicializar import conectar
from views.filtros_produtos import filtros_produtos


def tela_gerente_produtos_visualizar():

    # Verificação de acesso
    usuario = st.session_state.get("usuario")

    if not usuario or usuario.get("perfil") != "gerente":
        st.error("Acesso permitido somente para Gerentes.")
        return

    st.title("Produtos cadastrados")
    st.divider()

    # Buscar produtos no banco
    conexao = conectar()

    if conexao is None:
        st.error("Não foi possível conectar ao banco de dados.")
        return

    try:
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id_produto,
                nome,
                descricao,
                valor_compra_unitario_atual,
                percentual_contribuicao,
                preco_minimo_contribuicao,
                quantidade_estoque,
                fornecedor_atual,
                status,
                motivo_inativacao
            FROM produtos
            ORDER BY id_produto DESC
        """)

        produtos = cursor.fetchall()

        cursor.close()

    except Exception as erro:
        st.error(f"Erro ao buscar produtos: {erro}")
        return

    finally:
        conexao.close()

    # Verificar se existem produtos
    if not produtos:
        st.info("Nenhum produto cadastrado.")
        return

    # Busca e filtros
    produtos = filtros_produtos(produtos, prefixo="gerente_produtos")

    if not produtos:
        st.info("Nenhum produto encontrado com esses filtros.")
        return

    st.divider()

    # Cabeçalho da tabela
    colunas = st.columns([0.5, 1.5, 2, 1, 1, 1, 0.8, 1.5, 0.8, 1])

    titulos = [
        "ID",
        "Nome",
        "Descrição",
        "Compra",
        "Contribuição",
        "Preço mínimo",
        "Estoque",
        "Fornecedor",
        "Status",
        "Ação"
    ]

    for coluna, titulo in zip(colunas, titulos):
        coluna.markdown(f"**{titulo}**")

    st.divider()

    # Exibir produtos
    for produto in produtos:

        colunas = st.columns([0.5, 1.5, 2, 1, 1, 1, 0.8, 1.5, 0.8, 1])

        colunas[0].write(produto["id_produto"])
        colunas[1].write(produto["nome"])
        colunas[2].write(produto["descricao"] or "-")

        colunas[3].write(
            f"R$ {produto['valor_compra_unitario_atual']:.2f}"
        )

        colunas[4].write(
            f"{produto['percentual_contribuicao']:.2f}%"
        )

        colunas[5].write(
            f"R$ {produto['preco_minimo_contribuicao']:.2f}"
        )

        colunas[6].write(produto["quantidade_estoque"])
        colunas[7].write(produto["fornecedor_atual"] or "-")
        colunas[8].write(produto["status"])

        # O gerente não edita o cadastro (RN04); ele movimenta o estoque (RN05).
        if colunas[9].button(
            "Movimentar",
            key=f"movimentar_produto_{produto['id_produto']}"
        ):
            st.session_state["pagina"] = "gerente_estoque_movimentar"
            st.rerun()

        # Informações complementares
        if produto["motivo_inativacao"]:
            with st.expander(
                f"Motivo da inativação - {produto['nome']}"
            ):
                st.write(produto["motivo_inativacao"])

        st.divider()
