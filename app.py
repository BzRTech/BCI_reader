import os
import re
import uuid
from flask import Flask, request, jsonify, render_template
import pdfplumber

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Campos típicos de um BCI - Boletim de Cadastro Imobiliário
BCI_FIELDS = [
    ('inscricao', r'(?:inscrição|inscri[cç][aã]o\s*(?:imobili[aá]ria)?|c[oó]digo\s*(?:do\s*)?im[oó]vel)\s*[:\-]?\s*(.+?)(?:\n|$)'),
    ('setor', r'(?:setor)\s*[:\-]?\s*(.+?)(?:\n|$)'),
    ('quadra', r'(?:quadra)\s*[:\-]?\s*(.+?)(?:\n|$)'),
    ('lote', r'(?:lote)\s*[:\-]?\s*(.+?)(?:\n|$)'),
    ('unidade', r'(?:unidade)\s*[:\-]?\s*(.+?)(?:\n|$)'),
    ('proprietario', r'(?:propriet[aá]rio|nome\s*(?:do\s*)?propriet[aá]rio)\s*[:\-]?\s*(.+?)(?:\n|$)'),
    ('cpf_cnpj', r'(?:cpf|cnpj|cpf\s*/\s*cnpj)\s*[:\-]?\s*(.+?)(?:\n|$)'),
    ('endereco', r'(?:endere[cç]o|logradouro)\s*[:\-]?\s*(.+?)(?:\n|$)'),
    ('numero', r'(?:n[uú]mero|n[°º])\s*[:\-]?\s*(.+?)(?:\n|$)'),
    ('complemento', r'(?:complemento)\s*[:\-]?\s*(.+?)(?:\n|$)'),
    ('bairro', r'(?:bairro)\s*[:\-]?\s*(.+?)(?:\n|$)'),
    ('cidade', r'(?:cidade|munic[ií]pio)\s*[:\-]?\s*(.+?)(?:\n|$)'),
    ('cep', r'(?:cep)\s*[:\-]?\s*(\d[\d.\-/]+)'),
    ('area_terreno', r'(?:[aá]rea\s*(?:do\s*)?terreno)\s*[:\-]?\s*(.+?)(?:\n|$)'),
    ('area_construida', r'(?:[aá]rea\s*(?:constru[ií]da|edifica[cç][aã]o))\s*[:\-]?\s*(.+?)(?:\n|$)'),
    ('uso', r'(?:uso\s*(?:do\s*)?im[oó]vel|tipo\s*(?:de\s*)?uso|utiliza[cç][aã]o)\s*[:\-]?\s*(.+?)(?:\n|$)'),
    ('padrao', r'(?:padr[aã]o\s*(?:(?:de\s*)?constru[cç][aã]o)?|padr[aã]o\s*construtivo)\s*[:\-]?\s*(.+?)(?:\n|$)'),
    ('tipo_construcao', r'(?:tipo\s*(?:de\s*)?constru[cç][aã]o|tipologia)\s*[:\-]?\s*(.+?)(?:\n|$)'),
    ('estado_conservacao', r'(?:estado\s*(?:de\s*)?conserva[cç][aã]o)\s*[:\-]?\s*(.+?)(?:\n|$)'),
    ('ano_construcao', r'(?:ano\s*(?:da\s*)?constru[cç][aã]o)\s*[:\-]?\s*(\d{4})'),
    ('testada', r'(?:testada|frente)\s*[:\-]?\s*(.+?)(?:\n|$)'),
    ('profundidade', r'(?:profundidade|fundos)\s*[:\-]?\s*(.+?)(?:\n|$)'),
    ('topografia', r'(?:topografia|relevo)\s*[:\-]?\s*(.+?)(?:\n|$)'),
    ('situacao', r'(?:situa[cç][aã]o)\s*[:\-]?\s*(.+?)(?:\n|$)'),
    ('pedologia', r'(?:pedologia|solo)\s*[:\-]?\s*(.+?)(?:\n|$)'),
    ('valor_venal', r'(?:valor\s*venal)\s*[:\-]?\s*(.+?)(?:\n|$)'),
]


def split_bcis(text):
    """Divide o texto em múltiplos BCIs se houver mais de um no documento."""
    # Padrões comuns que indicam início de um novo BCI
    split_patterns = [
        r'(?=BOLETIM\s+DE\s+CADASTRO\s+IMOBILI[AÁ]RIO)',
        r'(?=B\s*\.\s*C\s*\.\s*I\s*\.?\s)',
        r'(?=BCI\s*[\-\s:nN°º]+\s*\d)',
        r'(?=BOLETIM\s*N[°º]?\s*\d)',
    ]

    for pattern in split_patterns:
        parts = re.split(pattern, text, flags=re.IGNORECASE)
        parts = [p.strip() for p in parts if p.strip()]
        if len(parts) > 1:
            return parts

    return [text]


def extract_tables_from_pages(pages):
    """Extrai tabelas diretamente das páginas do PDF usando pdfplumber."""
    all_tables = []
    for page in pages:
        tables = page.extract_tables()
        for table in tables:
            if table:
                all_tables.append(table)
    return all_tables


