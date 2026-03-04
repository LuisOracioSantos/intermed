from datetime import datetime, timedelta
from math import ceil

from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify
import os
import locale

from config import DevelopmentConfig, ProductionConfig
from service import service_bp
from service.clientesfiltros import clientes_nao_valiosos, clientes_valiosos, clientes_compraram_uma_vez
from service.controllerservice import get_Dados_Forecast_Produto, atualizar_todos, \
    get_dados_venda_cliente_id, get_produtos_cadastro, get_meses_forecast, cria_forecast_mes, \
    grava_observacao_forecast, lista_observacao_forecast, atualiza_dadositens_forecast, get_dados_venda_cliente, \
    autenticar_representante, get_dados_venda_periodo_rep, get_dados_venda_produto_periodo_rep, \
    get_dados_venda_cliente_produto_id, atualiza_dados_forecast_tela, fecharForecast, getRepresentanteUser, \
    deletar_produto, altera_senha_representante
from dotenv import load_dotenv
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user, current_user
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = 'forecast'

try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except locale.Error:
    print("Locale pt_BR.UTF-8 não está disponível no sistema. Os meses podem aparecer em inglês.")


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

env = os.getenv('FLASK_ENV', 'development')
if env == 'production':
    app.config.from_object(ProductionConfig)
else:
    app.config.from_object(DevelopmentConfig)

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Usuario(UserMixin):
    def __init__(self, idrep, nome, tipo=None):
        self.id = str(idrep)
        self.nome = nome
        self.tipo = tipo

    MAPA_PERFIL = {
        "ADMIN": "Administrador",
        "REPRESENTANTE": "Representante",
        "COMPRAS": "Compras",
        "ADMIN_REPRESENTANTE": "Administrador Representante",
        "ADMIN_COMPRAS": "Administrador Compras",
        "VIEW": "Visualização"
    }

    def get_perfil_formatado(self):
        return self.MAPA_PERFIL.get(self.tipo, self.tipo)

    def get_id(self):
        return self.id


@login_manager.user_loader
def load_user(user_id):
    try:
        if not user_id:
            return None

        dados_rep = getRepresentanteUser(int(user_id))

        print("user_id no user_loader:", user_id)
        if not dados_rep:
            return None

        return Usuario(
            dados_rep.get('reprId'),
            dados_rep.get('nome'),
            tipo=dados_rep.get('tipoUsuario')
        )

    except Exception as e:
        print("ERRO NO load_user:", e)
        return None


# Blueprint
app.register_blueprint(service_bp)


@app.route('/')
@login_required
def principal():
    print(current_user.tipo)

    if current_user.tipo == "REPRESENTANTE":
        return redirect(url_for('vendacliente'))

    page = request.args.get('page', 1, type=int)
    per_page = 35  # Número de produtos por página


    mes = request.args.get('mes', default=None, type=int)
    ano = request.args.get('ano', default=None, type=int)
    seq = request.args.get('seq', default=None, type=int)



    if mes is None or ano is None:
        data_atual = datetime.now()
        mes = data_atual.month
        ano = data_atual.year

    #Chama a função passando mes e ano
    listaprodutos = get_Dados_Forecast_Produto(mes, ano, seq)
    total = len(listaprodutos)
    print(listaprodutos)

    start = (page - 1) * per_page
    end = start + per_page

    lista_pag = listaprodutos[start:end]
    total_pages = ceil(total / per_page)

    return render_template('listaforecast.html',
                           titulo='SQ Quimica',
                           lista_produtos=lista_pag,
                           page=page,
                           total=total,
                           total_pages=total_pages,
                           mes=mes,
                           ano=ano,
                           seq=seq)


@app.route('/vendaprodutocliente')
@login_required
def venda_periodo_produto_representante():
    page = request.args.get('page', 1, type=int)
    per_page = 20

    idrep = current_user.id

    data_inicial_str = request.args.get('data_inicial')
    data_final_str = request.args.get('data_final')

    if data_inicial_str and data_final_str:
        # Converte as strings em objetos datetime
        inicio = datetime.strptime(data_inicial_str, '%Y-%m-%d')
        fim = datetime.strptime(data_final_str, '%Y-%m-%d')
    else:
        # Caso o usuário ainda não tenha filtrado, define padrão (últimos 6 meses)
        fim = datetime.today()
        inicio = fim - timedelta(days=180)

    dados = get_dados_venda_produto_periodo_rep(idrep, inicio, fim)

    total = len(dados)

    start = (page - 1) * per_page
    end = start + per_page

    lista_pag = dados[start:end]
    total_pages = ceil(total / per_page)

    print(dados)

    if dados is None:
        return jsonify({"error": "Erro ao buscar dados da API"}), 500

    return render_template('listavendaprodutoclientes.html',
                           titulo='SQ Quimica',
                           lista_produtos=lista_pag,
                           total=total,
                           page=page,
                           total_pages=total_pages)


