from datetime import datetime

from flask import Blueprint, jsonify, request, flash, redirect, url_for, render_template
import requests
from flask_login import current_user

from service.calculosForecast import calcular_desvio_padrao

# Cria o blueprint
service_bp = Blueprint('service_bp', __name__)


def autenticar_representante(rep, senha):
    try:
        response = requests.get("http://127.0.0.1:8080/rep/replogin",
                                 json={"rep": rep, "senha": senha} , timeout=5
        )

        print("autenditar",response)
        if response.status_code == 200:
            dados = response.json()
            if dados:
                return dados[0]  # pega o primeiro da lista retornada
            return None
        else:
            print(f"Erro na API: {response.status_code} -> {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão com API: {e}")
        return None

@service_bp.route('/cadastrar-produto-forecast', methods=['POST'])
def cadastrar_produto_forecast():
    data = request.get_json()

    payload = {
        "descricao": data.get("descricao"),
        "idProdutoPrincipal": data.get("idProdutoPrincipal"),
        "produtosRelacionados": data.get("produtosRelacionados", [])
    }

    try:
        response = requests.post("http://127.0.0.1:8080/forecast", json=payload)

        if response.status_code == 201 or response.status_code == 200:
            return jsonify({"mensagem": "Produto Forecast cadastrado com sucesso!"}), 201
        else:
            return jsonify({"erro": "Erro ao cadastrar produto", "detalhes": response.text}), 400

    except requests.exceptions.RequestException as e:
        return jsonify({"erro": "Erro de comunicação com backend", "detalhes": str(e)}), 500


@service_bp.route('/get-produtos-relacionados/<int:id_produto_principal>', methods=['GET'])
def get_dados_produto_forecast_id(id_produto_principal):
    try:
        response = requests.get(f"http://127.0.0.1:8080/forecast/itemprincipal/{id_produto_principal}")
        response.raise_for_status()
        produto = response.json()

        print(produto)

        return jsonify({
            "id": produto.get("id"),
            "relacionados": produto.get("produtosRelacionados", [])
        })

    except requests.HTTPError as e:
        return jsonify({"relacionados": []})  # ← Retorna lista vazia SEM erro
    except Exception as e:
        print("Erro inesperado:", e)
        return jsonify({"relacionados": [], "erro": str(e)}), 500


def deletar_produto(id_produto):
    try:
        response = requests.delete(f"http://127.0.0.1:8080/forecast/{id_produto}")

        if response.status_code == 204:
            return '', 204  # Retorna vazio com status 204 para o Flask
        elif response.status_code == 404:
            return jsonify({"error": "Produto não encontrado."}), 404
        else:
            return jsonify(
                {"error": f"Erro ao deletar produto. Código: {response.status_code}"}), response.status_code

    except requests.exceptions.ConnectionError:
        return jsonify({"error": "Erro de conexão com a API."}), 500
    except Exception as e:
        return jsonify({"error": f"Erro inesperado: {str(e)}"}), 500


def get_Dados_Forecast_Produto(mes, ano, seq):
    params = { 'mes': mes, 'ano': ano, 'seq': seq }

    print(params)

    response = requests.get("http://127.0.0.1:8080/mesforecast/getdadosmesforecast", params=params)
    produtos = response.json()
    for item in produtos:
        item["desviopadrao"] = calcular_desvio_padrao(
            item["vendames1"],
            item["vendames2"],
            item["vendames3"])
    return produtos


def atualiza_dados_forecast_tela(data, return_json=True):
    try:
        response = requests.post("http://127.0.0.1:8080/atualiza/dadositensforecast", json=data)

        if response.status_code in [200, 201]:
            if return_json:
                return jsonify({"mensagem": "Dados atualizados!"}), 201
            return {"status": "ok", "dados": data}
        else:
            if return_json:
                return jsonify({"erro": "Erro ao atualizar dados", "detalhes": response.text}), 400
            return {"status": "erro", "detalhes": response.text, "dados": data}

    except requests.exceptions.RequestException as e:
        if return_json:
            return jsonify({"erro": "Erro de comunicação com backend", "detalhes": str(e)}), 500
        return {"status": "erro", "detalhes": str(e), "dados": data}


