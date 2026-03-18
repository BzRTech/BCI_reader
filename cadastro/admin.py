from django.contrib import admin

from .models import BCI, Parcela, Validacao


@admin.register(Parcela)
class ParcelaAdmin(admin.ModelAdmin):
    list_display = ['inscricao', 'logradouro', 'numero', 'bairro', 'status_validacao']
    list_filter = ['status_validacao', 'bairro']
    search_fields = ['inscricao', 'logradouro', 'bairro']


@admin.register(BCI)
class BCIAdmin(admin.ModelAdmin):
    list_display = ['id', 'parcela', 'proprietario', 'uso', 'extraido_em']
    list_filter = ['uso', 'tipo_construcao']
    search_fields = ['proprietario', 'parcela__inscricao']


@admin.register(Validacao)
class ValidacaoAdmin(admin.ModelAdmin):
    list_display = ['parcela', 'campo', 'tipo', 'mensagem', 'criado_em']
    list_filter = ['tipo']
