import sqlite3

# Conectando ao banco de dados
conexao = sqlite3.connect("login_site.db")

# Criando um cursor
cursor = conexao.cursor()

# Criando a tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS cadastros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100),
    email VARCHAR(100),
    data_nascimento DATE,
    senha VARCHAR(255)
);
""")

# Inserindo um registro de teste
cursor.execute("""
INSERT INTO cadastros (nome, email, data_nascimento, senha)
VALUES ('Teste', 'teste@example.com', '2000-01-01', 'senha123');
""")

# Commitando as alterações
conexao.commit()

# Fechando a conexão
conexao.close()
