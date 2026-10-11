# NÃO SUBIR SUA SENHA PARA O GITHUB!
# Essa é a senha que você, (TÚ MESMO!), colocou quando estava instalando o MYSQL
# THIAGO CONFERE SE O BANCO DE DADOS QUE VC FEZ É COMPATIVEL (MESMO NOME DE DATABASE) E MUDA SE FOR NECESSARIO
# Thiago - Inseri o import "os" para poder pegar a senha do banco de dados do arquivo .env e assim cada um poderá ter sua própria senha sem precisar alterar o código.

import os
import mysql.connector


def conectar():
    conexao = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("MYSQL_PASSWORD"),
        database="estoque"
    )

    return conexao