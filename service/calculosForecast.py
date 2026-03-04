import statistics

def calcular_desvio_padrao(mes1, mes2, mes3):
    valores = [mes1, mes2, mes3]
    # Filtrar apenas valores numéricos > 0
    valores_validos = [v for v in valores if isinstance(v, (int, float))]

    if len(valores_validos) > 1:
        return round(statistics.stdev(valores_validos), 2)
    else:
        return 0.0



