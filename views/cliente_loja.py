import streamlit as st
from decimal import Decimal

from database.inicializar import conectar


def dinheiro(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def atualizar_quantidade_carrinho(codigo):
    chave = f"carrinho_quantidade_{codigo}"

    quantidade = int(st.session_state[chave])

    carrinho = st.session_state["carrinho_p01"]

    if codigo in carrinho:
        carrinho[codigo] = quantidade


def tela_cliente_loja():

    usuario = st.session_state.get("usuario")

    if not usuario or usuario.get("perfil") != "cliente":
        st.error("Acesso permitido somente para clientes.")
        return

    st.title("Loja da Cantina")

    st.caption("Escolha os produtos e acompanhe seu carrinho ao lado.")

    st.markdown(
        """
        <style>
        @media (min-width: 900px) {
            div[data-testid="stHorizontalBlock"]:has(
                .st-key-painel_carrinho_p02
            ) {
                align-items: flex-start;
            }

            div[data-testid="stColumn"]:has(
                .st-key-painel_carrinho_p02
            ) {
                position: sticky;
                top: 20px;
                align-self: flex-start;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    conexao = conectar()

    if conexao is None:
        st.error("Não foi possível consultar os produtos.")
        return

    cursor = None

    try:

        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT
                id_produto,
                nome,
                descricao,
                preco_minimo_contribuicao,
                quantidade_estoque,
                status
            FROM produtos
            ORDER BY nome, id_produto
            """)

        produtos = cursor.fetchall()

    except Exception:
        st.error("Ocorreu um erro ao carregar a loja.")
        return

    finally:

        if cursor is not None:
            cursor.close()

        conexao.close()

    carrinho = st.session_state.setdefault("carrinho_p01", {})

    produtos_por_codigo = {int(produto["id_produto"]): produto for produto in produtos}

    produtos_disponiveis = [
        produto
        for produto in produtos
        if produto["status"] == "ativo" and int(produto["quantidade_estoque"]) > 0
    ]


    coluna_produtos, coluna_carrinho = st.columns([1.8, 1], gap="large")

    with coluna_produtos:

        st.subheader("Produtos disponíveis")

        busca = st.text_input(
            "Buscar produto",
            placeholder="Digite o nome do produto...",
            key="busca_produto_p01",
        )

        termo_busca = busca.strip().casefold()

        produtos_filtrados = [
            produto
            for produto in produtos_disponiveis
            if termo_busca in produto["nome"].casefold()
        ]

        if not produtos_disponiveis:

            st.info("Nenhum produto disponível no momento.")

        elif not produtos_filtrados:

            st.info("Nenhum produto encontrado para essa pesquisa.")

        for produto in produtos_filtrados:

            codigo = int(produto["id_produto"])

            preco = Decimal(str(produto["preco_minimo_contribuicao"]))

            estoque = int(produto["quantidade_estoque"])

            with st.container(border=True):

                st.markdown(f"**{produto['nome']}**")

                if produto["descricao"]:
                    st.write(produto["descricao"])

                st.write(
                    f"Contribuição mínima: "
                    f"**{dinheiro(preco)}** "
                    f"| Disponíveis: {estoque}"
                )

                quantidade = st.number_input(
                    "Quantidade",
                    min_value=1,
                    max_value=estoque,
                    value=1,
                    step=1,
                    key=f"loja_quantidade_{codigo}",
                )

                if st.button(
                    "Adicionar ao carrinho",
                    key=f"loja_adicionar_{codigo}",
                    use_container_width=True,
                ):

                    atual = int(carrinho.get(codigo, 0))

                    nova_quantidade = atual + int(quantidade)

                    if nova_quantidade > estoque:

                        st.warning(
                            "A quantidade solicitada ultrapassa "
                            "o estoque disponível."
                        )

                    else:

                        carrinho[codigo] = nova_quantidade

                        # Sincroniza o campo do carrinho.
                        st.session_state[f"carrinho_quantidade_{codigo}"] = (
                            nova_quantidade
                        )

                        st.rerun()


    with coluna_carrinho:

        with st.container(key="painel_carrinho_p02", border=True):

            st.subheader("🛒 Meu carrinho")

            if not carrinho:

                st.info("Seu carrinho está vazio.")

            else:

                total_minimo = Decimal("0.00")

                pedido_valido = True


                with st.container(height=320, border=False):

                    for codigo, quantidade in list(carrinho.items()):

                        codigo = int(codigo)

                        quantidade = int(quantidade)

                        produto = produtos_por_codigo.get(codigo)

                        # Produto excluído do banco.
                        if produto is None:

                            pedido_valido = False

                            st.error(
                                f"O produto de código {codigo} "
                                "não está mais disponível."
                            )

                            if st.button(
                                "Remover produto",
                                key=f"remover_indisponivel_{codigo}",
                                use_container_width=True,
                            ):

                                del carrinho[codigo]

                                st.rerun()

                            st.divider()

                            continue

                        nome = produto["nome"]

                        preco = Decimal(str(produto["preco_minimo_contribuicao"]))

                        estoque = int(produto["quantidade_estoque"])

                        ativo = produto["status"] == "ativo"


                        st.markdown(f"**{nome}**")

                        st.caption(f"{dinheiro(preco)} por unidade")

                        chave_quantidade = f"carrinho_quantidade_{codigo}"

                        if chave_quantidade not in st.session_state:

                            st.session_state[chave_quantidade] = quantidade

                        coluna_qtd, coluna_remover = st.columns([2, 1])

                        with coluna_qtd:

                            st.number_input(
                                "Quantidade",
                                min_value=1,
                                step=1,
                                key=chave_quantidade,
                                on_change=(atualizar_quantidade_carrinho),
                                args=(codigo,),
                            )

                        with coluna_remover:

                            st.write("")

                            if st.button(
                                "✕",
                                key=f"carrinho_remover_{codigo}",
                                help="Remover produto",
                                use_container_width=True,
                            ):

                                del carrinho[codigo]

                                st.session_state.pop(chave_quantidade, None)

                                st.rerun()

                        # A quantidade pode ter sido
                        # alterada pelo cliente.
                        quantidade = int(carrinho[codigo])

                        subtotal = preco * quantidade

                        total_minimo += subtotal

                        st.caption(f"Subtotal: {dinheiro(subtotal)}")


                        if not ativo:

                            pedido_valido = False

                            st.warning("Produto inativo. " "Remova-o do carrinho.")

                        elif estoque <= 0:

                            pedido_valido = False

                            st.warning("Produto sem estoque disponível.")

                        elif quantidade > estoque:

                            pedido_valido = False

                            st.warning(
                                f"Estoque disponível: "
                                f"{estoque} unidade(s). "
                                "Reduza a quantidade."
                            )

                        st.divider()


                st.metric("Valor mínimo", dinheiro(total_minimo))

                if "adicional_compra_p02" not in st.session_state:

                    st.session_state["adicional_compra_p02"] = "0.00"

                if "contribuicao_adicional_p01" not in st.session_state:

                    st.session_state["contribuicao_adicional_p01"] = float(
                        st.session_state["adicional_compra_p02"]
                    )

                adicional = st.number_input(
                    "Contribuição adicional (R$)",
                    min_value=0.0,
                    step=0.50,
                    format="%.2f",
                    key="contribuicao_adicional_p01",
                )

                adicional_decimal = Decimal(str(adicional)).quantize(Decimal("0.01"))

                st.session_state["adicional_compra_p02"] = str(adicional_decimal)

                total = total_minimo + adicional_decimal

                st.write(f"**Total previsto: {dinheiro(total)}**")



                if not pedido_valido:

                    st.warning(
                        "Existem produtos indisponíveis ou "
                        "quantidades superiores ao estoque. "
                        "Ajuste o carrinho para continuar."
                    )

                if st.button(
                    "Continuar para confirmação",
                    disabled=not pedido_valido,
                    use_container_width=True,
                ):

                    st.session_state["adicional_compra_p02"] = str(adicional_decimal)

                    st.session_state.pagina = "cliente_finalizar_compra"

                    st.rerun()
