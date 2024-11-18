from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
import os
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime





app = Flask(__name__)
app.secret_key = 'projeto_giordana_secreto_web'
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')

# Configuração do banco de dados MySQL
def conexao():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="123456",
        database="eccomerce_db"  # Nome do banco de dados
    )

# Decorator para verificar se o usuário é administrador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session or session.get('role') != 'admin':
            return redirect(url_for('unauthorized'))  # Redireciona para uma página de acesso negado
        return f(*args, **kwargs)
    return decorated_function

# Rota para página de acesso negado
@app.route('/unauthorized')
def unauthorized():
    return "Você não tem permissão para acessar esta página.", 403

# Função para adicionar item ao carrinho
def adicionar_ao_carrinho(produto_id):
    # Verifica se o carrinho já existe na sessão
    if 'carrinho' not in session:
        session['carrinho'] = []

    carrinho = session['carrinho']

    # Conectar ao banco de dados para buscar o produto
    try:
        db = conexao()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, preco, imagem FROM produtos WHERE id = %s", (produto_id,))
        produto = cursor.fetchone()

        if produto:
            # Adicionar o produto ao carrinho
            carrinho.append(produto)
            session['carrinho'] = carrinho
        else:
            flash('Produto não encontrado.', 'danger')
    except mysql.connector.Error as err:
        flash(f"Erro ao adicionar produto: {str(err)}", 'danger')
    finally:
        cursor.close()
        db.close()

# Rota para exibir o carrinho
@app.route('/carrinho', methods=['GET', 'POST'])
def carrinho():
    if request.method == 'POST':
        # Verifica se o usuário está logado
        if 'usuario_id' not in session:
            flash('Você precisa estar logado para finalizar a compra.', 'warning')
            return redirect(url_for('criar_conta'))  # Redireciona para a página de criação de conta

        # Se o usuário está logado, redireciona para a página de pagamento
        return redirect(url_for('pagamento'))
    
    # Renderiza o carrinho normalmente
    return render_template('carrinho.html')

# Rota para adicionar produtos ao carrinho
@app.route('/adicionar_carrinho/<int:produto_id>')
def adicionar_carrinho(produto_id):
    adicionar_ao_carrinho(produto_id)
    flash('Produto adicionado ao carrinho!', 'success')
    return redirect(url_for('carrinho'))

# Rota para remover item do carrinho
@app.route('/remover_item/<int:produto_id>')
def remover_item(produto_id):
    carrinho = session.get('carrinho', [])
    
    # Remover o produto do carrinho pelo ID
    for item in carrinho:
        if item['id'] == produto_id:
            carrinho.remove(item)
            break

    session['carrinho'] = carrinho
    flash('Produto removido do carrinho.', 'success')
    return redirect(url_for('carrinho'))

# Rota para limpar o carrinho
@app.route('/limpar_carrinho')
def limpar_carrinho():
    session.pop('carrinho', None)
    flash('Carrinho limpo.', 'success')
    return redirect(url_for('carrinho'))



def get_usuario():
    return session.get('usuario_nome', 'Visitante')

@app.route('/')
def index():
    usuario = session.get('usuario_nome', 'Visitante')
    return render_template('index.html', usuario=usuario)


@app.route('/criarconta', methods=['GET', 'POST'])
def criarconta():
    if request.method == 'POST':
        # Coletando dados do formulário
        usuario = request.form['usuario']
        email = request.form['email']
        senha = request.form['senha']
        data_nascimento = request.form['data_nascimento']
        try:
            # Inserindo dados no banco de dados
            db = conexao()
            cursor = db.cursor()
            cursor.execute("INSERT INTO usuarios (usuario, email, senha, data_nascimento) VALUES (%s, %s, %s, %s)", (usuario, email, senha, data_nascimento))
            db.commit()
            flash('Usuário criado com sucesso!', 'success')
            return redirect(url_for('login'))  # Redireciona para o login após cadastro
        except mysql.connector.Error as err:
            flash(f"Erro ao cadastrar: {err}", 'danger')
            db.rollback()
        finally:
            cursor.close()
            db.close()
    return render_template('criarconta.html')  # Exibe o formulário se for um GET








# Rota para exibir os produtos e aplicar o filtro de marca
@app.route('/products', methods=['GET'])
def products():
    marca = request.args.get('brand')  # Obtém o valor do filtro de marca
    
    try:
        db = conexao()
        cursor = db.cursor(dictionary=True)

        # Se uma marca for selecionada no filtro, filtrar os produtos por essa marca
        if marca and marca != "":
            cursor.execute("SELECT id, nome, descricao, descricao_detalhada, preco, imagem FROM produtos WHERE nome LIKE %s", (f"%{marca}%",))
        else:
            cursor.execute("SELECT id, nome, descricao, descricao_detalhada, preco, imagem FROM produtos")

        produtos = cursor.fetchall()

        # Formatar o preço como string com duas casas decimais
        for produto in produtos:
            produto['preco'] = "{:.2f}".format(float(produto['preco']))

    finally:
        cursor.close()
        db.close()

    return render_template('products.html', produtos=produtos)

