import streamlit as st
from database.inicializar import conectar
from views.mensagens import avisar, mostrar_aviso
from controllers.validacoes import converter_valor, formatar_moeda


# Limite por depósito, para evitar erro de digitação (ex.: 5000 em vez de 50).
VALOR_MAXIMO_DEPOSITO = 500


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
    mostrar_aviso()

    with st.form("form_adicionar_credito"):
        valor_informado = st.text_input(
            "Valor do depósito (R$)",
            placeholder="Ex.: 50,00",
            max_chars=10,
            help=f"Valor entre R$ 0,01 e {formatar_moeda(VALOR_MAXIMO_DEPOSITO)}."
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

    # Aceita 50 / 50,00 / 50.00 / 1.250,50 (antes, "50.00" virava 5000).
    valor = converter_valor(valor_informado)

    if valor is None:
        st.error("Informe um valor válido. Exemplo: 50,00.")
        return

    if valor <= 0:
        st.error("Informe um valor maior que zero.")
        return

    if valor > VALOR_MAXIMO_DEPOSITO:
        st.error(
            f"O valor máximo por depósito é {formatar_moeda(VALOR_MAXIMO_DEPOSITO)}."
        )
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

        # A mensagem é guardada e mostrada depois do rerun.
        avisar(f"Crédito de {formatar_moeda(valor)} adicionado à sua carteira.")

        # Atualiza a página para exibir o saldo atualizado, caso ele seja
        # apresentado em outro componente da aplicação.
        st.rerun()

    except Exception as erro:
        if conexao:
            conexao.rollback()
        print(f"Erro ao adicionar crédito: {erro}")
        st.error("Não foi possível adicionar o crédito. Tente novamente.")

    finally:
        if cursor:
            cursor.close()
        if conexao:
            conexao.close()
