import streamlit as st
from database.inicializar import conectar
from views.admin_Mestoque_visualizar import tela_admin_estoque_visualizar


def tela_admin_inicio():

    usuario = st.session_state.usuario

    if not usuario or usuario["perfil"] != "administrador":
        st.error("Acesso não autorizado.")
        st.session_state.pagina = "login"
        st.rerun()
        return

    st.title("Painel Administrativo")
    st.write(f"Bem-vindo(a), {usuario['nome']}!")
    st.caption("Visão geral da Cantina da Honestidade")

    st.divider()

    st.subheader("Financeiro")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("Aqui vai ficar o orçamento")

    with col2:
        st.write("Aqui vai ficar o gasto do mês")

    with col3:
        st.write("Aqui vai ficar a arrecadação do mês")

    st.caption("Aqui fica um filtro de data para baixar ")
    st.caption("Aqui fica um botão de baixar relatório")
    st.write("Aqui vai ficar a tabela de data | orçamento | vendas | saídas (geral)(em reais) | Saldo final. (Esse é o relatório)")

    st.divider()

    tela_admin_estoque_visualizar()
