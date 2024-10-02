from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from flask import Flask, render_template, request, redirect, url_for, flash, session


app = Flask(__name__)
app.secret_key = 'projeto_giordana_secreto_web'

# Configuração do banco de dados
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="123456",
    database="eccomerce_db"  # Corrigido o nome do banco de dados
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/criarconta')
def criarconta():
    return render_template('criarconta.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/guitarforme')
def guitarforme():
    return render_template('guitarforme.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/cart')
def cart():
    return render_template('cart.html')  # icon do carrinho

@app.route('/minhaconta')  # Nova rota
def minhaconta():
    return render_template('minhaconta.html')

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    usuario = request.form['usuario']
    email = request.form['email']
    data_nascimento = request.form['data_nascimento']
    senha = request.form['senha']
    
    cursor = db.cursor()
    sql = "INSERT INTO usuarios (usuario, email, data_nascimento, senha) VALUES (%s, %s, %s, %s)"
    val = (usuario, email, data_nascimento, senha)
    cursor.execute(sql, val)
    db.commit()
    
    return redirect(url_for('index'))





@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        cursor = db.cursor(dictionary=True)
        sql = "SELECT * FROM usuarios WHERE email = %s AND senha = %s"
        val = (email, senha)
        cursor.execute(sql, val)
        usuario = cursor.fetchone()
        
        if usuario:
            session['usuario_id'] = usuario['id']
            session['usuario_nome'] = usuario['usuario']
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('index'))  # Redireciona para a página inicial
        else:
            flash('Email ou senha incorretos.', 'danger')
            # Retorna para a página de login com a mensagem de erro
            return redirect(url_for('login'))  # Redireciona para a página de login para mostrar a mensagem

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('usuario_id', None)  # Remove o usuário da sessão
    flash('Você foi desconectado.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
