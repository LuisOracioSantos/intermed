import pandas as pd
from datetime import datetime

def calcular_medias_vendas(dados_vendas_api: list) -> pd.DataFrame:

    if not dados_vendas_api:
        return pd.DataFrame()

    df = pd.DataFrame(dados_vendas_api)

    # Padroniza nomes das colunas
    df.columns = [col.lower() for col in df.columns]

    # Converte a coluna de data
    df['mes'] = pd.to_datetime(df['mes'])

    resumo = []

    for (item, descricao), grupo in df.groupby(['item', 'descricao']):
        grupo_ordenado = grupo.sort_values(by='mes')
        ultimos_valores = grupo_ordenado.tail(6).copy()

        media_3 = ultimos_valores['totalvenda'].tail(3).mean()
        media_6 = ultimos_valores['totalvenda'].mean()

        ultimos_3_valores = ultimos_valores['totalvenda'].tail(3).tolist()

        while len(ultimos_3_valores) < 3:
            ultimos_3_valores.insert(0, None)

        resumo.append({
            'item': item,
            'descricao': descricao,
            'mes1': ultimos_3_valores[0],
            'mes2': ultimos_3_valores[1],
            'mes3': ultimos_3_valores[2],
            'media_trimestre': round(media_3, 2),
            'media_semestre': round(media_6, 2),
            'saldodisponivel' : grupo_ordenado['saldodisponivel'].iloc[-1] if 'saldodisponivel' in grupo_ordenado.columns else None
        })

    print(resumo)

    return pd.DataFrame(resumo)



