import sqlite3

def criar_banco():
    conn = sqlite3.connect('estoque.db')
    cursor = conn.cursor()

    # Tabela de produtos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL
        )
    ''')

    # Tabela de usuários (funcionários)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            usuario TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    ''')

    # Tabela de retiradas
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

# Rodar a criação ao iniciar
criar_banco()

from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'chave_funcionario'

# Banco de dados compartilhado
def conectar():
    return sqlite3.connect('estoque.db')

# Cadastro
@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    erro = None
    if request.method == 'POST':
        nome = request.form['nome']
        usuario = request.form['usuario']
        senha = request.form['senha']

        conn = conectar()
        cursor = conn.cursor()

        try:
            cursor.execute('INSERT INTO usuarios (nome, usuario, senha) VALUES (?, ?, ?)', (nome, usuario, senha))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            erro = 'Usuário já existe!'
            conn.close()

    return render_template('cadastro.html', erro=erro)

# Login
@app.route('/', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM usuarios WHERE usuario = ? AND senha = ?', (usuario, senha))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['usuario_id'] = user[0]
            return redirect(url_for('home'))
        else:
            erro = 'Usuário ou senha inválidos'

    return render_template('login.html', erro=erro)

# Home
@app.route('/home')
def home():
    if not session.get('usuario_id'):
        return redirect(url_for('login'))
    return render_template('home.html')

# Retirar Produto
@app.route('/retirar', methods=['GET', 'POST'])
def retirar():
    if not session.get('usuario_id'):
        return redirect(url_for('login'))

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM produtos')
    produtos = cursor.fetchall()

    mensagem = None

    if request.method == 'POST':
        produto_id = request.form['produto_id']
        quantidade = int(request.form['quantidade'])

        cursor.execute('SELECT quantidade FROM produtos WHERE id = ?', (produto_id,))
        estoque = cursor.fetchone()

        if estoque and estoque[0] >= quantidade:
            novo_estoque = estoque[0] - quantidade
            cursor.execute('UPDATE produtos SET quantidade = ? WHERE id = ?', (novo_estoque, produto_id))

            data = datetime.now().strftime('%d/%m/%Y %H:%M')
            cursor.execute('INSERT INTO retiradas (usuario_id, produto_id, quantidade, data) VALUES (?, ?, ?, ?)',
                           (session['usuario_id'], produto_id, quantidade, data))

            conn.commit()
            mensagem = 'Retirada realizada com sucesso!'
        else:
            mensagem = 'Estoque insuficiente.'

    conn.commit()
    conn.close()
    return render_template('retirar.html', produtos=produtos, mensagem=mensagem)

# Histórico
@app.route('/historico')
def historico():
    if not session.get('usuario_id'):
        return redirect(url_for('login'))

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT p.nome, r.quantidade, r.data
        FROM retiradas r
        LEFT JOIN produtos p ON r.produto_id = p.id
        WHERE r.usuario_id = ?
    ''', (session['usuario_id'],))
    registros = cursor.fetchall()
    conn.close()
    return render_template('historico.html', registros=registros)

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)