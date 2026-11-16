import streamlit as st
from database.inicializar import conectar


def tela_cliente_inicio():

    usuario = st.session_state.usuario

    st.title("Cantina da Honestidade")

    st.write(f"Bem-vindo(a), {usuario['nome']}!")
    st.write(f"Matrícula: {usuario['matricula']}")

    conexao = conectar()

    if conexao:
        cursor = conexao.cursor(dictionary=True)

        cursor.execute("""
            SELECT saldo_atual
            FROM carteiras
            WHERE id_usuario = %s
        """, (usuario["id_usuario"],))

        carteira = cursor.fetchone()

        if carteira:
            st.write(f"Crédito: R$ {carteira['saldo_atual']:.2f}")
        else:
            st.write("Crédito: R$ 0,00")

        cursor.close()
        conexao.close()

    else:
        st.error("Não foi possível consultar o saldo da carteira.")

    st.divider()
