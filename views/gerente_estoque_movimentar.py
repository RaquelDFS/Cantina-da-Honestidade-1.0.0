
import streamlit as st
from database.inicializar import conectar


def tela_gerente_estoque_movimentar():

    # ==========================================
    # 1. IDENTIFICAÇÃO E PERMISSÃO
    # ==========================================

    st.title("Movimentação de Estoque")

    usuario = st.session_state.usuario

    if usuario is None or usuario["perfil"] != "gerente":
        st.error("Acesso não autorizado.")
        return

    # ==========================================
    # 2. BUSCAR PRODUTOS
    # ==========================================

    conexao = conectar()

    if not conexao:
        st.error("Não foi possível conectar ao banco de dados.")
        return

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
        conexao.close()

    if not produtos:
        st.warning("Não existem produtos cadastrados.")
        return

    produtos_por_id = {
        produto["id_produto"]: produto
        for produto in produtos
    }

    # ==========================================
    # 3. SELEÇÃO DO PRODUTO
    # ==========================================

    st.subheader("Produto")

    id_produto = st.selectbox(
        "Selecione o produto",
        options=list(produtos_por_id.keys()),
        format_func=lambda id: produtos_por_id[id]["nome"]
    )

    produto = produtos_por_id[id_produto]

    st.write(
        f"**Estoque atual:** {produto['quantidade_estoque']} unidades"
    )

    st.divider()

    # ==========================================
    # 4. TIPO DE MOVIMENTAÇÃO
    # ==========================================

    st.subheader("Dados da movimentação")

    operacao = st.selectbox(
        "Tipo de operação",
        options=[
            "Entrada por reposição",
            "Saída por avaria",
            "Saída por ajuste"
        ]
    )

    quantidade = st.number_input(
        "Quantidade",
        min_value=1,
        step=1
    )

    # ==========================================
    # 5. DADOS ESPECÍFICOS DA OPERAÇÃO
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
            format="%.2f"
        )

        custo_total = quantidade * valor_compra

        st.info(
            f"**Custo total da reposição: R$ {custo_total:.2f}**"
        )

        tipo = "entrada"
        motivo = "reposicao"

    elif operacao == "Saída por avaria":

        tipo = "saída"
        motivo = "avaria"

    else:

        tipo = "saída"
        motivo = "ajuste"

    descricao = st.text_area(
        "Descrição da movimentação (opcional)"
    )

    st.divider()

    # ==========================================
    # 6. REGISTRAR MOVIMENTAÇÃO
    # ==========================================

    if st.button("Registrar movimentação", use_container_width=True):

        if operacao == "Entrada por reposição":
            if not fornecedor.strip():
                st.warning("Informe o fornecedor.")

                return

            if valor_compra <= 0:
                st.warning("O valor de compra deve ser maior que zero.")
                return

        if tipo == "saída" and quantidade > produto["quantidade_estoque"]:
            st.warning("Não existe estoque suficiente para essa saída.")
            return

        conexao = conectar()

        if not conexao:
            st.error("Não foi possível conectar ao banco de dados.")
            return

        cursor = conexao.cursor(dictionary=True)

        try:

            # Bloqueia o registro durante a movimentação
            cursor.execute("""
                SELECT
                    quantidade_estoque,
                    status,
                    motivo_inativacao
                FROM produtos
                WHERE id_produto = %s
                FOR UPDATE
            """, (id_produto,))

            produto_atual = cursor.fetchone()

            if not produto_atual:
                st.error("Produto não encontrado.")
                return

            estoque_atual = produto_atual["quantidade_estoque"]

            # Calcula o novo estoque
            if tipo == "entrada":
                novo_estoque = estoque_atual + quantidade

            else:
                novo_estoque = estoque_atual - quantidade

            # Atualiza o status automaticamente conforme o estoque
            novo_status = produto_atual["status"]
            novo_motivo = produto_atual["motivo_inativacao"]

            if novo_estoque == 0:
                novo_status = "inativo"
                novo_motivo = "estoque_zero"

            elif (
                novo_status == "inativo"
                and novo_motivo == "estoque_zero"
            ):
                novo_status = "ativo"
                novo_motivo = None

            # Registra a movimentação
            cursor.execute("""
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
            """, (
                id_produto,
                usuario["id_usuario"],
                tipo,
                motivo,
                quantidade,
                valor_compra,
                custo_total,
                fornecedor,
                descricao.strip() or None
            ))

            # Atualiza a quantidade no cadastro do produto
            cursor.execute("""
                UPDATE produtos
                SET
                    quantidade_estoque = %s,
                    status = %s,
                    motivo_inativacao = %s
                WHERE id_produto = %s
            """, (
                novo_estoque,
                novo_status,
                novo_motivo,
                id_produto
            ))

            conexao.commit()

            st.success("Movimentação registrada com sucesso!")

            st.write(f"**Estoque anterior:** {estoque_atual}")
            st.write(f"**Quantidade movimentada:** {quantidade}")
            st.write(f"**Novo estoque:** {novo_estoque}")

            st.rerun()

        except Exception as erro:
            conexao.rollback()
            st.error(f"Erro ao registrar movimentação: {erro}")

        finally:
            cursor.close()
            conexao.close()
