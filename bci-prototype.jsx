
import { useState } from "react";

const SECTIONS = ["Identificação", "Proprietário", "Terreno", "Construção", "Validação"];

const statusColor = {
  ok: "#22c55e",
  alerta: "#f59e0b",
  erro: "#ef4444",
  vazio: "#94a3b8",
};

const mockLotes = [
  { id: 1, x: 120, y: 80, w: 70, h: 50, inscricao: "01.02.003.0004-0", status: "erro" },
  { id: 2, x: 200, y: 80, w: 60, h: 50, inscricao: "01.02.003.0005-0", status: "ok" },
  { id: 3, x: 270, y: 80, w: 75, h: 50, inscricao: "01.02.003.0006-0", status: "alerta" },
  { id: 4, x: 120, y: 140, w: 70, h: 55, inscricao: "01.02.003.0007-0", status: "ok" },
  { id: 5, x: 200, y: 140, w: 60, h: 55, inscricao: "01.02.003.0008-0", status: "vazio" },
  { id: 6, x: 270, y: 140, w: 75, h: 55, inscricao: "01.02.003.0009-0", status: "alerta" },
  { id: 7, x: 120, y: 205, w: 70, h: 50, inscricao: "01.02.003.0010-0", status: "ok" },
  { id: 8, x: 200, y: 205, w: 135, h: 50, inscricao: "01.02.003.0011-0", status: "erro" },
];

const initialBCI = {
  // Identificação
  inscricao: "01.02.003.0004-0",
  distrito: "01",
  setor: "02",
  quadra: "003",
  lote: "0004",
  logradouro: "Rua das Acácias",
  numero: "123",
  complemento: "",
  bairro: "Centro",
  cep: "58000-000",
  // Proprietário
  proprietario: "João da Silva",
  cpf_cnpj: "123.456.789-00",
  endereco_prop: "",
  telefone: "",
  tipo_dominio: "pleno",
  // Terreno
  area_terreno: "300",
  frente: "15",
  fundo: "15",
  lado_dir: "20",
  lado_esq: "20",
  situacao: "meio_quadra",
  topografia: "plano",
  pedologia: "seco",
  nivelamento: "nivel",
  // Construção
  uso: "residencial_unifamiliar",
  tipo_construcao: "casa",
  padrao: "normal",
  estado: "bom",
  ano_construcao: "1998",
  area_construida: "180",
  num_pavimentos: "1",
  num_comodos: "6",
  possui_construcao: "sim",
};

const validationRules = [
  { campo: "inscricao", label: "Inscrição Cadastral", tipo: "obrigatorio" },
  { campo: "logradouro", label: "Logradouro", tipo: "obrigatorio" },
  { campo: "proprietario", label: "Proprietário", tipo: "obrigatorio" },
  { campo: "area_terreno", label: "Área do Terreno", tipo: "obrigatorio" },
  { campo: "frente", label: "Testada Frontal", tipo: "obrigatorio" },
  {
    campo: "area_construida_vs_terreno",
    label: "Área construída ≤ área terreno",
    tipo: "logica",
    check: (d) => !d.area_construida || parseFloat(d.area_construida) <= parseFloat(d.area_terreno || 0),
    mensagem: "Área construída maior que área do terreno",
  },
  {
    campo: "ano_construcao",
    label: "Ano de construção válido",
    tipo: "logica",
    check: (d) => !d.ano_construcao || (parseInt(d.ano_construcao) >= 1850 && parseInt(d.ano_construcao) <= 2025),
    mensagem: "Ano de construção fora do intervalo válido (1850–2025)",
  },
];

function runValidation(data) {
  const erros = [];
  const alertas = [];
  validationRules.forEach((rule) => {
    if (rule.tipo === "obrigatorio") {
      if (!data[rule.campo] || data[rule.campo].toString().trim() === "") {
        erros.push({ campo: rule.campo, label: rule.label, mensagem: `Campo obrigatório não preenchido` });
      }
    } else if (rule.tipo === "logica") {
      if (!rule.check(data)) {
        alertas.push({ campo: rule.campo, label: rule.label, mensagem: rule.mensagem });
      }
    }
  });
  return { erros, alertas };
}

