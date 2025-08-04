import numpy as np
import pandas as pd


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

        ultimos_3_valores = ultimos_valores['totalvenda'].tail(3).tolist()

        # Preenche com 0.0 se tiver menos de 3 valores
        while len(ultimos_3_valores) < 3:
            ultimos_3_valores.insert(0, 0.0)

        # Substitui None/NaN por 0.0 explicitamente
        ultimos_3_valores = [0.0 if v is None or pd.isna(v) else float(v) for v in ultimos_3_valores]

        # Cálculo das métricas
        media_3 = round(np.mean(ultimos_3_valores), 2)
        desvio_padrao = round(np.std(ultimos_3_valores, ddof=1), 2) if len(ultimos_3_valores) >= 2 else 0.0
        media_6 = round(ultimos_valores['totalvenda'].fillna(0.0).mean(), 2)

        resumo.append({
            'item': item,
            'descricao': descricao,
            'mes1': ultimos_3_valores[0],
            'mes2': ultimos_3_valores[1],
            'mes3': ultimos_3_valores[2],
            'media_trimestre': media_3,
            'media_semestre': media_6,
            'desviopadrao_trimestre': desvio_padrao,
            'saldodisponivel': grupo_ordenado['saldodisponivel'].iloc[-1] if 'saldodisponivel' in grupo_ordenado.columns else None
        })

    return pd.DataFrame(resumo)