def get_produtos_cadastro():
    response = requests.get("http://127.0.0.1:8080/produtos/listartodos")
    produtos = response.json()
    return produtos


def get_dados_venda_cliente():
    response = requests.get("http://127.0.0.1:8080/vendas/dadosvendacliente")
    vendasCliente = response.json()
    return vendasCliente

def get_dados_venda_cliente_produto_id(iditem, dtinicio, dtfim, rep):
    params = {
        "iditem": iditem,
        "inicio": dtinicio,
        "fim": dtfim,
        "rep" :rep
    }

    try:
        response = requests.get("http://127.0.0.1:8080/vendas/dadosvendasclientesprod", params= params)

        if response.status_code == 200:
            return response.json()  # lista de dados
        else:
            print(f"Erro na API: {response.status_code} -> {response.text}")
            return None
    except Exception as e:
        print(f"Erro ao consumir API: {e}")
        return None

def get_dados_venda_periodo_rep(idrep, inicio, fim):
    params = {
        "rep": idrep,
        "inicio": inicio,
        "fim": fim
    }

    try:
        response = requests.get("http://127.0.0.1:8080/vendas/dadosvendaperiodorep", params=params)

        if response.status_code == 200:
            return response.json()  # lista de dados
        else:
            print(f"Erro na API: {response.status_code} -> {response.text}")
            return None
    except Exception as e:
        print(f"Erro ao consumir API: {e}")
        return None

def get_dados_venda_produto_periodo_rep(idrep, inicio, fim):
    params = {'rep': idrep, 'inicio': inicio, 'fim': fim}

    try:
        response = requests.get("http://127.0.0.1:8080/vendas/dadosvendaprodutosrep", params=params)

        if response.status_code == 200:
            return response.json()  # lista de dados
        else:
            print(f"Erro na API: {response.status_code} -> {response.text}")
            return None
    except Exception as e:
        print(f"Erro ao consumir API: {e}")
        return None


def get_meses_forecast():
    response = requests.get("http://127.0.0.1:8080/mesforecast")
    meses = response.json()
    return meses

def cria_forecast_mes():
    data_atual = datetime.now()
    mes = data_atual.month
    ano = data_atual.year
    params = {'mes': mes, 'ano': ano}

    try:
        response = requests.post("http://127.0.0.1:8080/mesforecast/criar",params=params)

        if response.status_code in (200, 201):
            resultado = response.text.strip().lower()  # ← pega a string retornada

            if resultado == "criado":
                return jsonify({"mensagem": "Forecast do mês criado com sucesso."}), 201
            elif resultado == "existe":
                return jsonify({"mensagem": "Já existe um Forecast para esse mês."}), 200
            elif resultado == "no item":
                return jsonify({"mensagem": "Não há itens cadastrados."}), 200
            else:
                return jsonify({
                    "erro": "Resposta inesperada do servidor.",
                    "detalhes": resultado,
                    "status_code": response.status_code
                }), 500

        return jsonify({
            "erro": "Erro ao comunicar com a API de forecast.",
            "status_code": response.status_code,
            "detalhes": response.text
        }), response.status_code

    except requests.exceptions.RequestException as e:
        return jsonify({"erro": "Erro ao criar forecast do mês", "detalhes": str(e)}), 500

def atualiza_dadositens_forecast(idforecast, dadositens):
    url_java = f'http://localhost:8080/dadositemforecast/{idforecast}'
    try:
        response = requests.put(url_java, json=dadositens)
        return (response.text, response.status_code, response.headers.items())
    except requests.exceptions.RequestException as e:
        return jsonify({'erro': str(e)}), 500


