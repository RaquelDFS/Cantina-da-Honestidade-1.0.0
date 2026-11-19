
import streamlit as st
from decimal import Decimal
from database.inicializar import conectar


def dinheiro(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def tela_cliente_loja():
    usuario = st.session_state.get("usuario")

    if not usuario or usuario.get("perfil") != "cliente":
        st.error("Acesso permitido somente para clientes.")
        return

    st.title("Loja da Cantina")
    st.caption("Escolha os produtos e revise seu carrinho antes de comprar.")

    conexao = conectar()

    if conexao is None:
        st.error("Não foi possível consultar os produtos.")
        return

    try:
        cursor = conexao.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT
                    id_produto,
                    nome,
                    descricao,
                    preco_minimo_contribuicao,
                    quantidade_estoque
                FROM produtos
                WHERE status = 'ativo'
                  AND quantidade_estoque > 0
                ORDER BY nome, id_produto
            """)

            produtos = cursor.fetchall()

        finally:
            cursor.close()

    except Exception:
        st.error("Ocorreu um erro ao carregar a loja.")
        return

    finally:
        conexao.close()

    # Carrinho temporário, sem movimentação financeira.
    carrinho = st.session_state.setdefault("carrinho_p01", {})

    disponiveis = {
        int(p["id_produto"]): p
        for p in produtos
    }

    # Atualiza o carrinho conforme a disponibilidade.
    for codigo in list(carrinho):

        if codigo not in disponiveis:
            del carrinho[codigo]

        else:
            estoque = int(
                disponiveis[codigo]["quantidade_estoque"]
            )

            carrinho[codigo] = min(
                int(carrinho[codigo]),
                estoque
            )

            if carrinho[codigo] <= 0:
                del carrinho[codigo]

    st.subheader("Produtos disponíveis")

    # Busca por nome, sem alterar a consulta ao banco.
    busca = st.text_input(
        "Buscar produto",
        placeholder="Digite o nome do produto...",
        key="busca_produto_p01"
    )

    termo_busca = busca.strip().casefold()

    produtos_filtrados = [
        produto
        for produto in produtos
        if termo_busca in produto["nome"].casefold()
    ]

    if not produtos:
        st.info("Nenhum produto disponível no momento.")

    elif not produtos_filtrados:
        st.info("Nenhum produto encontrado para essa pesquisa.")

    for produto in produtos_filtrados:

        codigo = int(produto["id_produto"])

        preco = Decimal(
            str(produto["preco_minimo_contribuicao"])
        )

        estoque = int(produto["quantidade_estoque"])

        with st.container(border=True):

            st.markdown(f"**{produto['nome']}**")

            if produto["descricao"]:
                st.write(produto["descricao"])

            st.write(
                f"Contribuição mínima: **{dinheiro(preco)}** "
                f"| Disponíveis: {estoque}"
            )

            quantidade = st.number_input(
                "Quantidade",
                min_value=1,
                max_value=estoque,
                value=1,
                step=1,
                key=f"loja_quantidade_{codigo}"
            )

            if st.button(
                "Adicionar ao carrinho",
                key=f"loja_adicionar_{codigo}"
            ):

                atual = int(carrinho.get(codigo, 0))

                if atual + int(quantidade) > estoque:
                    st.warning(
                        "A quantidade solicitada ultrapassa "
                        "o estoque disponível."
                    )

                else:
                    carrinho[codigo] = atual + int(quantidade)
                    st.rerun()

    st.divider()
    st.subheader("Meu carrinho")

    if not carrinho:
        st.info("Seu carrinho está vazio.")
        return

    total_minimo = Decimal("0.00")

    for codigo, quantidade in list(carrinho.items()):

        produto = disponiveis[codigo]

        preco = Decimal(
            str(produto["preco_minimo_contribuicao"])
        )

        subtotal = preco * quantidade
        total_minimo += subtotal

        with st.container(border=True):

            st.write(
                f"**{produto['nome']}** — "
                f"{dinheiro(preco)} por unidade"
            )

            coluna_quantidade, coluna_remover = st.columns(
                [2, 1]
            )

            nova_quantidade = coluna_quantidade.number_input(
                "Quantidade no carrinho",
                min_value=1,
                max_value=int(
                    produto["quantidade_estoque"]
                ),
                value=quantidade,
                step=1,
                key=f"carrinho_quantidade_{codigo}"
            )

            if int(nova_quantidade) != quantidade:
                carrinho[codigo] = int(nova_quantidade)
                st.rerun()

            coluna_quantidade.write(
                f"Subtotal: {dinheiro(subtotal)}"
            )

            if coluna_remover.button(
                "Remover",
                key=f"carrinho_remover_{codigo}"
            ):
                del carrinho[codigo]
                st.rerun()

    st.metric(
        "Valor mínimo do carrinho",
        dinheiro(total_minimo)
    )

    st.caption(
        "Você poderá contribuir com um valor adicional. "
        "Nenhum valor será debitado agora."
    )

    adicional = st.number_input(
        "Contribuição adicional voluntária (R$)",
        min_value=0.0,
        value=0.0,
        step=0.50,
        format="%.2f",
        key="contribuicao_adicional_p01"
    )

    total = total_minimo + Decimal(
        str(adicional)
    ).quantize(Decimal("0.01"))

    st.write(
        f"**Total previsto: {dinheiro(total)}**"
    )

    st.info(
        "A confirmação da compra, a validação do saldo "
        "e a baixa de estoque serão implementadas na P02."
    )

    st.button(
        "Continuar para confirmação",
        use_container_width=True,
        disabled=True
    )
