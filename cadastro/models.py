from django.conf import settings
from django.db import models

# Usar GeoDjango apenas quando o banco suportar PostGIS
_USE_GIS = 'gis' in settings.DATABASES.get('default', {}).get('ENGINE', '')

if _USE_GIS:
    from django.contrib.gis.db import models as gis_models


class Parcela(models.Model):
    """Parcela/lote com geometria georreferenciada."""

    STATUS_CHOICES = [
        ('ok', 'Regular'),
        ('alerta', 'Alerta'),
        ('erro', 'Irregular'),
        ('vazio', 'Não vistoriado'),
    ]

    inscricao = models.CharField('Inscrição Cadastral', max_length=30, unique=True)
    distrito = models.CharField('Distrito', max_length=10, blank=True, default='')
    setor = models.CharField('Setor', max_length=10, blank=True, default='')
    quadra = models.CharField('Quadra', max_length=10, blank=True, default='')
    lote = models.CharField('Lote', max_length=10, blank=True, default='')
    logradouro = models.TextField('Logradouro', blank=True, default='')
    numero = models.CharField('Número', max_length=20, blank=True, default='')
    complemento = models.CharField('Complemento', max_length=100, blank=True, default='')
    bairro = models.CharField('Bairro', max_length=100, blank=True, default='')
    cep = models.CharField('CEP', max_length=10, blank=True, default='')
    area_terreno = models.DecimalField(
        'Área do Terreno (m²)', max_digits=12, decimal_places=2, null=True, blank=True
    )
    area_construida = models.DecimalField(
        'Área Construída (m²)', max_digits=12, decimal_places=2, null=True, blank=True
    )
    # Geometria - SIRGAS 2000 (EPSG:4674)
    # Só disponível com PostGIS; com SQLite esse campo é armazenado como texto
    if _USE_GIS:
        geom = gis_models.PolygonField(srid=4674, null=True, blank=True)
    else:
        geom = models.TextField('Geometria (WKT)', null=True, blank=True)
    status_validacao = models.CharField(
        'Status de Validação', max_length=20, choices=STATUS_CHOICES, default='vazio'
    )
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Parcela'
        verbose_name_plural = 'Parcelas'
        ordering = ['inscricao']

    def __str__(self):
        return f'{self.inscricao} - {self.logradouro}, {self.numero}'