def grava_observacao_forecast(idforecast, obs, item ):
    payload = {
        'item': item,
        'observacao': obs,
        'idDadosForecast': idforecast
    }

    try:
        response = requests.post("http://127.0.0.1:8080/obs", json=payload)

        if response.status_code in (200, 201):
            return jsonify({"Mesagem": "Observação gravada com sucesso."}), 200
        else:
            return jsonify({
                "erro": "Resposta inesperada do servidor.",
                "status_code": response.status_code
            }), 500
    except Exception as e:
        return jsonify({"erro":str(e)}), 500


def grava_observacao_vendedores(cliente, idvendedor, obs):
    params = {'cliente': cliente, 'idvendedor': idvendedor, 'obs': obs}
    try:
        response = requests.post("http://127.0.0.1:8080/obsvendedor", params=params)
        if response.status_code in (200, 201):
            return jsonify({"Mesagem": "Observação gravada com sucesso."}), 200
        else:
            return jsonify({
                "erro": "Resposta inesperada do servidor.",
                "status_code": response.status_code
            }), 500
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

def lista_observacao_forecast(idforecastobs):
    response = requests.get(f"http://127.0.0.1:8080/obs/forecast/{idforecastobs}")
    return response.json()


def get_dados_venda_cliente_id(id, inicio, fim):
    params = {
        "inicio": inicio,
        "fim": fim
    }
    print(inicio, fim)
    try:
        url = f"http://localhost:8080/vendas/dadosvendaclienteid/{id}"
        response = requests.get(url, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            return jsonify(
                {"erro": f"Erro ao obter dados do cliente. Status: {response.status_code}"}), response.status_code
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@service_bp.route('/atualizarRegistros')
def atualizar_todos():
    response = requests.get("http://127.0.0.1:8080/atualiza/todos")
    if response.status_code == 200:
        return jsonify({"mensagem": "Registros atualizados com sucesso!"})
    else:
        return jsonify({"mensagem": "Erro ao atualizar"}), 500


def fecharForecast():
    data = request.get_json()

    print(data)

    if not data:
        return jsonify({"mensagem": "JSON não enviado"}), 400

    id_forecast = data.get('idMesForecast')
    seq_mes = data.get('seqmes')

    if not id_forecast or not seq_mes:
        return jsonify({"mensagem": "Parâmetros inválidos"}), 400

    payload = {
        "idMesForecast": int(id_forecast),
        "seqmes": int(seq_mes)
    }

    response = requests.post(
        "http://127.0.0.1:8080/mesforecast/fechar",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        return jsonify({"mensagem": "Forecast fechado com sucesso!"})
    else:
        return jsonify({
            "mensagem": "Erro ao fechar forecast",
            "status_java": response.status_code,
            "erro_java": response.text
        }), 500


def getRepresentanteUser(idrep):
    try:
        rep = int(idrep)
        response = requests.get(f"http://127.0.0.1:8080/rep/{rep}", timeout=3)

        # Se a resposta não tiver conteúdo, retorna None
        if not response.content or response.status_code != 200:
            print(f"API retornou status {response.status_code} com body: {response.text}")
            return None

        # Tenta decodificar JSON, mas captura falha
        try:
            return response.json()
        except Exception as e:
            print("Resposta não é JSON:", response.text)
            return None

    except Exception as e:
        print("Erro ao buscar representante:", e)
        return None

def altera_senha_representante(senha):
    print(senha)
    if senha:
        try:
            print(current_user.id)
            response = requests.put(
                f"http://127.0.0.1:8080/rep/{current_user.id}/senha",
                data=senha  # envia como texto puro, não JSON
            )

            if response.status_code == 200:
                flash("Senha alterada com sucesso!", "success")
            else:
                flash("Erro ao alterar senha!", "danger")

        except Exception as e:
            flash(f"Erro ao conectar com API: {e}", "danger")
    else:
        flash("Digite uma nova senha.", "warning")
