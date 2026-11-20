# Mensagens que sobrevivem ao st.rerun() (P10).
#
# Problema: várias telas fazem  st.success("...")  e logo depois  st.rerun().
# O rerun redesenha a página do zero e a mensagem some antes de o usuário ler.
#
# Solução (o mesmo padrão do flash() do Flask): guardar a mensagem no
# session_state antes do rerun e mostrá-la uma única vez na próxima execução.

import streamlit as st


_CHAVE = "aviso_pendente"


# Guarda uma mensagem para mostrar depois do rerun.
#
# tipo: "success", "info", "warning" ou "error".
def avisar(mensagem, tipo="success"):
    st.session_state[_CHAVE] = (tipo, mensagem)


# Mostra a mensagem guardada (se houver) e apaga, para não repetir.
def mostrar_aviso():
    aviso = st.session_state.pop(_CHAVE, None)

    if aviso:
        tipo, mensagem = aviso
        getattr(st, tipo)(mensagem)
