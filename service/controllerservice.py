from flask import Blueprint, jsonify, redirect, url_for, render_template
import requests

from service.calculosForecast import calcular_medias_vendas


# Cria o blueprint
service_bp = Blueprint('service_bp', __name__)

@service_bp.route('/getDadosForecast')
def buscadados():
    response = requests.get("http://127.0.0.1:8080/forecast/dadosvendas")
    produtos = response.json()
    print(produtos)


    df_resultado = calcular_medias_vendas(produtos)

    print(df_resultado)

    lista_resultado = df_resultado.to_dict(orient='records')

    return lista_resultado