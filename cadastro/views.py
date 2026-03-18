import os
import tempfile

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from .models import BCI, Parcela, Validacao
from .serializers import (
    BCISerializer,
    ParcelaListSerializer,
    ParcelaSerializer,
    PDFUploadSerializer,
    ValidacaoSerializer,
)
from .validacao import validar_bci
from .extracao import extrair_bci_de_pdf


class ParcelaViewSet(viewsets.ModelViewSet):
    """CRUD de Parcelas + validação + upload de PDF."""
    queryset = Parcela.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return ParcelaListSerializer
        return ParcelaSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        inscricao = self.request.query_params.get('inscricao')
        if inscricao:
            qs = qs.filter(inscricao__icontains=inscricao)
        bairro = self.request.query_params.get('bairro')
        if bairro:
            qs = qs.filter(bairro__icontains=bairro)
        status_val = self.request.query_params.get('status')
        if status_val:
            qs = qs.filter(status_validacao=status_val)
        logradouro = self.request.query_params.get('logradouro')
        if logradouro:
            qs = qs.filter(logradouro__icontains=logradouro)
        return qs

    @action(detail=True, methods=['post'], url_path='validar')
    def validar(self, request, pk=None):
        """POST /api/parcelas/{id}/validar/ — executa validação do BCI."""
        parcela = self.get_object()
        resultado = validar_bci(parcela)
        return Response({
            'parcela_id': parcela.id,
            'inscricao': parcela.inscricao,
            'status': parcela.status_validacao,
            'erros': resultado['erros'],
            'alertas': resultado['alertas'],
        })

    @action(detail=True, methods=['post'], url_path='upload-pdf',
            parser_classes=[MultiPartParser])
    def upload_pdf(self, request, pk=None):
        """POST /api/parcelas/{id}/upload-pdf/ — extrai BCI de PDF."""
        parcela = self.get_object()
        serializer = PDFUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        arquivo = serializer.validated_data['arquivo']

        if not arquivo.name.lower().endswith('.pdf'):
            return Response(
                {'erro': 'Apenas arquivos PDF são aceitos'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            for chunk in arquivo.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            resultado = extrair_bci_de_pdf(tmp_path, parcela)
            return Response(resultado, status=status.HTTP_201_CREATED)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


class BCIViewSet(viewsets.ModelViewSet):
    """CRUD de BCIs."""
    queryset = BCI.objects.select_related('parcela').all()
    serializer_class = BCISerializer

    def get_queryset(self):
        qs = super().get_queryset()
        parcela_id = self.request.query_params.get('parcela_id')
        if parcela_id:
            qs = qs.filter(parcela_id=parcela_id)
        return qs


class ValidacaoViewSet(viewsets.ReadOnlyModelViewSet):
    """Listagem de validações (somente leitura)."""
    queryset = Validacao.objects.select_related('parcela').all()
    serializer_class = ValidacaoSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        parcela_id = self.request.query_params.get('parcela_id')
        if parcela_id:
            qs = qs.filter(parcela_id=parcela_id)
        return qs
