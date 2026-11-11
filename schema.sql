CREATE DATABASE IF NOT EXISTS estoque;

USE estoque;

CREATE TABLE IF NOT EXISTS fornecedores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    contato VARCHAR(100),

    CONSTRAINT chk_fornecedor_nome_nao_vazio
        CHECK (CHAR_LENGTH(TRIM(nome)) > 0)
);

CREATE TABLE IF NOT EXISTS produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(30) NOT NULL,
    preco DECIMAL(10, 2) NOT NULL,
    quantidade_estoque INT NOT NULL DEFAULT 0,
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    id_fornecedor INT,

    CONSTRAINT chk_nome_nao_vazio
        CHECK (CHAR_LENGTH(TRIM(nome)) > 0),

    CONSTRAINT chk_preco_positivo
        CHECK (preco > 0),

    CONSTRAINT chk_estoque_nao_negativo
        CHECK (quantidade_estoque >= 0),

    CONSTRAINT chk_estoque_ativo
        CHECK (quantidade_estoque > 0 OR ativo = FALSE),

    CONSTRAINT fk_produtos_fornecedor
        FOREIGN KEY (id_fornecedor) REFERENCES fornecedores(id) ON DELETE SET NULL
);

INSERT INTO fornecedores (nome, contato) VALUES
('Fornecedor 1', 'contato@fornecedor1.com'),
('Fornecedor 2', 'vendas@fornecedor2.com'),
('Fornecedor 3', 'info@fornecedor3.com'),
('Fornecedor 4', 'contato@fornecedor4.com'),
('Fornecedor 5', 'contato@fornecedor5.com');