const Field = ({ label, children, required, error }) => (
  <div style={{ marginBottom: 14 }}>
    <label style={{ display: "block", fontSize: 11, fontWeight: 700, letterSpacing: "0.07em", color: error ? "#ef4444" : "#64748b", textTransform: "uppercase", marginBottom: 5 }}>
      {label} {required && <span style={{ color: "#ef4444" }}>*</span>}
    </label>
    {children}
    {error && <p style={{ fontSize: 11, color: "#ef4444", marginTop: 3 }}>{error}</p>}
  </div>
);

const Input = ({ value, onChange, placeholder, error, type = "text" }) => (
  <input
    type={type}
    value={value}
    onChange={(e) => onChange(e.target.value)}
    placeholder={placeholder}
    style={{
      width: "100%", padding: "8px 10px", fontSize: 13,
      border: `1.5px solid ${error ? "#ef4444" : "#e2e8f0"}`,
      borderRadius: 6, background: "#f8fafc", color: "#1e293b",
      outline: "none", fontFamily: "inherit", boxSizing: "border-box",
      transition: "border-color 0.15s",
    }}
  />
);

const Select = ({ value, onChange, options, error }) => (
  <select
    value={value}
    onChange={(e) => onChange(e.target.value)}
    style={{
      width: "100%", padding: "8px 10px", fontSize: 13,
      border: `1.5px solid ${error ? "#ef4444" : "#e2e8f0"}`,
      borderRadius: 6, background: "#f8fafc", color: "#1e293b",
      outline: "none", fontFamily: "inherit", boxSizing: "border-box",
    }}
  >
    {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
  </select>
);

const Row = ({ children, cols = 2 }) => (
  <div style={{ display: "grid", gridTemplateColumns: `repeat(${cols}, 1fr)`, gap: 12 }}>
    {children}
  </div>
);

export default function App() {
  const [selected, setSelected] = useState(mockLotes[0]);
  const [section, setSection] = useState(0);
  const [data, setData] = useState(initialBCI);
  const [saved, setSaved] = useState(false);
  const [validated, setValidated] = useState(false);
  const [validation, setValidation] = useState(null);

  const set = (field) => (val) => {
    setData((d) => ({ ...d, [field]: val }));
    setSaved(false);
    setValidated(false);
  };

  const handleSave = () => {
    const result = runValidation(data);
    setValidation(result);
    setValidated(true);
    if (result.erros.length === 0) setSaved(true);
  };

  const getFieldError = (campo) => {
    if (!validated || !validation) return null;
    const e = validation.erros.find((e) => e.campo === campo);
    return e ? e.mensagem : null;
  };

  const overallStatus = !validated ? "vazio" : validation.erros.length > 0 ? "erro" : validation.alertas.length > 0 ? "alerta" : "ok";

  return (
    <div style={{ fontFamily: "'DM Sans', 'Segoe UI', sans-serif", display: "flex", height: "100vh", background: "#0f172a", color: "#1e293b" }}>
      
      {/* LEFT: MAP PANEL */}
      <div style={{ width: 400, display: "flex", flexDirection: "column", borderRight: "1px solid #1e293b" }}>
        {/* Header */}
        <div style={{ background: "#0f172a", padding: "18px 20px", borderBottom: "1px solid #1e3a5f" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{ width: 32, height: 32, borderRadius: 8, background: "linear-gradient(135deg, #0ea5e9, #6366f1)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <span style={{ fontSize: 16 }}>🗺️</span>
            </div>
            <div>
              <div style={{ fontSize: 14, fontWeight: 700, color: "#f1f5f9", letterSpacing: "-0.01em" }}>BzR CTM</div>
              <div style={{ fontSize: 10, color: "#64748b", letterSpacing: "0.05em", textTransform: "uppercase" }}>Cadastro Territorial Multifinalitário</div>
            </div>
          </div>
        </div>

        {/* Search */}
        <div style={{ padding: "12px 16px", background: "#0f172a", borderBottom: "1px solid #1e3a5f" }}>
          <input
            placeholder="🔍  Buscar por inscrição ou endereço..."
            style={{ width: "100%", padding: "8px 12px", background: "#1e293b", border: "1px solid #334155", borderRadius: 8, color: "#94a3b8", fontSize: 12, outline: "none", boxSizing: "border-box", fontFamily: "inherit" }}
          />
        </div>

        {/* Mock Map */}
        <div style={{ flex: 1, position: "relative", background: "#1a2744", overflow: "hidden" }}>
          {/* Grid lines */}
          <svg style={{ position: "absolute", inset: 0, width: "100%", height: "100%", opacity: 0.15 }}>
            {[...Array(10)].map((_, i) => (
              <line key={`h${i}`} x1="0" y1={i * 40} x2="400" y2={i * 40} stroke="#4a90d9" strokeWidth="0.5" />
            ))}
            {[...Array(10)].map((_, i) => (
              <line key={`v${i}`} x1={i * 40} y1="0" x2={i * 40} y2="400" stroke="#4a90d9" strokeWidth="0.5" />
            ))}
          </svg>

          {/* Roads */}
          <svg style={{ position: "absolute", inset: 0, width: "100%", height: "100%", opacity: 0.6 }}>
            <rect x="0" y="60" width="400" height="12" fill="#243554" />
            <rect x="0" y="128" width="400" height="10" fill="#243554" />
            <rect x="0" y="196" width="400" height="10" fill="#243554" />
            <rect x="0" y="258" width="400" height="12" fill="#243554" />
            <rect x="100" y="0" width="12" height="400" fill="#243554" />
            <rect x="350" y="0" width="12" height="400" fill="#243554" />
          </svg>

          {/* Road labels */}
          <svg style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}>
            <text x="200" y="69" textAnchor="middle" fill="#4a90d9" fontSize="9" fontFamily="DM Sans, sans-serif" opacity="0.8">RUA DAS ACÁCIAS</text>
            <text x="200" y="135" textAnchor="middle" fill="#4a90d9" fontSize="9" fontFamily="DM Sans, sans-serif" opacity="0.8">RUA DOS IPÊS</text>
            <text x="200" y="203" textAnchor="middle" fill="#4a90d9" fontSize="9" fontFamily="DM Sans, sans-serif" opacity="0.8">AV. CENTRAL</text>
          </svg>

          {/* Lots */}
          <svg style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}>
            {mockLotes.map((lote) => (
              <g key={lote.id} onClick={() => { setSelected(lote); setSection(0); setValidated(false); }}>
                <rect
                  x={lote.x} y={lote.y} width={lote.w} height={lote.h}
                  fill={statusColor[lote.status]}
                  fillOpacity={selected?.id === lote.id ? 0.85 : 0.35}
                  stroke={selected?.id === lote.id ? "#fff" : statusColor[lote.status]}
                  strokeWidth={selected?.id === lote.id ? 2.5 : 1}
                  rx="2"
                  style={{ cursor: "pointer", transition: "all 0.15s" }}
                />
                <text x={lote.x + lote.w / 2} y={lote.y + lote.h / 2 + 4} textAnchor="middle" fill="#fff" fontSize="9" fontFamily="DM Sans, sans-serif" opacity="0.9" style={{ pointerEvents: "none" }}>
                  {lote.id.toString().padStart(4, "0")}
                </text>
              </g>
            ))}
          </svg>

          {/* Compass */}
          <div style={{ position: "absolute", top: 12, right: 12, background: "#0f172a99", borderRadius: 8, padding: "6px 10px", fontSize: 18, color: "#94a3b8" }}>N ↑</div>

          {/* Scale */}
          <div style={{ position: "absolute", bottom: 12, left: 12, background: "#0f172a99", borderRadius: 6, padding: "4px 8px", fontSize: 10, color: "#64748b" }}>
            Escala 1:1000
          </div>
        </div>

        {/* Legend */}
        <div style={{ background: "#0f172a", padding: "10px 16px", borderTop: "1px solid #1e3a5f", display: "flex", gap: 14, flexWrap: "wrap" }}>
          {Object.entries({ ok: "Regular", alerta: "Alerta", erro: "Irregular", vazio: "Não vistoriado" }).map(([k, v]) => (
            <div key={k} style={{ display: "flex", alignItems: "center", gap: 5 }}>
              <div style={{ width: 10, height: 10, borderRadius: 2, background: statusColor[k] }} />
              <span style={{ fontSize: 10, color: "#64748b" }}>{v}</span>
            </div>
          ))}
        </div>
      </div>

      {/* RIGHT: FORM PANEL */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", background: "#f8fafc", overflow: "hidden" }}>
        
        {/* Form Header */}
        <div style={{ background: "#fff", padding: "14px 24px", borderBottom: "1px solid #e2e8f0", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div>
            <div style={{ fontSize: 11, color: "#94a3b8", textTransform: "uppercase", letterSpacing: "0.07em", marginBottom: 2 }}>Boletim de Cadastro Imobiliário — NBR 14166</div>
            <div style={{ fontSize: 16, fontWeight: 700, color: "#0f172a", display: "flex", alignItems: "center", gap: 8 }}>
              Lote {selected?.id.toString().padStart(4, "0")}
              <span style={{ fontSize: 12, fontWeight: 500, color: "#fff", background: statusColor[overallStatus], padding: "2px 10px", borderRadius: 999 }}>
                {overallStatus === "ok" ? "✓ Regular" : overallStatus === "alerta" ? "⚠ Alerta" : overallStatus === "erro" ? "✕ Irregular" : "— Não validado"}
              </span>
            </div>
            <div style={{ fontSize: 12, color: "#64748b" }}>{selected?.inscricao}</div>
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            <button onClick={() => setSection(4)} style={{ padding: "8px 16px", fontSize: 12, fontWeight: 600, borderRadius: 8, border: "1.5px solid #e2e8f0", background: "#fff", color: "#64748b", cursor: "pointer" }}>
              ✓ Validar
            </button>
            <button onClick={handleSave} style={{ padding: "8px 20px", fontSize: 12, fontWeight: 700, borderRadius: 8, border: "none", background: saved ? "#22c55e" : "linear-gradient(135deg, #0ea5e9, #6366f1)", color: "#fff", cursor: "pointer" }}>
              {saved ? "✓ Salvo" : "💾 Salvar BCI"}
            </button>
          </div>
        </div>

        {/* Section Tabs */}
        <div style={{ background: "#fff", padding: "0 24px", borderBottom: "1px solid #e2e8f0", display: "flex", gap: 0 }}>
          {SECTIONS.map((s, i) => (
            <button key={s} onClick={() => setSection(i)} style={{
              padding: "12px 18px", fontSize: 12, fontWeight: 600, border: "none", background: "none", cursor: "pointer",
              color: section === i ? "#0ea5e9" : "#94a3b8",
              borderBottom: section === i ? "2.5px solid #0ea5e9" : "2.5px solid transparent",
              transition: "all 0.15s",
            }}>
              {["🏠", "👤", "📐", "🏗️", "✅"][i]} {s}
            </button>
          ))}
        </div>

        {/* Form Body */}
        <div style={{ flex: 1, overflowY: "auto", padding: "24px" }}>

          {/* SECTION 0: Identificação */}
          {section === 0 && (
            <div>
              <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a", marginBottom: 18, paddingBottom: 8, borderBottom: "2px solid #e2e8f0" }}>
                🏠 Identificação do Imóvel
              </div>
              <Row cols={4}>
                <Field label="Distrito" required error={getFieldError("distrito")}>
                  <Input value={data.distrito} onChange={set("distrito")} placeholder="01" />
                </Field>
                <Field label="Setor" required>
                  <Input value={data.setor} onChange={set("setor")} placeholder="02" />
                </Field>
                <Field label="Quadra" required>
                  <Input value={data.quadra} onChange={set("quadra")} placeholder="003" />
                </Field>
                <Field label="Lote" required>
                  <Input value={data.lote} onChange={set("lote")} placeholder="0004" />
                </Field>
              </Row>
              <Field label="Inscrição Cadastral" required error={getFieldError("inscricao")}>
                <Input value={data.inscricao} onChange={set("inscricao")} placeholder="DD.SS.QQQ.LLLL-D" error={getFieldError("inscricao")} />
              </Field>
              <Row cols={3}>
                <div style={{ gridColumn: "span 2" }}>
                  <Field label="Logradouro" required error={getFieldError("logradouro")}>
                    <Input value={data.logradouro} onChange={set("logradouro")} placeholder="Nome da rua" error={getFieldError("logradouro")} />
                  </Field>
                </div>
                <Field label="Número">
                  <Input value={data.numero} onChange={set("numero")} placeholder="123" />
                </Field>
              </Row>
              <Row>
                <Field label="Complemento">
                  <Input value={data.complemento} onChange={set("complemento")} placeholder="Apto, Bloco..." />
                </Field>
                <Field label="Bairro">
                  <Input value={data.bairro} onChange={set("bairro")} placeholder="Nome do bairro" />
                </Field>
              </Row>
              <Field label="CEP">
                <Input value={data.cep} onChange={set("cep")} placeholder="00000-000" />
              </Field>
            </div>
          )}

          {/* SECTION 1: Proprietário */}
          {section === 1 && (
            <div>
              <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a", marginBottom: 18, paddingBottom: 8, borderBottom: "2px solid #e2e8f0" }}>
                👤 Proprietário / Possuidor
              </div>
              <Field label="Nome completo / Razão Social" required error={getFieldError("proprietario")}>
                <Input value={data.proprietario} onChange={set("proprietario")} placeholder="Nome do proprietário" error={getFieldError("proprietario")} />
              </Field>
              <Row>
                <Field label="CPF / CNPJ">
                  <Input value={data.cpf_cnpj} onChange={set("cpf_cnpj")} placeholder="000.000.000-00" />
                </Field>
                <Field label="Telefone">
                  <Input value={data.telefone} onChange={set("telefone")} placeholder="(00) 00000-0000" />
                </Field>
              </Row>
              <Field label="Endereço para correspondência">
                <Input value={data.endereco_prop} onChange={set("endereco_prop")} placeholder="Se diferente do imóvel" />
              </Field>
              <Field label="Tipo de Domínio">
                <Select value={data.tipo_dominio} onChange={set("tipo_dominio")} options={[
                  { value: "pleno", label: "Domínio Pleno" },
                  { value: "util", label: "Domínio Útil" },
                  { value: "direto", label: "Domínio Direto" },
                  { value: "posse", label: "Posse" },
                  { value: "usufrutuario", label: "Usufrutuário" },
                ]} />
              </Field>
            </div>
          )}

          {/* SECTION 2: Terreno */}
          {section === 2 && (
            <div>
              <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a", marginBottom: 18, paddingBottom: 8, borderBottom: "2px solid #e2e8f0" }}>
                📐 Dados do Terreno
              </div>
              <Row>
                <Field label="Área do Terreno (m²)" required error={getFieldError("area_terreno")}>
                  <Input value={data.area_terreno} onChange={set("area_terreno")} placeholder="0,00" error={getFieldError("area_terreno")} />
                </Field>
                <Field label="Testada Frontal (m)" required error={getFieldError("frente")}>
                  <Input value={data.frente} onChange={set("frente")} placeholder="0,00" error={getFieldError("frente")} />
                </Field>
              </Row>
              <Row cols={3}>
                <Field label="Fundo (m)">
                  <Input value={data.fundo} onChange={set("fundo")} placeholder="0,00" />
                </Field>
                <Field label="Lado Direito (m)">
                  <Input value={data.lado_dir} onChange={set("lado_dir")} placeholder="0,00" />
                </Field>
                <Field label="Lado Esquerdo (m)">
                  <Input value={data.lado_esq} onChange={set("lado_esq")} placeholder="0,00" />
                </Field>
              </Row>
              <Row cols={3}>
                <Field label="Situação na Quadra">
                  <Select value={data.situacao} onChange={set("situacao")} options={[
                    { value: "meio_quadra", label: "Meio de Quadra" },
                    { value: "esquina", label: "Esquina" },
                    { value: "encravado", label: "Encravado" },
                    { value: "vila", label: "Vila" },
                    { value: "gleba", label: "Gleba" },
                  ]} />
                </Field>
                <Field label="Topografia">
                  <Select value={data.topografia} onChange={set("topografia")} options={[
                    { value: "plano", label: "Plano" },
                    { value: "aclive", label: "Aclive" },
                    { value: "declive", label: "Declive" },
                    { value: "irregular", label: "Irregular" },
                  ]} />
                </Field>
                <Field label="Pedologia">
                  <Select value={data.pedologia} onChange={set("pedologia")} options={[
                    { value: "seco", label: "Seco" },
                    { value: "inundavel", label: "Inundável" },
                    { value: "alagado", label: "Alagado" },
                    { value: "pantanoso", label: "Pantanoso" },
                  ]} />
                </Field>
              </Row>
              <Field label="Nivelamento em relação ao leito da rua">
                <Select value={data.nivelamento} onChange={set("nivelamento")} options={[
                  { value: "nivel", label: "Ao Nível" },
                  { value: "acima", label: "Acima do Nível" },
                  { value: "abaixo", label: "Abaixo do Nível" },
                ]} />
              </Field>
            </div>
          )}

          {/* SECTION 3: Construção */}
          {section === 3 && (
            <div>
              <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a", marginBottom: 18, paddingBottom: 8, borderBottom: "2px solid #e2e8f0" }}>
                🏗️ Dados da Construção
              </div>
              <Field label="Possui Construção?">
                <Select value={data.possui_construcao} onChange={set("possui_construcao")} options={[
                  { value: "sim", label: "Sim" },
                  { value: "nao", label: "Não (Terreno vago)" },
                ]} />
              </Field>
              {data.possui_construcao === "sim" && (
                <>
                  <Row>
                    <Field label="Uso">
                      <Select value={data.uso} onChange={set("uso")} options={[
                        { value: "residencial_unifamiliar", label: "Residencial Unifamiliar" },
                        { value: "residencial_multifamiliar", label: "Residencial Multifamiliar" },
                        { value: "comercial", label: "Comercial" },
                        { value: "industrial", label: "Industrial" },
                        { value: "servicos", label: "Serviços" },
                        { value: "misto", label: "Misto" },
                        { value: "institucional", label: "Institucional" },
                      ]} />
                    </Field>
                    <Field label="Tipo de Construção">
                      <Select value={data.tipo_construcao} onChange={set("tipo_construcao")} options={[
                        { value: "casa", label: "Casa" },
                        { value: "apartamento", label: "Apartamento" },
                        { value: "sala_comercial", label: "Sala Comercial" },
                        { value: "loja", label: "Loja" },
                        { value: "galpon", label: "Galpão" },
                        { value: "barracao", label: "Barracão" },
                      ]} />
                    </Field>
                  </Row>
                  <Row cols={3}>
                    <Field label="Padrão Construtivo">
                      <Select value={data.padrao} onChange={set("padrao")} options={[
                        { value: "popular", label: "Popular" },
                        { value: "simples", label: "Simples" },
                        { value: "normal", label: "Normal" },
                        { value: "bom", label: "Bom" },
                        { value: "otimo", label: "Ótimo" },
                        { value: "luxo", label: "Luxo" },
                      ]} />
                    </Field>
                    <Field label="Estado de Conservação">
                      <Select value={data.estado} onChange={set("estado")} options={[
                        { value: "otimo", label: "Ótimo" },
                        { value: "bom", label: "Bom" },
                        { value: "regular", label: "Regular" },
                        { value: "precario", label: "Precário" },
                        { value: "ruina", label: "Ruína" },
                      ]} />
                    </Field>
                    <Field label="Ano de Construção">
                      <Input value={data.ano_construcao} onChange={set("ano_construcao")} placeholder="AAAA" />
                    </Field>
                  </Row>
                  <Row cols={3}>
                    <Field label="Área Construída (m²)">
                      <Input value={data.area_construida} onChange={set("area_construida")} placeholder="0,00" />
                    </Field>
                    <Field label="Nº Pavimentos">
                      <Input value={data.num_pavimentos} onChange={set("num_pavimentos")} placeholder="1" />
                    </Field>
                    <Field label="Nº Cômodos">
                      <Input value={data.num_comodos} onChange={set("num_comodos")} placeholder="0" />
                    </Field>
                  </Row>
                </>
              )}
            </div>
          )}

          {/* SECTION 4: Validação */}
          {section === 4 && (
            <div>
              <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a", marginBottom: 18, paddingBottom: 8, borderBottom: "2px solid #e2e8f0" }}>
                ✅ Validação do BCI — NBR 14166
              </div>

              {!validated ? (
                <div style={{ textAlign: "center", padding: "40px 20px" }}>
                  <div style={{ fontSize: 48, marginBottom: 12 }}>🔍</div>
                  <div style={{ fontSize: 14, color: "#64748b", marginBottom: 20 }}>Clique em "Validar" para verificar a consistência dos dados preenchidos</div>
                  <button onClick={handleSave} style={{ padding: "12px 32px", fontSize: 13, fontWeight: 700, borderRadius: 10, border: "none", background: "linear-gradient(135deg, #0ea5e9, #6366f1)", color: "#fff", cursor: "pointer" }}>
                    🔍 Executar Validação
                  </button>
                </div>
              ) : (
                <div>
                  {/* Summary */}
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginBottom: 20 }}>
                    {[
                      { label: "Erros", count: validation.erros.length, color: "#ef4444", bg: "#fef2f2", icon: "✕" },
                      { label: "Alertas", count: validation.alertas.length, color: "#f59e0b", bg: "#fffbeb", icon: "⚠" },
                      { label: "Status", count: validation.erros.length === 0 ? "OK" : "Pendente", color: validation.erros.length === 0 ? "#22c55e" : "#ef4444", bg: validation.erros.length === 0 ? "#f0fdf4" : "#fef2f2", icon: validation.erros.length === 0 ? "✓" : "✕" },
                    ].map((s) => (
                      <div key={s.label} style={{ background: s.bg, border: `1px solid ${s.color}30`, borderRadius: 10, padding: "16px", textAlign: "center" }}>
                        <div style={{ fontSize: 24, fontWeight: 800, color: s.color }}>{s.icon} {s.count}</div>
                        <div style={{ fontSize: 11, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.06em" }}>{s.label}</div>
                      </div>
                    ))}
                  </div>

                  {/* Erros */}
                  {validation.erros.length > 0 && (
                    <div style={{ marginBottom: 16 }}>
                      <div style={{ fontSize: 12, fontWeight: 700, color: "#ef4444", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 8 }}>Erros ({validation.erros.length})</div>
                      {validation.erros.map((e, i) => (
                        <div key={i} style={{ background: "#fef2f2", border: "1px solid #fecaca", borderRadius: 8, padding: "10px 14px", marginBottom: 6, display: "flex", gap: 10, alignItems: "center" }}>
                          <span style={{ fontSize: 16 }}>✕</span>
                          <div>
                            <div style={{ fontSize: 12, fontWeight: 600, color: "#dc2626" }}>{e.label}</div>
                            <div style={{ fontSize: 11, color: "#b91c1c" }}>{e.mensagem}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Alertas */}
                  {validation.alertas.length > 0 && (
                    <div style={{ marginBottom: 16 }}>
                      <div style={{ fontSize: 12, fontWeight: 700, color: "#f59e0b", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: 8 }}>Alertas ({validation.alertas.length})</div>
                      {validation.alertas.map((a, i) => (
                        <div key={i} style={{ background: "#fffbeb", border: "1px solid #fde68a", borderRadius: 8, padding: "10px 14px", marginBottom: 6, display: "flex", gap: 10, alignItems: "center" }}>
                          <span style={{ fontSize: 16 }}>⚠</span>
                          <div>
                            <div style={{ fontSize: 12, fontWeight: 600, color: "#d97706" }}>{a.label}</div>
                            <div style={{ fontSize: 11, color: "#92400e" }}>{a.mensagem}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {validation.erros.length === 0 && validation.alertas.length === 0 && (
                    <div style={{ background: "#f0fdf4", border: "1px solid #bbf7d0", borderRadius: 10, padding: "24px", textAlign: "center" }}>
                      <div style={{ fontSize: 36, marginBottom: 8 }}>✅</div>
                      <div style={{ fontSize: 14, fontWeight: 600, color: "#16a34a" }}>BCI validado com sucesso!</div>
                      <div style={{ fontSize: 12, color: "#15803d" }}>Todos os campos obrigatórios foram preenchidos e os dados são consistentes.</div>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={{ background: "#fff", padding: "10px 24px", borderTop: "1px solid #e2e8f0", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span style={{ fontSize: 11, color: "#94a3b8" }}>BzR CTM • NBR 14166 • {new Date().toLocaleDateString("pt-BR")}</span>
          <div style={{ display: "flex", gap: 8 }}>
            {section > 0 && (
              <button onClick={() => setSection(s => s - 1)} style={{ padding: "6px 14px", fontSize: 11, fontWeight: 600, borderRadius: 6, border: "1.5px solid #e2e8f0", background: "#fff", color: "#64748b", cursor: "pointer" }}>
                ← Anterior
              </button>
            )}
            {section < SECTIONS.length - 1 && (
              <button onClick={() => setSection(s => s + 1)} style={{ padding: "6px 14px", fontSize: 11, fontWeight: 700, borderRadius: 6, border: "none", background: "#0ea5e9", color: "#fff", cursor: "pointer" }}>
                Próximo →
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
