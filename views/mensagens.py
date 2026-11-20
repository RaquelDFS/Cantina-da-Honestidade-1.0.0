# Guarda a mensagem para ela não sumir quando a tela recarrega
import streamlit as st


_CHAVE = "aviso_pendente"


def avisar(mensagem, tipo="success"):
    st.session_state[_CHAVE] = (tipo, mensagem)


# Mostra a mensagem guardada (se houver) e apaga, para não repetir
def mostrar_aviso():
    aviso = st.session_state.pop(_CHAVE, None)

    if aviso:
        tipo, mensagem = aviso
        getattr(st, tipo)(mensagem)
