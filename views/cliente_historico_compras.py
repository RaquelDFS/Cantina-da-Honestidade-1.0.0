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


def consultar_historico(id_usuario):
    conexao = conectar()

    if conexao is None:
        raise ValueError("Não foi possível conectar ao banco de dados.")

    cursor = None

    try:
        cursor = conexao.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                v.id_venda,
                v.data_hora,
                v.valor_total
            FROM vendas v
            WHERE v.id_cliente = %s
            ORDER BY v.data_hora DESC, v.id_venda DESC
            """,
            (id_usuario,),
        )

        vendas = cursor.fetchall()

        for venda in vendas:
            cursor.execute(
                """
                SELECT
                    iv.id_produto,
                    p.nome AS nome_produto,
                    iv.quantidade,
                    iv.preco_minimo_unitario_historico,
                    iv.valor_total_pago
                FROM itens_venda iv
                LEFT JOIN produtos p
                    ON p.id_produto = iv.id_produto
                WHERE iv.id_venda = %s
                ORDER BY iv.id_produto
                """,
                (venda["id_venda"],),
            )

            venda["itens"] = cursor.fetchall()

        return vendas

    finally:
        if cursor is not None:
            cursor.close()

        conexao.close()


def tela_cliente_historico_compras():

    # ==========================================
    # 1. IDENTIFICAR CLIENTE
    # ==========================================

    usuario = st.session_state.get("usuario")

    if not usuario or usuario.get("perfil") != "cliente":
        st.error("Acesso permitido somente para clientes.")
        return

    id_usuario = usuario.get("id_usuario")

    if id_usuario is None:
        st.error("Não foi possível identificar o cliente.")
        return

    st.title("Histórico de compras")
    st.caption("Consulte suas compras realizadas na cantina.")

    # ==========================================
    # 2. CONSULTAR HISTÓRICO
    # ==========================================

    try:
        vendas = consultar_historico(id_usuario)

    except Exception:
        st.error("Não foi possível carregar o histórico de compras.")
        return

    if not vendas:
        st.info("Você ainda não realizou nenhuma compra.")

        if st.button("Ir para a loja", use_container_width=True):
            st.session_state.pagina = "cliente_loja"
            st.rerun()

        return

    st.write(f"Total de compras realizadas: **{len(vendas)}**")

    st.divider()

    # ==========================================
    # 3. EXIBIR COMPRAS
    # ==========================================

    for venda in vendas:

        id_venda = venda["id_venda"]
        data_hora = venda["data_hora"]
        valor_total = arredondar(venda["valor_total"])
        itens = venda["itens"]

        data_formatada = data_hora.strftime("%d/%m/%Y às %H:%M")

        titulo = (
            f"Compra #{id_venda} | " f"{data_formatada} | " f"{dinheiro(valor_total)}"
        )

        with st.expander(titulo):

            st.write(f"**Data:** {data_formatada}")
            st.write(f"**Número da compra:** {id_venda}")

            st.divider()

            st.subheader("Produtos adquiridos")

            total_minimo = Decimal("0.00")
            total_itens = Decimal("0.00")

            for item in itens:

                quantidade = int(item["quantidade"])

                preco_minimo = arredondar(item["preco_minimo_unitario_historico"])

                valor_pago = arredondar(item["valor_total_pago"])

                subtotal_minimo = preco_minimo * quantidade

                total_minimo += subtotal_minimo
                total_itens += valor_pago

                nome_produto = item["nome_produto"] or f"Produto #{item['id_produto']}"

                with st.container(border=True):

                    st.markdown(f"**{nome_produto}**")

                    st.write(f"Quantidade: {quantidade}")

                    st.write("Valor mínimo unitário: " f"{dinheiro(preco_minimo)}")

                    st.write("Valor pago pelo item: " f"**{dinheiro(valor_pago)}**")

            # ==========================================
            # 4. RESUMO FINANCEIRO
            # ==========================================

            adicional = valor_total - total_minimo

            st.divider()
            st.subheader("Resumo financeiro")

            st.write("Valor mínimo dos produtos: " f"**{dinheiro(total_minimo)}**")

            st.write("Contribuição adicional: " f"**{dinheiro(adicional)}**")

            st.write(f"Total da compra: **{dinheiro(valor_total)}**")

            if total_itens != valor_total:
                st.warning(
                    "Os valores dos itens não correspondem "
                    "ao total registrado nesta compra."
                )

    st.divider()

    if st.button("Voltar à loja", use_container_width=True):
        st.session_state.pagina = "cliente_loja"
        st.rerun()
