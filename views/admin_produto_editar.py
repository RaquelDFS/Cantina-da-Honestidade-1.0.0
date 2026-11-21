
import streamlit as st

from database.inicializar import conectar
from views.mensagens import avisar
from controllers.validacoes import TAMANHO_FORNECEDOR, TAMANHO_NOME_PRODUTO


def tela_admin_produto_editar():

    # ==========================================
    # 1. IDENTIFICAÇÃO DO PRODUTO
    # ==========================================

    st.title("Editar Produto")

    id_produto = st.session_state.get("id_produto_editar")

    if not id_produto:
        st.warning("Nenhum produto foi selecionado para edição.")

        if st.button("Voltar", use_container_width=True):
            st.session_state.pagina = "admin_produtos_visualizar"
            st.rerun()

        return

    conexao = conectar()

    if not conexao:
        st.error("Não foi possível conectar ao banco de dados.")
        return

    cursor = conexao.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT *
            FROM produtos
            WHERE id_produto = %s
        """, (id_produto,))

        produto = cursor.fetchone()

        if not produto:
            st.error("Produto não encontrado.")
            return

        st.write(f"Editando: **{produto['nome']}**")
        st.divider()

        # ==========================================
        # 2. INFORMAÇÕES DO PRODUTO
        # ==========================================

        st.subheader("Informações do produto")

        nome = st.text_input(
            "Nome do produto *",
            value=produto["nome"] or "",
            max_chars=TAMANHO_NOME_PRODUTO
        )

        descricao = st.text_area(
            "Descrição",
            value=produto["descricao"] or "",
            max_chars=500
        )

        # ==========================================
        # 3. FORMAÇÃO DE PREÇO
        # ==========================================

        st.divider()
        st.subheader("Formação de preço")

        valor_compra = st.number_input(
            "Valor de compra unitário (R$)",
            min_value=0.01,
            value=max(
                0.01,
                float(produto["valor_compra_unitario_atual"])
            ),
            step=0.01,
            format="%.2f"
        )

        percentual = st.number_input(
            "Percentual de contribuição (%)",
            min_value=0.0,
            value=max(
                0.0,
                float(produto["percentual_contribuicao"])
            ),
            step=0.5,
            format="%.2f",
            help=(
                "Informe um percentual igual ou superior a 0%. "
                "Valores acima de 100% são permitidos."
            )
        )

        # Cálculo automático do preço final
        preco_final = valor_compra * (1 + percentual / 100)

        st.info(
            f"**Preço final calculado: R$ {preco_final:.2f}**"
        )

        # ==========================================
        # 4. ESTOQUE E FORNECEDOR
        # ==========================================

        st.divider()
        st.subheader("Estoque e fornecedor")

        quantidade = st.number_input(
            "Quantidade em estoque",
            min_value=0,
            value=max(
                0,
                int(produto["quantidade_estoque"])
            ),
            step=1
        )

        fornecedor = st.text_input(
            "Fornecedor atual",
            value=produto["fornecedor_atual"] or "",
            max_chars=TAMANHO_FORNECEDOR
        )

        status_atual = produto["status"]

        status = st.selectbox(
            "Status do produto",
            options=["ativo", "inativo"],
            index=0 if status_atual == "ativo" else 1,
            format_func=lambda x: x.capitalize()
        )

        # ==========================================
        # 5. AÇÕES
        # ==========================================

        st.divider()

        col_salvar, col_cancelar = st.columns(2)

        with col_salvar:
            salvar = st.button(
                "Salvar alterações",
                use_container_width=True
            )

        with col_cancelar:
            cancelar = st.button(
                "Cancelar",
                use_container_width=True
            )

        if cancelar:
            st.session_state.pagina = "admin_produtos_visualizar"
            st.rerun()

        # ==========================================
        # 6. VALIDAÇÕES E ATUALIZAÇÃO
        # ==========================================

        if salvar:

            if not nome.strip():
                st.warning("O nome do produto é obrigatório.")

            elif valor_compra <= 0:
                st.warning(
                    "O valor de compra deve ser maior que zero."
                )

            elif percentual < 0:
                st.warning(
                    "O percentual de contribuição não pode ser negativo."
                )

            elif quantidade == 0 and status == "ativo":
                st.warning(
                    "Um produto sem estoque não pode ficar ativo."
                )

            else:

                # Define o status e o motivo da inativação
                if quantidade == 0:
                    status = "inativo"
                    motivo_inativacao = "estoque_zero"

                elif status == "inativo":
                    motivo_inativacao = "manual"

                else:
                    motivo_inativacao = None

                try:

                    cursor.execute("""
                        UPDATE produtos
                        SET
                            nome = %s,
                            descricao = %s,
                            valor_compra_unitario_atual = %s,
                            percentual_contribuicao = %s,
                            preco_minimo_contribuicao = %s,
                            quantidade_estoque = %s,
                            fornecedor_atual = %s,
                            status = %s,
                            motivo_inativacao = %s
                        WHERE id_produto = %s
                    """, (
                        nome.strip(),
                        descricao.strip(),
                        valor_compra,
                        percentual,
                        preco_final,
                        quantidade,
                        fornecedor.strip(),
                        status,
                        motivo_inativacao,
                        id_produto
                    ))

                    conexao.commit()

                    # Mostrada na listagem, depois do rerun.
                    avisar(
                        f"Produto '{nome.strip()}' atualizado com sucesso!"
                    )

                    del st.session_state["id_produto_editar"]

                    st.session_state.pagina = "admin_produtos_visualizar"
                    st.rerun()

                except Exception as erro:
                    conexao.rollback()
                    print(f"Erro ao atualizar produto: {erro}")

                    st.error(
                        "Não foi possível salvar as alterações. "
                        "Tente novamente."
                    )

    finally:
        cursor.close()
        conexao.close()
