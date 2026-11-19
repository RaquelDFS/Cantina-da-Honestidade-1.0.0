import json
from decimal import Decimal, ROUND_HALF_UP

import streamlit as st

from database.inicializar import conectar

CENTAVO = Decimal("0.01")


def arredondar(valor):
    return Decimal(str(valor)).quantize(CENTAVO, rounding=ROUND_HALF_UP)


def dinheiro(valor):
    return (
        f"R$ {arredondar(valor):,.2f}".replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def obter_id_usuario(usuario):
    return usuario.get("id_usuario")


def distribuir_adicional(itens, adicional):
    """
    Distribui a contribuição adicional proporcionalmente
    ao subtotal mínimo de cada produto.

    A última linha recebe o ajuste dos centavos para
    garantir que a soma seja exatamente igual ao total.
    """

    total_minimo = sum((item["subtotal_minimo"] for item in itens), Decimal("0.00"))

    restante = adicional

    for indice, item in enumerate(itens):

        if indice == len(itens) - 1:
            parcela = restante

        else:
            proporcao = item["subtotal_minimo"] / total_minimo

            parcela = arredondar(adicional * proporcao)
            restante -= parcela

        item["valor_adicional"] = parcela

        item["valor_total_pago"] = item["subtotal_minimo"] + parcela

        item["valor_unitario_efetivo"] = (
            item["valor_total_pago"] / item["quantidade"]
        ).quantize(CENTAVO, rounding=ROUND_HALF_UP)

    return itens


def consultar_confirmacao(id_usuario, carrinho):
    conexao = conectar()

    if conexao is None:
        raise ValueError("Não foi possível conectar ao banco de dados.")

    cursor = None

    try:
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT saldo_atual
            FROM carteiras
            WHERE id_usuario = %s
            """,
            (id_usuario,),
        )

        carteira = cursor.fetchone()

        if carteira is None:
            raise ValueError("O cliente não possui uma carteira cadastrada.")

        itens = []

        for codigo in sorted(carrinho):

            cursor.execute(
                """
                SELECT
                    id_produto,
                    nome,
                    status,
                    quantidade_estoque,
                    valor_compra_unitario_atual,
                    preco_minimo_contribuicao
                FROM produtos
                WHERE id_produto = %s
                """,
                (codigo,),
            )

            produto = cursor.fetchone()

            if produto is None:
                raise ValueError(f"O produto de código {codigo} não existe.")

            quantidade = int(carrinho[codigo])

            if quantidade <= 0:
                raise ValueError("O carrinho contém uma quantidade inválida.")

            if produto["status"] != "ativo":
                raise ValueError(f"O produto {produto['nome']} está inativo.")

            if quantidade > int(produto["quantidade_estoque"]):
                raise ValueError(f"Estoque insuficiente para " f"{produto['nome']}.")

            custo = arredondar(produto["valor_compra_unitario_atual"])

            preco = arredondar(produto["preco_minimo_contribuicao"])

            if custo <= 0 or preco < custo:
                raise ValueError(
                    f"O produto {produto['nome']} possui " "um valor mínimo inválido."
                )

            itens.append(
                {
                    "id_produto": int(produto["id_produto"]),
                    "nome": produto["nome"],
                    "quantidade": quantidade,
                    "preco_minimo": preco,
                    "subtotal_minimo": preco * quantidade,
                }
            )

        return {"itens": itens, "saldo": arredondar(carteira["saldo_atual"])}

    finally:
        if cursor is not None:
            cursor.close()

        conexao.close()


def processar_compra(id_usuario, carrinho, adicional, valores_confirmados):
    """
    Executa a compra em uma única transação.

    Em caso de erro, nenhuma alteração é confirmada.
    """

    conexao = conectar()

    if conexao is None:
        raise ValueError("Não foi possível conectar ao banco de dados.")

    cursor = None
    transacao_iniciada = False

    try:
        conexao.start_transaction()
        transacao_iniciada = True

        cursor = conexao.cursor(dictionary=True)

        # ==========================================
        # 1. BLOQUEAR CARTEIRA
        # ==========================================

        cursor.execute(
            """
            SELECT id_carteira, saldo_atual
            FROM carteiras
            WHERE id_usuario = %s
            FOR UPDATE
            """,
            (id_usuario,),
        )

        carteira = cursor.fetchone()

        if carteira is None:
            raise ValueError("Carteira não encontrada.")

        # ==========================================
        # 2. BLOQUEAR E VALIDAR PRODUTOS
        # ==========================================

        itens = []

        for codigo in sorted(carrinho):

            cursor.execute(
                """
                SELECT
                    id_produto,
                    nome,
                    status,
                    quantidade_estoque,
                    valor_compra_unitario_atual,
                    preco_minimo_contribuicao
                FROM produtos
                WHERE id_produto = %s
                FOR UPDATE
                """,
                (codigo,),
            )

            produto = cursor.fetchone()

            if produto is None:
                raise ValueError("Um produto do carrinho não foi encontrado.")

            quantidade = int(carrinho[codigo])

            if quantidade <= 0:
                raise ValueError("Quantidade inválida no carrinho.")

            if produto["status"] != "ativo":
                raise ValueError(f"O produto {produto['nome']} está inativo.")

            estoque = int(produto["quantidade_estoque"])

            if quantidade > estoque:
                raise ValueError(f"Estoque insuficiente para " f"{produto['nome']}.")

            custo = arredondar(produto["valor_compra_unitario_atual"])

            preco = arredondar(produto["preco_minimo_contribuicao"])

            if custo <= 0 or preco < custo:
                raise ValueError(
                    f"O produto {produto['nome']} possui " "um valor mínimo inválido."
                )

            # Impede que uma alteração de preço passe
            # despercebida durante a confirmação.
            if (
                codigo not in valores_confirmados
                or preco != valores_confirmados[codigo]
            ):
                raise ValueError(
                    f"O preço de {produto['nome']} foi "
                    "alterado. Confira o pedido novamente."
                )

            itens.append(
                {
                    "id_produto": codigo,
                    "nome": produto["nome"],
                    "quantidade": quantidade,
                    "estoque_anterior": estoque,
                    "preco_minimo": preco,
                    "subtotal_minimo": preco * quantidade,
                }
            )

        if not itens:
            raise ValueError("O carrinho está vazio.")

        # ==========================================
        # 3. CALCULAR E VALIDAR TOTAL
        # ==========================================

        total_minimo = sum((item["subtotal_minimo"] for item in itens), Decimal("0.00"))

        if adicional < 0:
            raise ValueError("A contribuição adicional não pode " "ser negativa.")

        total = arredondar(total_minimo + adicional)

        saldo = arredondar(carteira["saldo_atual"])

        if saldo < total:
            raise ValueError("Saldo insuficiente para concluir a compra.")

        itens = distribuir_adicional(itens, adicional)

        # ==========================================
        # 4. REGISTRAR VENDA
        # ==========================================

        cursor.execute(
            """
            INSERT INTO vendas (
                id_cliente,
                data_hora,
                valor_total
            )
            VALUES (%s, NOW(), %s)
            """,
            (id_usuario, total),
        )

        id_venda = cursor.lastrowid

        # ==========================================
        # 5. REGISTRAR ITENS E BAIXAR ESTOQUE
        # ==========================================

        for item in itens:

            cursor.execute(
                """
                INSERT INTO itens_venda (
                    id_venda,
                    id_produto,
                    quantidade,
                    preco_minimo_unitario_historico,
                    valor_total_pago,
                    valor_unitario_efetivo
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    id_venda,
                    item["id_produto"],
                    item["quantidade"],
                    item["preco_minimo"],
                    item["valor_total_pago"],
                    item["valor_unitario_efetivo"],
                ),
            )

            id_item_venda = cursor.lastrowid

            novo_estoque = item["estoque_anterior"] - item["quantidade"]

            if novo_estoque == 0:
                novo_status = "inativo"
                motivo = "estoque_zero"
            else:
                novo_status = "ativo"
                motivo = None

            cursor.execute(
                """
                UPDATE produtos
                SET
                    quantidade_estoque = %s,
                    status = %s,
                    motivo_inativacao = %s
                WHERE id_produto = %s
                """,
                (novo_estoque, novo_status, motivo, item["id_produto"]),
            )

            cursor.execute(
                """
                INSERT INTO movimentacoes_estoque (
                    id_produto,
                    id_usuario_responsavel,
                    id_item_venda,
                    tipo,
                    motivo,
                    quantidade
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    item["id_produto"],
                    id_usuario,
                    id_item_venda,
                    "saída",
                    "venda",
                    item["quantidade"],
                ),
            )

            # Registra a inativação automática.
            if novo_estoque == 0:

                alteracoes = {
                    "origem": "venda",
                    "id_venda": id_venda,
                    "motivo": "estoque_zero",
                    "quantidade_anterior": (item["estoque_anterior"]),
                    "quantidade_atual": 0,
                    "status_anterior": "ativo",
                    "status_atual": "inativo",
                }

                cursor.execute(
                    """
                    INSERT INTO historico_alteracoes_produto (
                        id_produto,
                        id_usuario_responsavel,
                        alteracoes
                    )
                    VALUES (%s, %s, %s)
                    """,
                    (item["id_produto"], id_usuario, json.dumps(alteracoes)),
                )

        # ==========================================
        # 6. DEBITAR CARTEIRA
        # ==========================================

        cursor.execute(
            """
            UPDATE carteiras
            SET saldo_atual = saldo_atual - %s
            WHERE id_carteira = %s
            """,
            (total, carteira["id_carteira"]),
        )

        # ==========================================
        # 7. REGISTRAR SAÍDA FINANCEIRA
        # ==========================================

        cursor.execute(
            """
            INSERT INTO movimentacoes_carteira (
                id_carteira,
                id_venda,
                id_usuario_responsavel,
                tipo,
                valor,
                descricao
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                carteira["id_carteira"],
                id_venda,
                id_usuario,
                "saída",
                total,
                f"Pagamento da venda #{id_venda}",
            ),
        )

        # ==========================================
        # 8. CONFIRMAR TRANSAÇÃO
        # ==========================================

        conexao.commit()
        transacao_iniciada = False

        return id_venda

    except Exception:
        if transacao_iniciada:
            conexao.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()

        conexao.close()


