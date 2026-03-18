# BzR CTM — Briefing para Claude Code

## Contexto do Desenvolvedor
- **Nome:** Filipe Bezerra — CEO da BzR Technology, João Pessoa/PB
- **Stack dominada:** Django, React, PostgreSQL/PostGIS, AWS, ArcGIS Pro, Python
- **Já tem:** Pipeline de extração de PDFs de BCI via API Anthropic (Jupyter Notebook funcional)

---

## O Produto: BzR CTM

Sistema WebGIS de Cadastro Territorial Multifinalitário (CTM) **vendável para prefeituras brasileiras**.

### Proposta de valor
> Digitalize o cadastro imobiliário municipal, identifique inconsistências no BCI e consulte qualquer imóvel em segundos — sem instalar nada.

### Dor que resolve
- Maioria das prefeituras pequenas tem BCI em papel ou PDF desorganizado
- Diferencial competitivo: pipeline de extração com IA (Claude) já funcionando

---

## Funcionalidades Definidas

1. **Mapa de parcelas/lotes** com dados cadastrais e colorização por status de validação (verde/amarelo/vermelho)
2. **Formulário de preenchimento do BCI** — usuário clica no lote no mapa e preenche o formulário lateral
3. **Validação automática do BCI** — campos obrigatórios + consistência lógica (NBR 14166)
4. **Consulta de imóvel** por inscrição cadastral ou endereço
5. **Relatórios e estatísticas cadastrais** exportáveis (PDF/Excel)
6. **Importação de PDFs** → extração automática via API Claude

---

## Stack Técnica Definida

```
Frontend  →  React + MapLibre GL JS + Tailwind CSS  →  Vercel (grátis)
Backend   →  Django + Django REST Framework          →  Render.com (grátis p/ MVP)
Banco     →  PostgreSQL + PostGIS                   →  Supabase (grátis p/ MVP)
Mapas     →  MapLibre GL JS (tiles vetoriais)
IA        →  Anthropic API (extração de BCI de PDFs) — já implementado
```

---

## Modelo de Dados (PostgreSQL + PostGIS)

```sql
-- Parcelas com geometria
CREATE TABLE parcelas (
  id              SERIAL PRIMARY KEY,
  inscricao       VARCHAR(30) UNIQUE NOT NULL,
  logradouro      TEXT,
  numero          TEXT,
  bairro          TEXT,
  area_terreno    NUMERIC(12,2),
  area_construida NUMERIC(12,2),
  geom            GEOMETRY(Polygon, 4674),  -- SIRGAS 2000
  status_validacao VARCHAR(20)              -- 'ok' | 'alerta' | 'erro'
);

-- Dados do BCI extraídos dos PDFs
CREATE TABLE bci (
  id              SERIAL PRIMARY KEY,
  parcela_id      INT REFERENCES parcelas(id),
  proprietario    TEXT,
  uso             TEXT,
  padrao_const    TEXT,
  ano_construcao  INT,
  valor_venal     NUMERIC(15,2),
  raw_json        JSONB,
  extraido_em     TIMESTAMP DEFAULT NOW()
);

-- Resultado da validação
CREATE TABLE validacoes (
  id          SERIAL PRIMARY KEY,
  parcela_id  INT REFERENCES parcelas(id),
  campo       TEXT,
  tipo        TEXT,            -- 'erro' | 'alerta'
  mensagem    TEXT,
  criado_em   TIMESTAMP DEFAULT NOW()
);
```

---

## Seções do Formulário BCI (NBR 14166)

### 1. Identificação do Imóvel
- Inscrição Cadastral (formato: DD.SS.QQQ.LLLL-D)
- Distrito, Setor, Quadra, Lote
- Logradouro, Número, Complemento, Bairro, CEP

### 2. Proprietário / Possuidor
- Nome completo / Razão Social
- CPF / CNPJ
- Telefone, Endereço para correspondência
- Tipo de domínio (pleno, útil, direto, posse, usufrutuário)

### 3. Terreno
- Área do terreno (m²)
- Testada frontal, Fundo, Lado direito, Lado esquerdo (metros)
- Situação na quadra (meio de quadra, esquina, encravado, vila, gleba)
- Topografia (plano, aclive, declive, irregular)
- Pedologia (seco, inundável, alagado, pantanoso)
- Nivelamento em relação ao leito da rua

