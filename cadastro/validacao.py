"""Engine de validação do BCI conforme NBR 14166."""

from datetime import datetime

from .models import Parcela, Validacao


REGRAS_BCI = [
    # Campos obrigatórios
    {
        'campo': 'proprietario',
        'label': 'Proprietário',
        'tipo': 'obrigatorio',
    },
    {
        'campo': 'inscricao',
        'label': 'Inscrição Cadastral',
        'tipo': 'obrigatorio',
        'source': 'parcela',
    },
    {
        'campo': 'area_terreno',
        'label': 'Área do Terreno',
        'tipo': 'obrigatorio',
    },
    {
        'campo': 'logradouro',
        'label': 'Logradouro',
        'tipo': 'obrigatorio',
        'source': 'parcela',
    },
    {
        'campo': 'uso',
        'label': 'Uso do Imóvel',
        'tipo': 'obrigatorio',
    },
    {
        'campo': 'frente',
        'label': 'Testada Frontal',
        'tipo': 'obrigatorio',
    },
]


def _get_value(bci, parcela, campo, source=None):
    """Obtém o valor de um campo do BCI ou da Parcela."""
    if source == 'parcela':
        return getattr(parcela, campo, None)
    return getattr(bci, campo, None)


def validar_bci(parcela):
    """
    Valida o BCI mais recente de uma parcela.
    Retorna dict com 'erros' e 'alertas'.
    Também persiste os resultados na tabela Validacao.
    """
    erros = []
    alertas = []

    # Buscar BCI mais recente
    bci = parcela.bcis.order_by('-extraido_em').first()

    if not bci:
        erros.append({
            'campo': 'bci',
            'label': 'BCI',
            'mensagem': 'Nenhum BCI cadastrado para esta parcela',
        })
        _salvar_validacoes(parcela, erros, alertas)
        return {'erros': erros, 'alertas': alertas}

    # Campos obrigatórios
    for regra in REGRAS_BCI:
        if regra['tipo'] != 'obrigatorio':
            continue
        valor = _get_value(bci, parcela, regra['campo'], regra.get('source'))
        if not valor or (isinstance(valor, str) and not valor.strip()):
            erros.append({
                'campo': regra['campo'],
                'label': regra['label'],
                'mensagem': 'Campo obrigatório não preenchido',
            })

    # Consistência: área construída <= área terreno
    if bci.area_construida and bci.area_terreno:
        if bci.area_construida > bci.area_terreno:
            erros.append({
                'campo': 'area_construida',
                'label': 'Área construída vs terreno',
                'mensagem': 'Área construída maior que área do terreno',
            })

    # Consistência: ano de construção
    ano_atual = datetime.now().year
    if bci.ano_construcao is not None:
        if bci.ano_construcao < 1850:
            alertas.append({
                'campo': 'ano_construcao',
                'label': 'Ano de construção',
                'mensagem': f'Ano de construção anterior a 1850 ({bci.ano_construcao})',
            })
        if bci.ano_construcao > ano_atual:
            erros.append({
                'campo': 'ano_construcao',
                'label': 'Ano de construção',
                'mensagem': f'Ano de construção no futuro ({bci.ano_construcao})',
            })

    # Consistência: valor venal
    if bci.valor_venal is not None and bci.valor_venal <= 0:
        erros.append({
            'campo': 'valor_venal',
            'label': 'Valor venal',
            'mensagem': 'Valor venal deve ser positivo',
        })

    # Persistir e atualizar status da parcela
    _salvar_validacoes(parcela, erros, alertas)

    return {'erros': erros, 'alertas': alertas}


def _salvar_validacoes(parcela, erros, alertas):
    """Persiste os resultados da validação e atualiza o status da parcela."""
    # Limpar validações anteriores
    parcela.validacoes.all().delete()

    # Criar novas
    validacoes = []
    for erro in erros:
        validacoes.append(Validacao(
            parcela=parcela,
            campo=erro['campo'],
            tipo='erro',
            mensagem=erro['mensagem'],
        ))
    for alerta in alertas:
        validacoes.append(Validacao(
            parcela=parcela,
            campo=alerta['campo'],
            tipo='alerta',
            mensagem=alerta['mensagem'],
        ))
    if validacoes:
        Validacao.objects.bulk_create(validacoes)

    # Atualizar status da parcela
    if erros:
        parcela.status_validacao = 'erro'
    elif alertas:
        parcela.status_validacao = 'alerta'
    else:
        parcela.status_validacao = 'ok'
    parcela.save(update_fields=['status_validacao'])
