import sqlite3

# Conectar ou criar o banco de dados
conn = sqlite3.connect('estoque.db')
cursor = conn.cursor()

# Criar tabela de produtos
cursor.execute('''
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        quantidade INTEGER NOT NULL
    )
''')

# Criar tabela de usuários (funcionários)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        usuario TEXT NOT NULL UNIQUE,
        senha TEXT NOT NULL
    )
''')

# Criar tabela de retiradas (histórico)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS retiradas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        produto_id INTEGER,
        quantidade INTEGER,
        data TEXT,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (produto_id) REFERENCES produtos(id)
    )
''')

# Criar usuário administrador padrão
try:
    cursor.execute("INSERT INTO usuarios (nome, usuario, senha) VALUES (?, ?, ?)",
                   ('Administrador', 'admin', 'admin'))
except sqlite3.IntegrityError:
    print("Administrador já cadastrado.")

conn.commit()
conn.close()

print("Banco de dados criado com sucesso!")