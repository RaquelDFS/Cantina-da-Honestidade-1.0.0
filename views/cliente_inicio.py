import streamlit as st
from database.inicializar import conectar
from views.cliente_loja import tela_cliente_loja


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

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Adicionar crédito", use_container_width=True):
            st.session_state.pagina = "cliente_adicionar_credito"
            st.rerun()

    with col2:
        if st.button("Histórico de compras", use_container_width=True):
            st.session_state.pagina = "cliente_historico_compras"
            st.rerun()

    st.divider()
    st.write("Aqui vai ficar direto a Loja.")
    st.write("Então vamos tirar a loja do menu lateral e colocar um botão de perfil que só vai mostrar as informações pessoais dele, nada mais.")
    tela_cliente_loja()
