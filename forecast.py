from collections import defaultdict
from datetime import datetime
from math import ceil

from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify
import os
from config import DevelopmentConfig, ProductionConfig
from service import service_bp
from service.clientesfiltros import clientes_nao_valiosos, clientes_valiosos, clientes_compraram_uma_vez
from service.controllerservice import getDadosForecastProduto, get_dados_forecast_venda_cliente, atualizarTodos, \
    get_dados_forecast_venda_cliente_id
from dotenv import load_dotenv



load_dotenv()

class Usuario:
    def __init__(self, nome, nickname, senha):
        self.nome = nome
        self.nickname = nickname
        self.senha = senha

usuario1 = Usuario("admin", "admin", "admin")


usuarios = { usuario1.nickname : usuario1}


app = Flask(__name__)
app.secret_key = 'forecast'

env = os.getenv('FLASK_ENV', 'development')
if env == 'production':
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(DevelopmentConfig)

app.register_blueprint(service_bp)

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Número de produtos por página

    listaprodutos = getDadosForecastProduto()
    total = len(listaprodutos)

    start = (page - 1) * per_page
    end = start + per_page

    lista_pag = listaprodutos[start:end]
    total_pages = ceil(total / per_page)

    return render_template('listaprodutos.html',
                           titulo='SQ Quimica',
                           lista_produtos=lista_pag,
                           page=page,
                           total=total,
                           total_pages=total_pages)


@app.route('/vendacliente', defaults={'categoria': 'valiosos'})
@app.route('/vendacliente/<categoria>')
def vendacliente(categoria):

    page = request.args.get('page', 1, type=int)
    per_page = 20

    listaclientes = get_dados_forecast_venda_cliente()


    if categoria == 'valiosos':
        clientes_filtrados = clientes_valiosos(listaclientes)
    elif categoria == 'regulares':
        clientes_filtrados = clientes_nao_valiosos(listaclientes)
    elif categoria == 'inativos':
        clientes_filtrados = clientes_compraram_uma_vez(listaclientes)
    else:
        return f"Categoria '{categoria}' não reconhecida", 400

    total = len(clientes_filtrados)

    start = (page - 1) * per_page
    end = start + per_page

    lista_pag = clientes_filtrados[start:end]
    total_pages = ceil(total / per_page)

    return render_template('listaclientes.html',
                           titulo='SQ Quimica',
                           lista_clientes = lista_pag,
                           total=total,
                           page=page,
                           total_pages=total_pages)


@app.route('/getDadosVendaClienteId/<int:id>', methods=['GET'])
def api_produtos_cliente(codigo):
    produtos = buscar_produtos_vendidos_por_cliente(codigo)
    return jsonify(produtos)


def buscar_produtos_vendidos_por_cliente(codigo):
    return get_dados_forecast_venda_cliente_id(codigo)

@app.route('/novo')
def novo():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('novo')))
    return render_template('novo.html', titulo='Novo Jogo')

@app.route('/atualizartodos')
def atualizatodos():
    atualizarTodos()

# @app.route('/criar', methods=['POST',])
# def criar():
#     nome = request.form['nome']
#     categoria = request.form['categoria']
#     console = request.form['console']
#     jogo = Jogo(nome, categoria, console)
#     lista.append(jogo)
#     return redirect(url_for('index'))

@app.route('/login')
def login():
    proxima = request.args.get('proxima')
    return render_template('login.html', proxima=proxima)

@app.route('/autenticar', methods=['POST',])
def autenticar():
    if request.form['usuario'] in usuarios:
        usuario = usuarios[request.form['usuario']]
        if request.form['senha'] == usuario.senha:
            session['usuario_logado'] = usuario.nickname
            flash(usuario.nickname + ' logado com sucesso!')
            proxima_pagina = request.form['proxima']
            return redirect(proxima_pagina)
    else:
        flash('Usuário não logado.')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session['usuario_logado'] = None
    flash('Logout efetuado com sucesso!')
    return redirect(url_for('index'))

@app.template_filter('moeda')
def formatar_moeda(valor):
    return f'R$ {valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')

@app.template_filter('data_br')
def formatar_data_br(data_str):
    try:
        if isinstance(data_str, str):
            data = datetime.fromisoformat(data_str.replace("Z", "").split("+")[0])
            return data.strftime('%d/%m/%Y')
        return data_str
    except Exception:
        return data_str

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
