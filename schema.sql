CREATE DATABASE IF NOT EXISTS estoque;

USE estoque;

CREATE TABLE IF NOT EXISTS produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    preco DECIMAL(10, 2) NOT NULL,
    quantidade_estoque INT NOT NULL DEFAULT 0,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT chk_nome_nao_vazio
        CHECK (CHAR_LENGTH(TRIM(nome)) > 0),

    CONSTRAINT chk_preco_positivo
        CHECK (preco > 0),

    CONSTRAINT chk_estoque_nao_negativo
        CHECK (quantidade_estoque >= 0),

    CONSTRAINT chk_estoque_ativo
        CHECK (quantidade_estoque > 0 OR ativo = FALSE)
);