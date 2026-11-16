import streamlit as st
from decimal import Decimal, InvalidOperation
from database.inicializar import conectar


def tela_cliente_adicionar_credito():
    """
    Permite que o cliente logado adicione crédito à própria carteira.

    Estrutura esperada da sessão:
        st.session_state["usuario"] = {
            "id_usuario": ...,
            "perfil": "cliente",
            ...
        }
    """

    st.title("Adicionar crédito")

    # Verifica a autenticação e o perfil antes de permitir qualquer operação.
    usuario = st.session_state.get("usuario")

    if not usuario:
        st.error("É necessário fazer login para acessar esta página.")
        return

    if usuario.get("perfil") != "cliente":
        st.error("Apenas usuários do tipo cliente podem adicionar crédito.")
        return

    id_usuario = usuario.get("id_usuario")

    if not id_usuario:
        st.error("Não foi possível identificar o usuário logado.")
        return

    st.write("Adicione crédito à sua carteira.")

    with st.form("form_adicionar_credito"):
        valor_informado = st.text_input(
            "Valor do depósito (R$)",
            placeholder="Ex.: 50,00"
        )
        descricao = st.text_input(
            "Descrição (opcional)",
            max_chars=255,
            placeholder="Ex.: Depósito de crédito"
        )
        enviar = st.form_submit_button(
            "Adicionar crédito",
            use_container_width=True
        )

    if not enviar:
        return

    # Aceita valores no formato brasileiro (50,00) ou decimal (50.00).
    try:
        valor_texto = valor_informado.strip().replace(".", "").replace(",", ".")
        valor = Decimal(valor_texto).quantize(Decimal("0.01"))

        if not valor.is_finite() or valor <= 0:
            st.error("Informe um valor maior que zero.")
            return
    except (InvalidOperation, ValueError):
        st.error("Informe um valor válido. Exemplo: 50,00.")
        return

    conexao = None
    cursor = None

    try:
        conexao = conectar()

        if conexao is None:
            st.error("Não foi possível conectar ao banco de dados.")
            return

        cursor = conexao.cursor(dictionary=True)

        # Inicia uma transação para atualizar o saldo e registrar a movimentação
        # como uma única operação.
        conexao.start_transaction()

        # A carteira é localizada pelo ID do usuário da sessão, nunca por um
        # ID informado pelo formulário.
        cursor.execute(
            """
            SELECT id_carteira, saldo_atual
            FROM carteiras
            WHERE id_usuario = %s
            FOR UPDATE
            """,
            (id_usuario,)
        )
        carteira = cursor.fetchone()

        if not carteira:
            conexao.rollback()
            st.error("Não foi encontrada uma carteira para este cliente.")
            return

        id_carteira = carteira["id_carteira"]

        cursor.execute(
            """
            UPDATE carteiras
            SET saldo_atual = saldo_atual + %s
            WHERE id_carteira = %s
              AND id_usuario = %s
            """,
            (valor, id_carteira, id_usuario)
        )

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
            VALUES (%s, NULL, %s, 'entrada', %s, %s)
            """,
            (
                id_carteira,
                id_usuario,
                valor,
                descricao.strip() or "Depósito de crédito"
            )
        )

        conexao.commit()

        st.success(f"Crédito de R$ {valor:,.2f} adicionado à sua carteira.")

        # Atualiza a página para exibir o saldo atualizado, caso ele seja
        # apresentado em outro componente da aplicação.
        st.rerun()

    except Exception as erro:
        if conexao:
            conexao.rollback()
        st.error(f"Não foi possível adicionar o crédito: {erro}")

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()
