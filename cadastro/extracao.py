"""Extração de dados de BCI a partir de PDFs usando pdfplumber + Anthropic API."""

import json
import os

import pdfplumber

from .models import BCI
from .serializers import BCISerializer


# Prompt para a API Claude extrair campos do BCI
PROMPT_EXTRACAO = """Analise o texto a seguir, extraído de um PDF de Boletim de Cadastro Imobiliário (BCI).
Extraia os seguintes campos e retorne APENAS um JSON válido (sem markdown, sem explicação):

{
  "proprietario": "nome do proprietário",
  "cpf_cnpj": "CPF ou CNPJ",
  "telefone": "telefone",
  "endereco_correspondencia": "endereço de correspondência",
  "tipo_dominio": "pleno|util|direto|posse|usufrutuario",
  "area_terreno": 0.0,
  "frente": 0.0,
  "fundo": 0.0,
  "lado_direito": 0.0,
  "lado_esquerdo": 0.0,
  "situacao": "meio_quadra|esquina|encravado|vila|gleba",
  "topografia": "plano|aclive|declive|irregular",
  "pedologia": "seco|inundavel|alagado|pantanoso",
  "nivelamento": "nivel|acima|abaixo",
  "possui_construcao": true,
  "uso": "residencial_unifamiliar|residencial_multifamiliar|comercial|industrial|servicos|misto|institucional",
  "tipo_construcao": "casa|apartamento|sala_comercial|loja|galpao|barracao",
  "padrao_construtivo": "popular|simples|normal|bom|otimo|luxo",
  "estado_conservacao": "otimo|bom|regular|precario|ruina",
  "ano_construcao": 0,
  "area_construida": 0.0,
  "num_pavimentos": 0,
  "num_comodos": 0,
  "valor_venal": 0.0
}

Se um campo não for encontrado, use null. Para campos numéricos, retorne o número sem unidade.
Para campos com opções fixas, use exatamente uma das opções listadas.

TEXTO DO PDF:
"""


def extrair_texto_pdf(filepath):
    """Extrai texto de todas as páginas do PDF."""
    texto = ''
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ''
            texto += page_text + '\n'
    return texto


def extrair_via_anthropic(texto):
    """Usa a API Anthropic para extrair campos estruturados do BCI."""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        return None, 'ANTHROPIC_API_KEY não configurada'

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

        message = client.messages.create(
            model='claude-sonnet-4-20250514',
            max_tokens=2000,
            messages=[{
                'role': 'user',
                'content': PROMPT_EXTRACAO + texto[:8000],
            }],
        )

        response_text = message.content[0].text.strip()

        # Tentar parsear como JSON
        # Remover possíveis markdown code blocks
        if response_text.startswith('```'):
            lines = response_text.split('\n')
            response_text = '\n'.join(lines[1:-1])

        dados = json.loads(response_text)
        return dados, None

    except json.JSONDecodeError as e:
        return None, f'Erro ao parsear resposta da IA: {e}'
    except Exception as e:
        return None, f'Erro na API Anthropic: {e}'


def extrair_bci_de_pdf(filepath, parcela):
    """
    Processa um PDF, extrai dados via Anthropic e cria um BCI vinculado à parcela.
    Retorna dict com resultado.
    """
    texto = extrair_texto_pdf(filepath)

    if not texto.strip():
        return {
            'sucesso': False,
            'erro': 'PDF sem texto extraível',
        }

    dados, erro = extrair_via_anthropic(texto)

    if erro:
        return {
            'sucesso': False,
            'erro': erro,
            'texto_extraido': texto[:2000],
        }

    # Limpar campos None
    campos_bci = {}
    for campo, valor in dados.items():
        if valor is not None:
            campos_bci[campo] = valor

    # Criar BCI
    bci = BCI.objects.create(
        parcela=parcela,
        raw_json=dados,
        **campos_bci,
    )

    # Atualizar campos da parcela com dados extraídos
    update_fields = []
    if dados.get('area_terreno') and not parcela.area_terreno:
        parcela.area_terreno = dados['area_terreno']
        update_fields.append('area_terreno')
    if dados.get('area_construida') and not parcela.area_construida:
        parcela.area_construida = dados['area_construida']
        update_fields.append('area_construida')
    if update_fields:
        parcela.save(update_fields=update_fields)

    return {
        'sucesso': True,
        'bci_id': bci.id,
        'dados_extraidos': BCISerializer(bci).data,
    }
