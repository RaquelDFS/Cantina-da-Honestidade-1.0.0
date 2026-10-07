# NÃO SUBIR SUA SENHA PARA O GITHUB!
# Essa é a senha que você, (TÚ MESMO!), colocou quando estava instalando o MYSQL
# THIAGO CONFERE SE O BANCO DE DADOS QUE VC FEZ É COMPATIVEL (MESMO NOME DE DATABASE) E MUDA SE FOR NECESSARIO
import mysql.connector


def conectar():
    conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="estoque"
    )

    return conexao
