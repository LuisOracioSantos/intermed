from collections import defaultdict, Counter


def agrupar_vendas_por_cliente(vendas):
    agrupado = defaultdict(lambda: {'codigo': None, 'cliente': '', 'total_venda': 0.0, 'qtd_vendas': 0, 'dataCadastroCli':None})
    for venda in vendas:
        cid = venda['idCliente']
        agrupado[cid]['codigo'] = cid
        agrupado[cid]['cliente'] = venda['apelido']
        agrupado[cid]['total_venda'] += venda.get('vlrTotalItem', 0.0)
        agrupado[cid]['qtd_vendas'] += 1
        if agrupado[cid]['dataCadastroCli'] is None:
            agrupado[cid]['dataCadastroCli'] = venda.get('dataCadastroCli')
    return list(agrupado.values())

def clientes_valiosos(vendas, limite=50000.00):
    clientes = agrupar_vendas_por_cliente(vendas)
    valiosos = [c for c in clientes if c['total_venda'] > limite]
    return sorted(valiosos, key=lambda x: x['cliente'])

def clientes_nao_valiosos(vendas, limite=1000):
    clientes = agrupar_vendas_por_cliente(vendas)
    nao_valiosos = [c for c in clientes if 1 < c['qtd_vendas'] and c['total_venda'] <= limite]
    return sorted(nao_valiosos, key=lambda x: x['cliente'])


def clientes_compraram_uma_vez(vendas):
    contador = Counter(v['idCliente'] for v in vendas)
    clientes_uma_vez = [v for v in vendas if contador[v['idCliente']] == 1]
    resultado = []
    for v in clientes_uma_vez:
        resultado.append({
            'codigo': v['idCliente'],
            'cliente': v['apelido'],
            'total_venda': v['vlrTotalItem'],
            'dataCadastroCli': v.get('dataCadastroCli')
        })
    return sorted(resultado, key=lambda x: x['cliente'])