@app.route('/vendacliente', defaults={'categoria': 'valiosos'})
@app.route('/vendacliente/<categoria>')
@login_required
def vendacliente(categoria):
    page = request.args.get('page', 1, type=int)
    per_page = 20

    idrep = current_user.get_id()

    # Tenta pegar as datas do formulário
    data_inicial_str = request.args.get('data_inicial')
    data_final_str = request.args.get('data_final')

    if data_inicial_str and data_final_str:
        # Converte as strings em objetos datetime
        inicio = datetime.strptime(data_inicial_str, '%Y-%m-%d')
        fim = datetime.strptime(data_final_str, '%Y-%m-%d')
    else:
        # Caso o usuário ainda não tenha filtrado, define padrão (últimos 6 meses)
        fim = datetime.today()
        inicio = fim - timedelta(days=180)

    # Formata para string no formato YYYY-MM-DD
    inicio_str = inicio.strftime('%Y-%m-%d')
    fim_str = fim.strftime('%Y-%m-%d')

    listaclientes = get_dados_venda_periodo_rep(idrep, inicio_str, fim_str)

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

    return render_template('listavendaclientes.html',
                           titulo='SQ Quimica',
                           lista_clientes=lista_pag,
                           total=total,
                           page=page,
                           total_pages=total_pages)


@app.route('/getDadosVendaClienteId/<int:id>', methods=['GET'])
@login_required
def api_produtos_cliente(id):
    data_inicial = request.args.get('data_inicial')
    data_final = request.args.get('data_final')

    if data_inicial and data_final:
        # Converte as strings em objetos datetime
        dtinicio = datetime.strptime(data_inicial, '%Y-%m-%d')
        dtfim = datetime.strptime(data_final, '%Y-%m-%d')
    else:
        # Caso o usuário ainda não tenha filtrado, define padrão (últimos 6 meses)
        dtfim = datetime.today()
        dtinicio = dtfim - timedelta(days=180)

    # Formata para string no formato YYYY-MM-DD
    inicio = dtinicio.strftime('%Y-%m-%d')
    fim = dtfim.strftime('%Y-%m-%d')

    produtos = get_dados_venda_cliente_id(id, inicio, fim)
    return jsonify(produtos)


@app.route('/getDadosVendaClienteProdutoId/<int:id>', methods=['GET'])
@login_required
def filtro_vendedor_por_produtos(id):
    idrep = current_user.id
    data_inicial = request.args.get('data_inicial')
    data_final = request.args.get('data_final')

    if data_inicial and data_final:
        # Converte as strings em objetos datetime
        dtinicio = datetime.strptime(data_inicial, '%Y-%m-%d')
        dtfim = datetime.strptime(data_final, '%Y-%m-%d')
    else:
        # Caso o usuário ainda não tenha filtrado, define padrão (últimos 6 meses)
        dtfim = datetime.today()
        dtinicio = dtfim - timedelta(days=180)

        # Formata para string no formato YYYY-MM-DD
    inicio = dtinicio.strftime('%Y-%m-%d')
    fim = dtfim.strftime('%Y-%m-%d')

    print(id, inicio, fim, idrep)

    vendas = get_dados_venda_cliente_produto_id(id, inicio, fim, idrep)
    return jsonify(vendas)


@app.route('/novo')
def novo():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('novo')))
    return render_template('novo.html', titulo='Novo Jogo')


@app.route('/atualizartodos')
def atualizatodos():
    atualizar_todos()


@app.route('/login')
def login():
    proxima = request.args.get('proxima')
    return render_template('login.html', proxima=proxima)


@app.route('/usuario')
def alterarusuario():
    proxima = request.args.get('proxima')
    return render_template('usuario.html', proxima=proxima)


@app.route('/configproduto')
def configproduto():
    # parâmetros opcionais
    itemid = request.args.get('itemid', type=int)
    item = request.args.get('item', default="", type=str)
    descricao = request.args.get('descricao', default="", type=str)
    proxima = request.args.get('proxima', default="", type=str)

    return render_template('configproduto.html',
                           itemid=itemid,
                           item=item,
                           descricao=descricao,
                           proxima=proxima)

