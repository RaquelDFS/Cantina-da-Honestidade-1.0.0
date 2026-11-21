
import streamlit as st

from database.inicializar import conectar
from controllers.validacoes import TAMANHO_FORNECEDOR, TAMANHO_NOME_PRODUTO


def tela_produto_cadastro():

    usuario = st.session_state.get("usuario")

    # RN04: apenas o administrador pode cadastrar produtos.
    if not usuario or usuario.get("perfil") != "administrador":
        st.error("Apenas administradores podem cadastrar produtos.")
        return

    st.title("Cadastro de produtos")
    st.write("Preencha os dados para cadastrar um novo produto.")
    st.caption("Campos com * são obrigatórios.")

    st.divider()

    # ==========================================
    # 1. INFORMAÇÕES DO PRODUTO
    # ==========================================

    st.subheader("Informações do produto")

    nome = st.text_input(
        "Nome do produto *",
        max_chars=TAMANHO_NOME_PRODUTO,
        placeholder="Ex.: Café 250g"
    )

    descricao = st.text_area(
        "Descrição",
        max_chars=500
    )

    fornecedor = st.text_input(
        "Fornecedor atual *",
        max_chars=TAMANHO_FORNECEDOR,
        placeholder="Ex.: Atacadão"
    )

    st.divider()

    # ==========================================
    # 2. INFORMAÇÕES FINANCEIRAS E ESTOQUE
    # ==========================================

    st.subheader("Informações financeiras e estoque")

    col1, col2, col3 = st.columns(3)

    with col1:
        valor_compra = st.number_input(
            "Valor de compra unitário (R$) *",
            min_value=0.01,
            value=0.01,
            step=0.01,
            format="%.2f",
            key="valor_compra"
        )

    with col2:
        percentual = st.number_input(
            "Percentual de contribuição (%) *",
            min_value=0.0,
            max_value=999.99,
            value=0.0,
            step=0.5,
            format="%.2f",
            help=(
                "Informe um percentual entre 0% e 999,99%. "
                "Valores acima de 100% são permitidos."
            ),
            key="percentual"
        )

    with col3:
        quantidade = st.number_input(
            "Quantidade inicial em estoque *",
            min_value=1,
            value=1,
            step=1,
            key="quantidade"
        )

    # Cálculo automático do preço mínimo
    preco_minimo = valor_compra + (valor_compra * percentual / 100)

    st.metric(
        "Preço mínimo de contribuição",
        f"R$ {preco_minimo:.2f}"
    )

    st.divider()

    # ==========================================
    # 3. CADASTRO
    # ==========================================

    if st.button("Cadastrar produto", use_container_width=True):

        if not nome.strip():
            st.error("O nome do produto é obrigatório.")
            return

        if valor_compra <= 0:
            st.error("O valor de compra deve ser maior que zero.")
            return

        if percentual < 0 or percentual > 999.99:
            st.error(
                "O percentual de contribuição deve estar "
                "entre 0% e 999,99%."
            )
            return

        if quantidade <= 0:
            st.error("A quantidade inicial em estoque deve ser maior que zero.")
            return

        if not fornecedor.strip():
            st.error(
                "O fornecedor é obrigatório para registrar a entrada inicial."
            )
            return

        status = "ativo"
        motivo_inativacao = None

        conexao = conectar()

        if conexao is None:
            st.error("Não foi possível conectar ao banco.")
            return

        cursor = None

        try:
            cursor = conexao.cursor()

            # 1. Cadastrar produto
            sql = """
                INSERT INTO produtos (
                    nome,
                    descricao,
                    valor_compra_unitario_atual,
                    percentual_contribuicao,
                    preco_minimo_contribuicao,
                    quantidade_estoque,
                    fornecedor_atual,
                    status,
                    motivo_inativacao
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            valores = (
                nome.strip(),
                descricao.strip() or None,
                valor_compra,
                percentual,
                preco_minimo,
                quantidade,
                fornecedor.strip(),
                status,
                motivo_inativacao
            )

            cursor.execute(sql, valores)

            # Recuperar ID do produto cadastrado
            id_produto = cursor.lastrowid

            # 2. Registrar entrada inicial no estoque
            custo_total = quantidade * valor_compra

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
                VALUES (%s, %s, 'entrada', 'reposicao', %s, %s, %s, %s, %s)
            """, (
                id_produto,
                usuario["id_usuario"],
                quantidade,
                valor_compra,
                custo_total,
                fornecedor.strip(),
                "Cadastro inicial do produto"
            ))

            # 3. Confirmar as duas operações
            conexao.commit()

            st.success(
                f"Produto '{nome.strip()}' cadastrado com sucesso!"
            )

        except Exception as erro:
            conexao.rollback()
            print(f"Erro ao cadastrar produto: {erro}")

            st.error(
                "Não foi possível cadastrar o produto. "
                "Confira os dados e tente novamente."
            )

        finally:
            if cursor:
                cursor.close()

            conexao.close()
