from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
import os
from werkzeug.utils import secure_filename

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
@app.route('/carrinho')
def carrinho():
    carrinho = session.get('carrinho', [])
    total = sum(item['preco'] for item in carrinho)  # Calcular o valor total do carrinho
    return render_template('carrinho.html', carrinho=carrinho, total=total)

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
 

@app.route('/pagamento')
def pagamento():
    return render_template('pagamento.html')


def get_usuario():
    return session.get('usuario_nome', 'Visitante')

@app.route('/')
def index():
    return render_template('index.html', usuario=get_usuario())

@app.route('/criarconta')
def criarconta():
    return render_template('criarconta.html')

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
        cursor.execute("""
            UPDATE produtos 
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

@app.route('/addproduto')
def adicionarProduto():
    return render_template('adicionar.html')



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

@app.route('/add_product', methods=['POST'])
def add_product():
    if request.method == 'POST':
        product_name = request.form['productName']
        product_description = request.form['productDescription']
        product_description_details = request.form['productDescriptionDetails']
        product_price = float(request.form['productPrice'])
        product_image = request.files['productImage']

        # Certifique-se de que o diretório de upload existe
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])

        # Salva a imagem
        image_url = None
        if product_image:
            filename = secure_filename(product_image.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            product_image.save(image_path)  # Salva a imagem
            image_url = filename  # Armazena apenas o nome do arquivo

        # Inserir o produto no banco de dados
        try:
            db = conexao()
            cursor = db.cursor()

            sql = "INSERT INTO produtos (nome, descricao, descricao_detalhada, preco, imagem) VALUES (%s, %s, %s, %s, %s)"
            val = (product_name, product_description, product_description_details, product_price, image_url)
            cursor.execute(sql, val)
            db.commit()

        except mysql.connector.Error as err:
            db.rollback()
            return jsonify({'error': str(err)}), 500
        
        finally:
            db.close()

        return redirect(url_for('index'))
    
@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    usuario = request.form['usuario']
    email = request.form['email']
    data_nascimento = request.form['data_nascimento']
    senha = request.form['senha']
    
    db = conexao()
    cursor = db.cursor()
    sql = "INSERT INTO usuarios (usuario, email, data_nascimento, senha) VALUES (%s, %s, %s, %s)"
    val = (usuario, email, data_nascimento, senha)
    cursor.execute(sql, val)
    db.commit()
    cursor.close()
    
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        
        db = conexao()
        cursor = db.cursor(dictionary=True)
        sql = "SELECT * FROM usuarios WHERE email = %s AND senha = %s"
        val = (email, senha)
        cursor.execute(sql, val)
        usuario = cursor.fetchone()
        
        if usuario:
            session['usuario_id'] = usuario['id']
            session['usuario_nome'] = usuario['usuario']
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Email ou senha incorretos.', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    session.pop('usuario_nome', None)
    flash('Você foi desconectado.', 'success')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