def parse_bci_from_text(text):
    """Extrai campos do BCI a partir do texto."""
    bci = {}
    for field_name, pattern in BCI_FIELDS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1).strip()
            # Limpar valores
            value = re.sub(r'\s+', ' ', value)
            if value and value not in ['-', '–', '—', '.', ':', '/']:
                bci[field_name] = value
    return bci


def parse_bci_from_tables(tables):
    """Tenta extrair campos do BCI a partir de tabelas extraídas do PDF."""
    bci = {}
    for table in tables:
        for row in table:
            if not row or len(row) < 2:
                continue
            # Verificar pares chave-valor nas células
            for i in range(len(row) - 1):
                cell_key = str(row[i] or '').strip().lower()
                cell_val = str(row[i + 1] or '').strip()
                if not cell_key or not cell_val:
                    continue
                for field_name, pattern in BCI_FIELDS:
                    # Simplificar: verificar se a chave do campo aparece no nome da célula
                    field_keywords = {
                        'inscricao': ['inscrição', 'inscricao', 'código imóvel'],
                        'setor': ['setor'],
                        'quadra': ['quadra'],
                        'lote': ['lote'],
                        'unidade': ['unidade'],
                        'proprietario': ['proprietário', 'proprietario', 'nome'],
                        'cpf_cnpj': ['cpf', 'cnpj'],
                        'endereco': ['endereço', 'endereco', 'logradouro'],
                        'numero': ['número', 'numero', 'n°', 'nº'],
                        'complemento': ['complemento'],
                        'bairro': ['bairro'],
                        'cidade': ['cidade', 'município', 'municipio'],
                        'cep': ['cep'],
                        'area_terreno': ['área terreno', 'area terreno'],
                        'area_construida': ['área construída', 'area construida', 'área edificação'],
                        'uso': ['uso'],
                        'padrao': ['padrão', 'padrao'],
                        'tipo_construcao': ['tipo construção', 'tipo construcao', 'tipologia'],
                        'estado_conservacao': ['conservação', 'conservacao'],
                        'ano_construcao': ['ano construção', 'ano construcao'],
                        'testada': ['testada', 'frente'],
                        'profundidade': ['profundidade', 'fundos'],
                        'topografia': ['topografia', 'relevo'],
                        'situacao': ['situação', 'situacao'],
                        'pedologia': ['pedologia', 'solo'],
                        'valor_venal': ['valor venal'],
                    }
                    keywords = field_keywords.get(field_name, [])
                    if any(kw in cell_key for kw in keywords):
                        if cell_val not in ['-', '–', '—', '.', ':', '/']:
                            bci[field_name] = cell_val
                        break
    return bci


def process_pdf(filepath):
    """Processa um PDF e retorna lista de BCIs encontrados."""
    bcis = []

    with pdfplumber.open(filepath) as pdf:
        # Extrair texto completo
        full_text = ''
        for page in pdf.pages:
            page_text = page.extract_text() or ''
            full_text += page_text + '\n'

        # Extrair tabelas
        all_tables = extract_tables_from_pages(pdf.pages)

        # Dividir em múltiplos BCIs
        bci_texts = split_bcis(full_text)

        for i, bci_text in enumerate(bci_texts):
            # Extrair campos do texto
            bci_data = parse_bci_from_text(bci_text)

            # Se for o primeiro (ou único), tentar também tabelas
            if i == 0 and all_tables:
                table_data = parse_bci_from_tables(all_tables)
                # Mesclar: texto tem prioridade, tabela preenche lacunas
                for key, val in table_data.items():
                    if key not in bci_data:
                        bci_data[key] = val

            if bci_data:
                bci_data['_bci_index'] = i + 1
                bcis.append(bci_data)

        # Se nenhum campo foi extraído via regex, retornar texto bruto
        if not bcis:
            bcis.append({
                '_bci_index': 1,
                '_raw_text': full_text[:5000],
                '_aviso': 'Não foi possível extrair campos automaticamente. Texto bruto exibido abaixo.'
            })

    return bcis


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    if 'files' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400

    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400

    all_results = []

    for file in files:
        if not file.filename:
            continue
        if not file.filename.lower().endswith('.pdf'):
            all_results.append({
                'filename': file.filename,
                'error': 'Arquivo não é PDF',
                'bcis': []
            })
            continue

        # Salvar temporariamente
        safe_name = f"{uuid.uuid4().hex}.pdf"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)

        try:
            file.save(filepath)
            bcis = process_pdf(filepath)
            all_results.append({
                'filename': file.filename,
                'bcis': bcis,
                'total_bcis': len(bcis)
            })
        except Exception as e:
            all_results.append({
                'filename': file.filename,
                'error': str(e),
                'bcis': []
            })
        finally:
            # Remover arquivo temporário
            if os.path.exists(filepath):
                os.remove(filepath)

    return jsonify({'results': all_results})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