def tela_cliente_finalizar_compra():

    # ==========================================
    # 1. IDENTIFICAR CLIENTE
    # ==========================================

    usuario = st.session_state.get("usuario")

    if not usuario or usuario.get("perfil") != "cliente":
        st.error("Acesso permitido somente para clientes.")
        return

    id_usuario = obter_id_usuario(usuario)

    if id_usuario is None:
        st.error("Não foi possível identificar o cliente.")
        return

    st.title("Finalizar compra")
    st.caption("Confira seu pedido antes de confirmar o pagamento.")

    # ==========================================
    # 2. EXIBIR COMPRA CONCLUÍDA
    # ==========================================

    venda_concluida = st.session_state.get("venda_concluida_p02")

    if venda_concluida is not None:

        st.success("Compra realizada com sucesso!")

        st.write(f"**Número da venda:** {venda_concluida}")

        if st.button("Voltar à loja", use_container_width=True):
            del st.session_state["venda_concluida_p02"]

            st.session_state.pagina = "cliente_loja"
            st.rerun()

        return

    # ==========================================
    # 3. CONSULTAR CARRINHO
    # ==========================================

    carrinho_original = st.session_state.get("carrinho_p01", {})

    carrinho = {
        int(codigo): int(quantidade) for codigo, quantidade in carrinho_original.items()
    }

    if not carrinho:
        st.info("Seu carrinho está vazio.")

        if st.button("Voltar à loja", use_container_width=True):
            st.session_state.pagina = "cliente_loja"
            st.rerun()

        return

    try:
        adicional = arredondar(st.session_state.get("adicional_compra_p02", "0.00"))

        if adicional < 0:
            raise ValueError("A contribuição adicional é inválida.")

        confirmacao = consultar_confirmacao(id_usuario, carrinho)

    except ValueError as erro:
        st.warning(str(erro))

        if st.button("Voltar à loja"):
            st.session_state.pagina = "cliente_loja"
            st.rerun()

        return

    except Exception:
        st.error("Não foi possível carregar os dados da compra.")
        return

    itens = confirmacao["itens"]
    saldo = confirmacao["saldo"]

    # ==========================================
    # 4. APRESENTAR PRODUTOS
    # ==========================================

    st.subheader("Resumo do pedido")

    for item in itens:

        with st.container(border=True):

            st.markdown(f"**{item['nome']}**")

            st.write(f"Quantidade: {item['quantidade']}")

            st.write("Valor mínimo unitário: " f"{dinheiro(item['preco_minimo'])}")

            st.write("Subtotal: " f"**{dinheiro(item['subtotal_minimo'])}**")

    # ==========================================
    # 5. RESUMO FINANCEIRO
    # ==========================================

    total_minimo = sum((item["subtotal_minimo"] for item in itens), Decimal("0.00"))

    total = arredondar(total_minimo + adicional)

    st.divider()
    st.subheader("Resumo financeiro")

    st.write(f"Valor mínimo dos produtos: " f"**{dinheiro(total_minimo)}**")

    st.write(f"Contribuição adicional: " f"**{dinheiro(adicional)}**")

    st.write(f"Total da compra: **{dinheiro(total)}**")

    st.write(f"Saldo disponível: **{dinheiro(saldo)}**")

    saldo_suficiente = saldo >= total

    if not saldo_suficiente:
        st.warning(
            "Saldo insuficiente. Adicione créditos " "antes de confirmar a compra."
        )

    # ==========================================
    # 6. CONFIRMAR COMPRA
    # ==========================================

    st.divider()

    coluna_voltar, coluna_confirmar = st.columns(2)

    with coluna_voltar:

        if st.button("Voltar à loja", use_container_width=True):
            st.session_state.pagina = "cliente_loja"
            st.rerun()

    with coluna_confirmar:

        if st.button(
            "Confirmar compra",
            type="primary",
            disabled=not saldo_suficiente,
            use_container_width=True,
        ):

            if st.session_state.get("processando_compra_p02", False):
                st.warning("Uma compra já está em processamento.")
                return

            st.session_state["processando_compra_p02"] = True

            valores_confirmados = {
                item["id_produto"]: item["preco_minimo"] for item in itens
            }

            try:

                with st.spinner("Processando sua compra..."):

                    id_venda = processar_compra(
                        id_usuario, carrinho, adicional, valores_confirmados
                    )

                # Limpa o carrinho somente após o COMMIT.
                st.session_state["carrinho_p01"] = {}

                st.session_state["adicional_compra_p02"] = "0.00"

                st.session_state["venda_concluida_p02"] = id_venda

                st.rerun()

            except ValueError as erro:
                st.warning(str(erro))

            except Exception as erro:
                st.error(
                    "Não foi possível concluir a compra. "
                    "Nenhuma alteração foi confirmada."
                )
                st.caption(f"Detalhes técnicos: {erro}")

            finally:
                st.session_state["processando_compra_p02"] = False