@app.route('/listaprodutos', methods=['GET'])
@admin_required
def listaprodutos():
    try:
        # Conectar ao banco de dados
        conn = conexao()
        cursor = conn.cursor(dictionary=True)

        # Consulta para obter produtos
        cursor.execute("SELECT id, nome FROM produtos")
        produtos = cursor.fetchall()

    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500

    finally:
        cursor.close()
        conn.close()

    return render_template('produtos.html', produtos=produtos)

@app.route('/edit_product/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def edit_product(product_id):
    db = conexao()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        
        # Verifica se uma nova imagem foi enviada
        product_image = request.files.get('productImage')

        # Se não houver uma nova imagem, não sobrescreva a imagem existente
        if product_image and product_image.filename:
            # Certifique-se de que o diretório de upload existe
            if not os.path.exists(app.config['UPLOAD_FOLDER']): 
                os.makedirs(app.config['UPLOAD_FOLDER'])

            # Salva a nova imagem
            filename = secure_filename(product_image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            product_image.save(image_path)  # Salva a imagem
            image_url = filename  # Armazena apenas o nome do arquivo
        else:
            # Se não houver nova imagem, mantenha a imagem existente
            cursor.execute("SELECT imagem FROM produtos WHERE id = %s", (product_id,))
            existing_product = cursor.fetchone()
            image_url = existing_product['imagem']

        # Atualiza o produto no banco de dados
        cursor.execute("""UPDATE produtos 
            SET nome = %s, descricao = %s, preco = %s, imagem = %s 
            WHERE id = %s
        """, (name, description, price, image_url, product_id))

        db.commit()
        cursor.close()
        db.close()
        flash('Produto atualizado com sucesso!')
        return redirect(url_for('products'))

    # Se o método for GET, buscar o produto
    cursor.execute("SELECT * FROM produtos WHERE id = %s", (product_id,))
    product = cursor.fetchone()
    cursor.close()
    db.close()

    return render_template('edit_product.html', product=product)

@app.route('/guitarforme')
def guitarforme():
    return render_template('guitarforme.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/sobre')
def sobre():
    return render_template('sobre.html')





@app.route('/addproduto')
@admin_required
def adicionarProduto():
    return render_template('adicionar.html')







@app.route('/remove_product', methods=['POST'])
@admin_required
def remove_product():
    product_id = request.form.get('productId')  # Obtém o ID do produto do formulário

    # Conectando ao banco de dados
    conn = conexao()
    cursor = conn.cursor()

    # Verificar e remover o produto da tabela 'produtos'
    cursor.execute("SELECT id FROM produtos WHERE id = %s", (product_id,))
    produto = cursor.fetchone()

    if produto:
        cursor.execute("DELETE FROM produtos WHERE id = %s", (product_id,))
        conn.commit()
        flash("Produto removido com sucesso!", "success")
    else:
        flash("Produto não encontrado.", "error")

    # Fechar conexão
    cursor.close()
    conn.close()

    return redirect(url_for('index'))

@app.route('/remove_product_form')
@admin_required
def remove_product_form():
    return render_template('deletar.html')  # Renderiza o formulário de remoção










@app.route('/minhaconta')
def minhaconta():
    return render_template('minhaconta.html')

@app.route('/produto/<int:produto_id>', methods=['GET'])

def produto(produto_id):

    try:
        db = conexao()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, descricao, descricao_detalhada, preco, imagem FROM produtos WHERE id = %s", (produto_id,))
        produto = cursor.fetchone()

        if not produto:
            return "Produto não encontrado", 404

        # Formatar o preço como string com duas casas decimais
        produto['preco'] = "{:.2f}".format(float(produto['preco']))

    finally:
        cursor.close()
        db.close()

    return render_template('produto.html', produto=produto)

@app.route('/add_product', methods=['GET', 'POST'])
@admin_required
def add_product():
    if request.method == 'POST':
        product_name = request.form['productName']
        product_description = request.form['productDescription']
        product_description_details = request.form['productDescriptionDetails']
        product_price = request.form['productPrice']
        product_image = request.files['productImage']

        # Salvando a imagem do produto
        filename = secure_filename(product_image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        product_image.save(image_path)

        # Inserindo o produto no banco de dados
        db = conexao()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO produtos (nome, descricao, descricao_detalhada, preco, imagem) 
            VALUES (%s, %s, %s, %s, %s)
        """, (product_name, product_description, product_description_details, product_price, filename))
        db.commit()

        cursor.close()
        db.close()

        flash('Produto adicionado com sucesso!', 'success')
        return redirect(url_for('listaprodutos'))  # Redireciona para a lista de produtos após adicionar
    return render_template('adicionar.html')  # Exibe o formulário para adicionar produto se for GET





@app.route('/pagamento', methods=['GET', 'POST'])
def pagamento():
    if 'usuario_id' not in session:
        flash('Por favor, faça login ou crie uma conta para continuar.', 'warning')
        return redirect(url_for('criarconta'))
    if request.method == 'POST':
        # Capturando os dados do formulário
        nome = request.form['name']
        email = request.form['email']
        rua = request.form['rua']
        cep = request.form['cep']
        endereco = request.form['endereco']
        bairro = request.form['bairro']
        numero = request.form['numero']
        complemento = request.form['complemento']
        cidade = request.form['cidade']
        estado = request.form['estado']
        telefone = request.form['telefone']
        forma_pagamento = request.form['payment']
        total = request.form['total']
    

        # Pegando o ID do usuário logado da sessão
        usuario_id = session.get('usuario_id')

        # Obtendo a conexão
        db = conexao()
        cursor = db.cursor()  # Agora isso deve funcionar corretamente

        try:
            # Inserindo os dados na tabela pagamentos
            cursor.execute(""" 
                INSERT INTO pagamentos (usuario_id, total, nome, email, cep, endereco, bairro, numero, complemento, cidade, estado, telefone, forma_pagamento,rua) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (usuario_id, total, nome, email, cep, endereco, bairro, numero, complemento, cidade, estado, telefone, forma_pagamento, rua))

            # Confirma a transação
            db.commit()

            flash('Pagamento realizado com sucesso!', 'success')  # Notificação de sucesso
        except mysql.connector.Error as err:
            print(f"Erro: {err}")
            db.rollback()  # Reverta a transação em caso de erro
            flash('Erro ao processar o pagamento. Tente novamente.', 'danger')  # Notificação de erro
        finally:
            if cursor:  # Certifique-se de que o cursor foi criado
                cursor.close()
            if db:  # Feche a conexão se não for reutilizar
                db.close()

        # Redireciona para a página de confirmação ou sucesso
        return redirect(url_for('index'))

    return render_template('pagamento.html')  # Retorna o formulário de pagamento se GET



@app.route('/seus-pedidos')
def seus_pedidos():
    # Supondo que você tenha um método para obter o ID do usuário logado
    usuario_id = session.get('usuario_id')  # ou outro método de autenticação

    if not usuario_id:
        return redirect(url_for('index'))  # Redireciona se não estiver logado

    db = conexao()
    cursor = db.cursor(dictionary=True)
    
    # Consulta filtrando por ID do usuário
    query = "SELECT * FROM pagamentos WHERE usuario_id = %s"
    cursor.execute(query, (usuario_id,))
    pedidos = cursor.fetchall()

    cursor.close()
    return render_template('seus_pedidos.html', pedidos=pedidos)

















@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        try:
            db = conexao()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE email = %s AND senha = %s", (email, senha))
            user = cursor.fetchone()

            if user:
                session['usuario_id'] = user['id']
                session['usuario_nome'] = user.get('nome', 'Cliente')
                session['role'] = user.get('role', 'user')

                # Verifica se o usuário é um administrador
                if session['role'] == 'admin':
                    session['usuario_nome'] = 'Administrador'  # Altera para 'Administrador' se for admin
                
                session['is_admin'] = session['role'] == 'admin'
                return redirect(url_for('index'))
            else:
                flash('Email ou senha incorretos.', 'danger')

        except mysql.connector.Error as err:
            flash(f"Erro de login: {str(err)}", 'danger')

        finally:
            cursor.close()
            db.close()

    return render_template('login.html')


@app.route('/alterar_senha', methods=['GET', 'POST'])
def alterar_senha():
    if request.method == 'POST':
        email = request.form['email']
        senha_atual = request.form['senha_atual']
        nova_senha = request.form['nova_senha']
        confirmar_nova_senha = request.form['confirmar_nova_senha']

        if nova_senha != confirmar_nova_senha:
            flash('As novas senhas não coincidem.', 'danger')
            return redirect(url_for('alterar_senha'))

        try:
            db = conexao()
            cursor = db.cursor(dictionary=True)
            # Verificar se o email e a senha atual estão corretos
            cursor.execute("SELECT * FROM usuarios WHERE email = %s AND senha = %s", (email, senha_atual))
            user = cursor.fetchone()

            if user:
                # Atualizar a senha no banco de dados
                cursor.execute("UPDATE usuarios SET senha = %s WHERE email = %s", (nova_senha, email))
                db.commit()
                flash('Senha alterada com sucesso!', 'success')
            else:
                flash('Email ou senha atual incorretos.', 'danger')

        except mysql.connector.Error as err:
            flash(f"Erro ao alterar a senha: {str(err)}", 'danger')

        finally:
            cursor.close()
            db.close()

    return render_template('alterar_senha.html')


# Rota para logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