class BCI(models.Model):
    """Boletim de Cadastro Imobiliário - dados extraídos dos PDFs."""

    TIPO_DOMINIO_CHOICES = [
        ('pleno', 'Domínio Pleno'),
        ('util', 'Domínio Útil'),
        ('direto', 'Domínio Direto'),
        ('posse', 'Posse'),
        ('usufrutuario', 'Usufrutuário'),
    ]

    USO_CHOICES = [
        ('residencial_unifamiliar', 'Residencial Unifamiliar'),
        ('residencial_multifamiliar', 'Residencial Multifamiliar'),
        ('comercial', 'Comercial'),
        ('industrial', 'Industrial'),
        ('servicos', 'Serviços'),
        ('misto', 'Misto'),
        ('institucional', 'Institucional'),
    ]

    TIPO_CONSTRUCAO_CHOICES = [
        ('casa', 'Casa'),
        ('apartamento', 'Apartamento'),
        ('sala_comercial', 'Sala Comercial'),
        ('loja', 'Loja'),
        ('galpao', 'Galpão'),
        ('barracao', 'Barracão'),
    ]

    PADRAO_CHOICES = [
        ('popular', 'Popular'),
        ('simples', 'Simples'),
        ('normal', 'Normal'),
        ('bom', 'Bom'),
        ('otimo', 'Ótimo'),
        ('luxo', 'Luxo'),
    ]

    ESTADO_CHOICES = [
        ('otimo', 'Ótimo'),
        ('bom', 'Bom'),
        ('regular', 'Regular'),
        ('precario', 'Precário'),
        ('ruina', 'Ruína'),
    ]

    SITUACAO_CHOICES = [
        ('meio_quadra', 'Meio de Quadra'),
        ('esquina', 'Esquina'),
        ('encravado', 'Encravado'),
        ('vila', 'Vila'),
        ('gleba', 'Gleba'),
    ]

    TOPOGRAFIA_CHOICES = [
        ('plano', 'Plano'),
        ('aclive', 'Aclive'),
        ('declive', 'Declive'),
        ('irregular', 'Irregular'),
    ]

    PEDOLOGIA_CHOICES = [
        ('seco', 'Seco'),
        ('inundavel', 'Inundável'),
        ('alagado', 'Alagado'),
        ('pantanoso', 'Pantanoso'),
    ]

    parcela = models.ForeignKey(
        Parcela, on_delete=models.CASCADE, related_name='bcis'
    )

    # Proprietário / Possuidor
    proprietario = models.CharField('Proprietário', max_length=255, blank=True, default='')
    cpf_cnpj = models.CharField('CPF/CNPJ', max_length=20, blank=True, default='')
    telefone = models.CharField('Telefone', max_length=20, blank=True, default='')
    endereco_correspondencia = models.TextField(
        'Endereço para correspondência', blank=True, default=''
    )
    tipo_dominio = models.CharField(
        'Tipo de Domínio', max_length=20, choices=TIPO_DOMINIO_CHOICES,
        blank=True, default=''
    )

    # Terreno
    area_terreno = models.DecimalField(
        'Área do Terreno (m²)', max_digits=12, decimal_places=2, null=True, blank=True
    )
    frente = models.DecimalField(
        'Testada Frontal (m)', max_digits=8, decimal_places=2, null=True, blank=True
    )
    fundo = models.DecimalField(
        'Fundo (m)', max_digits=8, decimal_places=2, null=True, blank=True
    )
    lado_direito = models.DecimalField(
        'Lado Direito (m)', max_digits=8, decimal_places=2, null=True, blank=True
    )
    lado_esquerdo = models.DecimalField(
        'Lado Esquerdo (m)', max_digits=8, decimal_places=2, null=True, blank=True
    )
    situacao = models.CharField(
        'Situação na Quadra', max_length=20, choices=SITUACAO_CHOICES,
        blank=True, default=''
    )
    topografia = models.CharField(
        'Topografia', max_length=20, choices=TOPOGRAFIA_CHOICES,
        blank=True, default=''
    )
    pedologia = models.CharField(
        'Pedologia', max_length=20, choices=PEDOLOGIA_CHOICES,
        blank=True, default=''
    )
    nivelamento = models.CharField(
        'Nivelamento', max_length=20, blank=True, default=''
    )

    # Construção
    possui_construcao = models.BooleanField('Possui Construção', default=False)
    uso = models.CharField(
        'Uso', max_length=30, choices=USO_CHOICES, blank=True, default=''
    )
    tipo_construcao = models.CharField(
        'Tipo de Construção', max_length=20, choices=TIPO_CONSTRUCAO_CHOICES,
        blank=True, default=''
    )
    padrao_construtivo = models.CharField(
        'Padrão Construtivo', max_length=20, choices=PADRAO_CHOICES,
        blank=True, default=''
    )
    estado_conservacao = models.CharField(
        'Estado de Conservação', max_length=20, choices=ESTADO_CHOICES,
        blank=True, default=''
    )
    ano_construcao = models.IntegerField('Ano de Construção', null=True, blank=True)
    area_construida = models.DecimalField(
        'Área Construída (m²)', max_digits=12, decimal_places=2, null=True, blank=True
    )
    num_pavimentos = models.IntegerField('Nº Pavimentos', null=True, blank=True)
    num_comodos = models.IntegerField('Nº Cômodos', null=True, blank=True)

    # Valor
    valor_venal = models.DecimalField(
        'Valor Venal (R$)', max_digits=15, decimal_places=2, null=True, blank=True
    )

    # Dados brutos da extração
    raw_json = models.JSONField('JSON bruto da extração', null=True, blank=True)
    extraido_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'BCI'
        verbose_name_plural = 'BCIs'
        ordering = ['-extraido_em']

    def __str__(self):
        return f'BCI #{self.pk} - {self.parcela.inscricao}'


class Validacao(models.Model):
    """Resultado de validação de uma parcela/BCI."""

    TIPO_CHOICES = [
        ('erro', 'Erro'),
        ('alerta', 'Alerta'),
    ]

    parcela = models.ForeignKey(
        Parcela, on_delete=models.CASCADE, related_name='validacoes'
    )
    campo = models.CharField('Campo', max_length=50)
    tipo = models.CharField('Tipo', max_length=10, choices=TIPO_CHOICES)
    mensagem = models.TextField('Mensagem')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Validação'
        verbose_name_plural = 'Validações'
        ordering = ['-criado_em']

    def __str__(self):
        return f'[{self.tipo}] {self.campo}: {self.mensagem}'
