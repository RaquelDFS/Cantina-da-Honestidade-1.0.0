import streamlit as st
from database.inicializar import conectar


def tela_gerente_estoque_movimentar():

    # ==========================================
    # 1. IDENTIFICAÇÃO E PERMISSÃO
    # ==========================================

    st.title("Movimentação de Estoque")

    usuario = st.session_state.get("usuario")

    if not usuario or usuario.get("perfil") != "gerente":
        st.error("Acesso não autorizado.")
        return

    # ==========================================
    # 2. MENSAGEM APÓS MOVIMENTAÇÃO
    # ==========================================

    resultado_movimentacao = st.session_state.pop(
        "resultado_movimentacao_estoque", None
    )

    if resultado_movimentacao:
        st.success("Movimentação registrada com sucesso!")

        st.write(
            f"**Estoque anterior:** " f"{resultado_movimentacao['estoque_anterior']}"
        )
        st.write(
            f"**Quantidade movimentada:** " f"{resultado_movimentacao['quantidade']}"
        )
        st.write(f"**Novo estoque:** " f"{resultado_movimentacao['novo_estoque']}")

        st.toast(
            "Movimentação registrada com sucesso!",
            icon="✅",
        )

    # ==========================================
    # 3. BUSCAR PRODUTOS
    # ==========================================

    conexao = conectar()

    if not conexao:
        st.error("Não foi possível conectar ao banco de dados.")
        return

    try:
        cursor = conexao.cursor(dictionary=True)

        try:
            cursor.execute("""
                SELECT
                    id_produto,
                    nome,
                    quantidade_estoque,
                    status,
                    motivo_inativacao
                FROM produtos
                ORDER BY nome
            """)

            produtos = cursor.fetchall()

        finally:
            cursor.close()

    except Exception as erro:
        st.error(f"Erro ao consultar produtos: {erro}")
        return

    finally:
        conexao.close()

    if not produtos:
        st.warning("Não existem produtos cadastrados.")
        return

    produtos_por_id = {produto["id_produto"]: produto for produto in produtos}

    # ==========================================
    # 4. SELEÇÃO DO PRODUTO
    # ==========================================

    st.subheader("Produto")

    ids_produtos = list(produtos_por_id.keys())

    id_preselecionado = st.session_state.pop("id_produto_movimentar", None)

    indice_inicial = 0

    if id_preselecionado in produtos_por_id:
        indice_inicial = ids_produtos.index(id_preselecionado)

    id_produto = st.selectbox(
        "Selecione o produto",
        options=ids_produtos,
        index=indice_inicial,
        format_func=lambda id: produtos_por_id[id]["nome"],
        key="produto_movimentacao",
    )

    produto = produtos_por_id[id_produto]

    st.write(f"**Estoque atual:** " f"{produto['quantidade_estoque']} unidades")

    st.write(f"**Status:** {produto['status'].capitalize()}")

    st.divider()

    # ==========================================
    # 5. TIPO DE MOVIMENTAÇÃO
    # ==========================================

    st.subheader("Dados da movimentação")

    operacao = st.selectbox(
        "Tipo de operação",
        options=[
            "Entrada por reposição",
            "Saída por avaria",
            "Ajuste de inventário",
        ],
    )

    tipo = None
    motivo = None

    if operacao == "Entrada por reposição":
        tipo = "entrada"
        motivo = "reposicao"

    elif operacao == "Saída por avaria":
        tipo = "saída"
        motivo = "avaria"

    else:
        motivo = "ajuste"

        direcao_ajuste = st.radio(
            "Direção do ajuste",
            options=["Aumentar estoque", "Diminuir estoque"],
            horizontal=True,
        )

        if direcao_ajuste == "Aumentar estoque":
            tipo = "entrada"
        else:
            tipo = "saída"

    quantidade = st.number_input(
        "Quantidade",
        min_value=1,
        step=1,
    )

    # ==========================================
    # 6. DADOS ESPECÍFICOS
    # ==========================================

    fornecedor = None
    valor_compra = None
    custo_total = None

    if operacao == "Entrada por reposição":

        st.subheader("Dados da reposição")

        fornecedor = st.text_input("Fornecedor")

        valor_compra = st.number_input(
            "Valor de compra unitário (R$)",
            min_value=0.01,
            step=0.01,
            format="%.2f",
        )

        custo_total = quantidade * valor_compra

        st.info(f"**Custo total da reposição: R$ {custo_total:.2f}**")

    descricao = st.text_area(
        (
            "Justificativa do ajuste (obrigatória)"
            if motivo == "ajuste"
            else "Descrição da movimentação (opcional)"
        ),
        max_chars=255,
    )

    # ==========================================
    # 7. PRÉVIA DO NOVO ESTOQUE
    # ==========================================

    estoque_exibido = produto["quantidade_estoque"]

    if tipo == "entrada":
        estoque_previsto = estoque_exibido + quantidade
    else:
        estoque_previsto = estoque_exibido - quantidade

    st.divider()

    st.subheader("Prévia da movimentação")

    col_atual, col_movimento, col_final = st.columns(3)

    with col_atual:
        st.metric("Estoque atual", estoque_exibido)

    with col_movimento:
        sinal = "+" if tipo == "entrada" else "-"
        st.metric("Movimentação", f"{sinal}{quantidade}")

    with col_final:
        st.metric("Estoque previsto", estoque_previsto)

    if estoque_previsto < 0:
        st.warning("A quantidade informada é maior que o estoque disponível.")

    # ==========================================
    # 8. REGISTRAR MOVIMENTAÇÃO
    # ==========================================

    if st.button(
        "Registrar movimentação",
        use_container_width=True,
    ):

        if motivo == "ajuste" and not descricao.strip():
            st.warning("Informe a justificativa do ajuste de inventário.")
            return

        if operacao == "Entrada por reposição":

            if not fornecedor.strip():
                st.warning("Informe o fornecedor.")
                return

            if valor_compra <= 0:
                st.warning("O valor de compra deve ser maior que zero.")
                return

        conexao = conectar()

        if not conexao:
            st.error("Não foi possível conectar ao banco de dados.")
            return

        cursor = conexao.cursor(dictionary=True)
        movimentacao_confirmada = False

        try:

            # Bloqueia o produto durante a movimentação.
            cursor.execute(
                """
                SELECT
                    quantidade_estoque,
                    status,
                    motivo_inativacao
                FROM produtos
                WHERE id_produto = %s
                FOR UPDATE
                """,
                (id_produto,),
            )

            produto_atual = cursor.fetchone()

            if not produto_atual:
                st.error("Produto não encontrado.")
                conexao.rollback()
                return

            estoque_atual = produto_atual["quantidade_estoque"]

            # Valida o saldo atualizado dentro da transação.
            if tipo == "saída" and quantidade > estoque_atual:
                st.warning(
                    "Estoque insuficiente. "
                    f"Saldo disponível: {estoque_atual} unidades."
                )
                conexao.rollback()
                return

            # Calcula o novo estoque.
            if tipo == "entrada":
                novo_estoque = estoque_atual + quantidade
            else:
                novo_estoque = estoque_atual - quantidade

            # Atualiza o status conforme o estoque.
            novo_status = produto_atual["status"]
            novo_motivo = produto_atual["motivo_inativacao"]

            if novo_estoque == 0:
                novo_status = "inativo"
                novo_motivo = "estoque_zero"

            elif novo_status == "inativo" and novo_motivo == "estoque_zero":
                novo_status = "ativo"
                novo_motivo = None

            # Registra a movimentação no histórico.
            cursor.execute(
                """
                INSERT INTO movimentacoes_estoque (
                    id_produto,
                    id_usuario_responsavel,
                    tipo,
                    motivo,
                    quantidade,
                    valor_compra_unitario_registrado,
                    custo_total,
                    fornecedor,
                    descricao
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    id_produto,
                    usuario["id_usuario"],
                    tipo,
                    motivo,
                    quantidade,
                    valor_compra,
                    custo_total,
                    fornecedor,
                    descricao.strip() or None,
                ),
            )

            # Atualiza o saldo do produto.
            cursor.execute(
                """
                UPDATE produtos
                SET
                    quantidade_estoque = %s,
                    status = %s,
                    motivo_inativacao = %s
                WHERE id_produto = %s
                """,
                (
                    novo_estoque,
                    novo_status,
                    novo_motivo,
                    id_produto,
                ),
            )

            conexao.commit()

            # Guarda o resultado para exibir após atualizar a tela.
            st.session_state["resultado_movimentacao_estoque"] = {
                "estoque_anterior": estoque_atual,
                "quantidade": quantidade,
                "novo_estoque": novo_estoque,
            }

            movimentacao_confirmada = True

        except Exception as erro:
            conexao.rollback()
            st.error(f"Erro ao registrar movimentação: {erro}")

        finally:
            cursor.close()
            conexao.close()

        if movimentacao_confirmada:
            st.rerun()
