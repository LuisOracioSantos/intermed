from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify

from service import service_bp
from service.controllerservice import buscadados


class Usuario:
    def __init__(self, nome, nickname, senha):
        self.nome = nome
        self.nickname = nickname
        self.senha = senha

usuario1 = Usuario("admin", "admin", "admin")


usuarios = { usuario1.nickname : usuario1}

##listaprodutos = buscadados()

listaprodutos =[
    {
        "item": "AP1010",
        "descricao": "Produto A",
        "mes1": 1200,
        "mes2": 1500,
        "mes3": 1300,
        "media_trimestre": round((1200 + 1500 + 1300) / 3, 2),
        "media_semestre": round((1200 + 1500 + 1300 + 1400 + 1600 + 1700) / 6, 2)  # Exemplo completo
    },
    {
        "item": "CE2025",
        "descricao": "Produto B",
        "mes1": 800,
        "mes2": 950,
        "mes3": 1100,
        "media_trimestre": round((800 + 950 + 1100) / 3, 2),
        "media_semestre": round((800 + 950 + 1100 + 1000 + 1050 + 1150) / 6, 2)
    },
    {
        "item": "XP3050",
        "descricao": "Produto C",
        "mes1": 300,
        "mes2": 400,
        "mes3": 500,
        "media_trimestre": round((300 + 400 + 500) / 3, 2),
        "media_semestre": round((300 + 400 + 500 + 600 + 700 + 800) / 6, 2)
    }
]

listaclientes =[
    {
        "codigo": "1530",
        "cliente": "Cliente 1",
        "totalvendames": 5500,
        "observacao": "Venda realizado na semana passada",
        "previsaoia": "Possivel venda"

    },
    {
        "codigo": "1010",
        "cliente": "Cliente 2",
        "totalvendames": 3200,
        "observacao": "Venda realizado na semana passada",
        "previsaoia": "Possivel venda"
    },
    {
        "codigo": "2230",
        "cliente": "Cliente 3",
        "totalvendames": 2600,
        "observacao": "Venda realizado na semana passada",
        "previsaoia": "Possivel venda"
    }
]



app = Flask(__name__)
app.secret_key = 'forecast'
app.register_blueprint(service_bp)

@app.route('/')
def index():

    return render_template('lista.html', titulo='SQ Quimica', lista_produtos= listaprodutos)


@app.route('/vendacliente')
def vendacliente():
    return render_template('listaclientes.html', titulo='SQ Quimica', lista_clientes = listaclientes)

@app.route('/api/clientes/<codigo>/produtos')
def api_produtos_cliente(codigo):
    produtos = buscar_produtos_vendidos_por_cliente(codigo)
    return jsonify(produtos)

def buscar_produtos_vendidos_por_cliente(codigo):
    return [
        {'nome': 'Arroz 5kg', 'quantidade': 20, 'data': '2025-06-01', 'valor': 200.00},
        {'nome': 'Feijão 1kg', 'quantidade': 15, 'data': '2025-06-05', 'valor': 90.00}
    ]

@app.route('/novo')
def novo():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('novo')))
    return render_template('novo.html', titulo='Novo Jogo')

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

app.run(debug=True)