### 4. Construção
- Possui construção? (sim/não)
- Uso (residencial unifamiliar, multifamiliar, comercial, industrial, serviços, misto, institucional)
- Tipo de construção (casa, apartamento, sala comercial, loja, galpão, barracão)
- Padrão construtivo (popular, simples, normal, bom, ótimo, luxo)
- Estado de conservação (ótimo, bom, regular, precário, ruína)
- Ano de construção
- Área construída (m²), Nº pavimentos, Nº cômodos

---

## Engine de Validação BCI

```python
REGRAS_BCI = [
    # Campos obrigatórios
    {"campo": "proprietario",  "tipo": "obrigatorio"},
    {"campo": "inscricao",     "tipo": "obrigatorio"},
    {"campo": "area_terreno",  "tipo": "obrigatorio"},
    {"campo": "logradouro",    "tipo": "obrigatorio"},
    {"campo": "uso",           "tipo": "obrigatorio"},

    # Consistência numérica
    {"regra": "area_construida <= area_terreno",  "tipo": "erro"},
    {"regra": "ano_construcao >= 1850",           "tipo": "alerta"},
    {"regra": "ano_construcao <= ano_atual",      "tipo": "erro"},
    {"regra": "valor_venal > 0",                  "tipo": "erro"},

    # Consistência geométrica (PostGIS)
    {"regra": "ST_IsValid(geom)",                 "tipo": "erro"},
    {"regra": "ST_Area(geom) > 0",                "tipo": "erro"},
]
```

---

## Protótipo Visual (já construído)

Foi desenvolvido um protótipo React interativo com:
- Mapa mock com lotes coloridos por status de validação
- Clique no lote abre formulário lateral com 4 seções
- Navegação por abas (Identificação / Proprietário / Terreno / Construção / Validação)
- Engine de validação funcional com resultado em painel dedicado
- Botões Salvar, Validar, Anterior/Próximo
- Visual: dark map (azul noturno) + formulário claro, identidade "BzR CTM"
- Arquivo do protótipo: bci-prototype.jsx (incluso junto a este briefing)

---

## Roadmap

```
Fase 1 — MVP (prioridade agora)
  ✅ Pipeline PDF → extração Claude (já existe)
  🔲 Models Django: Parcela, BCI, Validacao
  🔲 Django REST API (CRUD parcelas + BCI + validação)
  🔲 Supabase com PostGIS configurado
  🔲 Frontend React com MapLibre (substituir mapa mock)
  🔲 Formulário BCI integrado à API

Fase 2 — Produto
  🔲 Upload de PDFs no frontend
  🔲 Dashboard de validação
  🔲 Relatório exportável (PDF/Excel)
  🔲 Busca por inscrição/endereço

Fase 3 — Comercial
  🔲 Multi-tenant (um schema por município)
  🔲 Login/autenticação por prefeitura
  🔲 Migração para AWS EC2 (produção)
```

---

## Hospedagem

| Fase | Backend | Banco | Frontend |
|---|---|---|---|
| MVP / Portfólio | Render.com (grátis) | Supabase (grátis) | Vercel (grátis) |
| Produção (prefeitura) | AWS EC2 t3.small (~R$80/mês) | RDS PostgreSQL | Vercel |

Modelo de negócio sugerido: R$ 1.200/mês por município (R$ 100–200 cobre infra).

---

## Próxima Ação Sugerida para o Claude Code

Começar pelo backend Django:

1. Criar projeto Django + DRF com suporte a GeoDjango
2. Configurar PostGIS (django.contrib.gis)
3. Criar models: `Parcela`, `BCI`, `Validacao`
4. Criar serializers e viewsets DRF
5. Configurar conexão com Supabase
6. Implementar endpoint de validação automática (`POST /api/parcelas/{id}/validar/`)
7. Criar endpoint para upload de PDF e extração via Anthropic API

**Obs importante:** Filipe ainda vai enviar um PDF de BCI real para mapear os campos exatos do formulário — os campos atuais são baseados na NBR 14166 mas podem precisar de ajuste por município.