@app.route('/atualizacoes')
def atualizacoes():
    proxima = request.args.get('proxima')
    return render_template('atualizacao.html', proxima=proxima)


@app.route('/getDadosProdutosCadastro', methods=['GET'])
@login_required
def getProdutos():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    termo_busca = request.args.get('busca', '').strip().lower()

    produtos = get_produtos_cadastro()

    if termo_busca:
        produtos = [
            p for p in produtos
            if termo_busca in p['item'].lower() or termo_busca in p['descricao'].lower()
        ]

    # chama função auxiliar
    total = len(produtos)
    start = (page - 1) * per_page
    end = start + per_page
    produtos_paginados = produtos[start:end]

    return jsonify({
        "produtos": produtos_paginados,
        "pagina_atual": page,
        "total_paginas": (total + per_page - 1) // per_page
    })

@app.route('/getMesesForecast')
def getmesesforecast():
    try:
        dados = get_meses_forecast()

        resultado = []
        for item in dados:
            id_forecast = item.get("idmesforecast")
            data_mes = item.get("mesforecast")
            seq_mes = item.get("seqmes")
            fechado = item.get("fechado")

            data_formatada = datetime.strptime(data_mes, "%Y-%m-%d").strftime("%B/%Y")

            resultado.append({
                "id": id_forecast,
                "mes": data_formatada.capitalize(),
                "seqmes": seq_mes,# Capitaliza o mês
                "fechado": fechado
            })

        return jsonify(resultado)

    except Exception as e:
        print(f"Erro ao buscar forecast: {e}")
        return jsonify([]), 500


@app.route('/cria_forecast_mes')
def criamesforecast():
    return cria_forecast_mes()

@app.route('/gravar-observacao', methods=['POST'])
def gravar_observacao_controller():
    idforecast = request.args.get('idforecast')
    item = request.args.get('item')
    obs = request.args.get('obs')

    return grava_observacao_forecast(idforecast, obs, item)

@app.route('/listar_observacoes/<int:idforecastobs>')
def api_observacoes(idforecastobs):
    try:
        observacoes = lista_observacao_forecast(idforecastobs)
        return jsonify(observacoes)
    except Exception as e:
        return jsonify({'error': 'Erro ao buscar observações', 'detalhe': str(e)}), 500


@app.route('/atualizar_dados_itens_forecast/<int:idforecast>', methods=['PUT'])
def atualizar_dadositens_forecast(idforecast):
    dadositens = request.get_json()
    return atualiza_dadositens_forecast(idforecast, dadositens)


@app.route('/atualizar_dados', methods=['POST'])
def atualizar_dados():
    dados = request.get_json(force=True)

    if not isinstance(dados, list):
        dados = [dados]

    resultado = atualiza_dados_forecast_tela(dados, return_json=False)

    if resultado["status"] == "ok":
        return jsonify({"mensagem": "Atualização concluída", "detalhes": resultado["dados"]}), 201
    else:
        return jsonify({"erro": "Falha na atualização", "detalhes": resultado["detalhes"]}), 400


@app.route('/fecharforecast', methods=['POST'])
def fechar_forecast():
    return fecharForecast()

@app.route('/deletaprodutoforecast/<int:idproduto>', methods=['DELETE'])
def deletaprodutorecast(idproduto):
    return deletar_produto(idproduto)

@app.route('/alterarsenha', methods=['GET', 'POST'])
@login_required
def alterarsenhausuario():
    if request.method == 'POST':
        nova_senha = request.form.get('senha')
        print("fnova senha", nova_senha)
        altera_senha_representante(nova_senha)
        return redirect(url_for('alterarsenhausuario'))

    return render_template('usuario.html')


@app.route('/autenticar', methods=['POST'])
def autenticar():
    rep = request.form['usuario']
    senha = request.form['senha']

    dados_rep = autenticar_representante(rep, senha)

    if dados_rep:
        user = Usuario(
            dados_rep['reprId'],
            dados_rep['nome'],
            tipo=dados_rep.get('tipoUsuario')
        )


        login_user(user)

        flash(f"{user.nome} logado com sucesso!", "success")
        return redirect(url_for('principal'))

    flash("Usuário ou senha inválidos", "danger")
    return redirect(url_for('login'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout efetuado com sucesso!')
    return redirect(url_for('login'))

@app.route('/clear-session')
def clear_session():
    session.clear()
    return "Sessão limpa"


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
