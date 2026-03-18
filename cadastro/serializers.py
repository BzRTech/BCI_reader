from rest_framework import serializers

from .models import BCI, Parcela, Validacao


class ValidacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Validacao
        fields = ['id', 'campo', 'tipo', 'mensagem', 'criado_em']
        read_only_fields = ['id', 'criado_em']


class BCISerializer(serializers.ModelSerializer):
    class Meta:
        model = BCI
        fields = [
            'id', 'parcela',
            # Proprietário
            'proprietario', 'cpf_cnpj', 'telefone',
            'endereco_correspondencia', 'tipo_dominio',
            # Terreno
            'area_terreno', 'frente', 'fundo',
            'lado_direito', 'lado_esquerdo',
            'situacao', 'topografia', 'pedologia', 'nivelamento',
            # Construção
            'possui_construcao', 'uso', 'tipo_construcao',
            'padrao_construtivo', 'estado_conservacao',
            'ano_construcao', 'area_construida',
            'num_pavimentos', 'num_comodos',
            # Valor
            'valor_venal',
            # Meta
            'raw_json', 'extraido_em',
        ]
        read_only_fields = ['id', 'extraido_em']


class ParcelaSerializer(serializers.ModelSerializer):
    validacoes = ValidacaoSerializer(many=True, read_only=True)
    ultimo_bci = serializers.SerializerMethodField()

    class Meta:
        model = Parcela
        fields = [
            'id', 'inscricao', 'distrito', 'setor', 'quadra', 'lote',
            'logradouro', 'numero', 'complemento', 'bairro', 'cep',
            'area_terreno', 'area_construida',
            'status_validacao',
            'criado_em', 'atualizado_em',
            'validacoes', 'ultimo_bci',
        ]
        read_only_fields = ['id', 'criado_em', 'atualizado_em', 'status_validacao']

    def get_ultimo_bci(self, obj):
        bci = obj.bcis.order_by('-extraido_em').first()
        if bci:
            return BCISerializer(bci).data
        return None


class ParcelaListSerializer(serializers.ModelSerializer):
    """Serializer leve para listagem (sem BCIs e validações aninhados)."""

    class Meta:
        model = Parcela
        fields = [
            'id', 'inscricao', 'distrito', 'setor', 'quadra', 'lote',
            'logradouro', 'numero', 'bairro',
            'area_terreno', 'area_construida',
            'status_validacao',
        ]


class PDFUploadSerializer(serializers.Serializer):
    """Serializer para upload de PDF de BCI."""
    arquivo = serializers.FileField()
    parcela_id = serializers.IntegerField(required=False, help_text='ID da parcela (opcional)')
