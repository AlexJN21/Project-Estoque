from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'chave_admin'

# Banco de dados compartilhado
def conectar():
    return sqlite3.connect('estoque.db')

# Criação do banco e tabelas
def criar_banco():
    conn = conectar()
    cursor = conn.cursor()

    # Produtos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL
        )
    ''')

    # Usuários (funcionários)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            usuario TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    ''')

    # Retiradas
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

    conn.commit()
    conn.close()

# Cria banco se não existir
criar_banco()

# Login Admin
@app.route('/', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        if request.form['usuario'] == 'admin' and request.form['senha'] == 'admin':
            session['admin'] = True
            return redirect(url_for('home'))
        else:
            erro = 'Usuário ou senha inválidos'
    return render_template('login_1.html', erro=erro)

# Home
@app.route('/home')
def home():
    if not session.get('admin'):
        return redirect(url_for('login_1'))
    return render_template('home.html')

# Produtos
@app.route('/produtos', methods=['GET', 'POST'])
def produtos():
    if not session.get('admin'):
        return redirect(url_for('login_1'))

    conn = conectar()
    cursor = conn.cursor()

    if request.method == 'POST':
        nome = request.form['nome']
        quantidade = request.form['quantidade']
        cursor.execute('INSERT INTO produtos (nome, quantidade) VALUES (?, ?)', (nome, quantidade))
        conn.commit()

    cursor.execute('SELECT * FROM produtos')
    produtos = cursor.fetchall()
    conn.close()
    return render_template('produtos.html', produtos=produtos)

# Histórico
@app.route('/historico')
def historico():
    if not session.get('admin'):
        return redirect(url_for('login_1'))

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT r.id, u.nome, p.nome, r.quantidade, r.data
        FROM retiradas r
        LEFT JOIN usuarios u ON r.usuario_id = u.id
        LEFT JOIN produtos p ON r.produto_id = p.id
    ''')
    registros = cursor.fetchall()
    conn.close()
    return render_template('historico.html', registros=registros)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)