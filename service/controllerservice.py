from flask import Blueprint, jsonify, redirect, url_for, render_template
import requests

from service.calculosForecast import calcular_medias_vendas


# Cria o blueprint
service_bp = Blueprint('service_bp', __name__)

@service_bp.route('/getDadosForecastProduto')
def getDadosForecastProduto():
    response = requests.get("http://127.0.0.1:8080/forecast/dadosproduto")
    produtos = response.json()

    df_resultado = calcular_medias_vendas(produtos)

    lista_resultado = df_resultado.to_dict(orient='records')
    return lista_resultado

@service_bp.route('/getDadosVendaCliente')
def get_dados_forecast_venda_cliente():
    response = requests.get("http://127.0.0.1:8080/forecast/dadosvendacliente")
    vendasCliente = response.json()
    return vendasCliente

@service_bp.route('/getDadosVendaClienteId/<int:id>', methods=['GET'])
def get_dados_forecast_venda_cliente_id(id):
    try:
        url = f"http://localhost:8080/forecast/dadosvendaclienteid/{id}"
        response = requests.get(url)

        if response.status_code == 200:
            vendasCliente = response.json()
            return jsonify(vendasCliente), 200
        else:
            return jsonify(
                {"erro": f"Erro ao obter dados do cliente. Status: {response.status_code}"}), response.status_code
    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@service_bp.route('/atualizarRegistros')
def atualizarTodos():
    response = requests.get("http://127.0.0.1:8080/atualiza/todos")
    if response.status_code == 200:
        return jsonify({"mensagem": "Registros atualizados com sucesso!"})
    else:
        return jsonify({"mensagem": "Erro ao atualizar"}), 500


