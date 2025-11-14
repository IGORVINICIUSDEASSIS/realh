# 📊 Real H - Dashboard de Análise de Vendas

Sistema completo de análise de vendas com Streamlit, PPTX gerado e navegação otimizada para storytelling.

## 🎯 Características Principais

### 📊 Análise Completa
- **Dashboard**: Visão geral com KPIs principais
- **Comparativos**: Análise período a período
- **Insights**: Identificação de problemas (devoluções, etc)
- **Gráficos e Evolução**: Tendências temporais

### 🗺️ Navegação Inteligente
- **Nova Página: Mapa de Análise** → Navegação rápida para segmentações
- Guia de fluxo no Dashboard
- Buttons com st.switch_page() para navegação perfeita

### 📊 Segmentações
- **Por Linha de Produto**: Análise por linha de negócio
- **Por Produto**: Performance detalhada de SKUs
- **Por Vendedor**: Análise individual de desempenho
- **Por Região/Gerente**: Perspectiva geográfica

### 📄 Relatórios Profissionais
- **Opção A**: Geração automática de PPTX
- **Opção B**: Template customizado com placeholders
- Suporte para gráficos Plotly em apresentações
- Logo da empresa integrada
- Exportação de template padrão

### ⚙️ Configurações
- Gerenciamento de templates PPTX
- Upload de templates personalizados
- Documentação em português

## 📁 Estrutura de Páginas

```
├── app.py                                    (Home - Carregamento de dados)
└── pages/
    ├── 0_📊_Dashboard.py                    (Visão geral + Guia de fluxo)
    ├── 1_📈_Comparativos.py                 (Análise comparativa)
    ├── 2_💡_Insights.py                     (Problemas identificados)
    ├── 3_🗺️_Mapa_de_Análise.py              (Navegação rápida) ⭐ NOVO
    ├── 4_🏢_Análise_por_Linha.py
    ├── 5_📈_Gráficos_e_Evolução.py
    ├── 6_📦_Análise_de_Produtos.py
    ├── 7_👤_Análise_de_Vendedores.py
    ├── 8_🌎_Análise_por_Gerente_Regional.py
    ├── 9_📄_Relatório.py                    (Gerador PPTX)
    └── 10_⚙️_Configurações_Relatório.py     (Setup templates)

```

## 🎨 Jornada de Navegação (Storytelling)

```
📊 Dashboard             → "Como está o negócio?"
   ↓
📈 Comparativos          → "O que mudou?"
   ↓
💡 Insights              → "Qual é o problema?"
   ↓
🗺️ Mapa de Análise       → "Onde investigar?" [NOVO]
   ├─ 🏢 Por Linha
   ├─ 📦 Por Produto
   ├─ 👤 Por Vendedor
   └─ 🌎 Por Região
   ↓
📈 Gráficos/Evolução     → "Quando começou?"
   ↓
📄 Relatório             → "Vou comunicar"
   ↓
⚙️ Configurações         → "Personalizações"
```

**Score de Storytelling: 9.0/10** ⭐⭐⭐

## 🚀 Como Usar

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Rodar a Aplicação

```bash
streamlit run app.py
```

### 3. Carregar Dados

1. Na página inicial (app.py), carregue seus arquivos:
   - `vendas.xlsx` ou `vendas.csv`
   - `devolucoes.xlsx` ou `devolucoes.csv` (opcional)

2. Configure as colunas (mapeamento de campos)

### 4. Navegar

Use o menu lateral para:
- Ver o **Dashboard** (panorama geral)
- Ir para **Comparativos** (análise período)
- Analisar **Insights** (problemas encontrados)
- Usar **Mapa de Análise** para escolher segmentação
- Ou ir direto para a segmentação que precisa
- **Gerar Relatório** em PPTX profissional

## 📊 Funcionalidades Específicas

### 📈 Gráficos com Toggle

Todos os top 10 têm toggle entre gráfico e tabela:
- Clique em "Ver Gráfico" ou "Ver Tabela"
- Visualize os dados na forma que preferir
- Exporte dados facilmente

### 📄 Gerador de PPTX

**Opção A - Automática:**
- Cria PPTX do zero
- Insere gráficos Plotly
- Adiciona logo da empresa
- Pronto para enviar

**Opção B - Com Template:**
- Upload template customizado
- Substitui placeholders: `{{TITULO}}`, `{{PERIODO}}`, `{{METRICAS}}`, `{{GRAFICO}}`
- Converte gráficos para PNG
- Mantém design original

### ⚙️ Configurações

- Gerar template padrão
- Upload de templates personalizados
- Tutoriais em português
- Documentação de placeholders

## 📋 Requisitos

- Python 3.11+
- Streamlit
- Pandas
- Plotly
- python-pptx
- kaleido (para conversão de gráficos)

## 📝 Documentação

- `MELHORIAS_STORYTELLING.md` - Detalhes das melhorias implementadas
- Tutoriais em português nas páginas de configuração
- Guia interativo no Dashboard

## 🎯 Próximos Passos (Sugestões)

- [ ] Adicionar breadcrumb na sidebar
- [ ] Botão "Voltar" em cada segmentação
- [ ] Sugestões automáticas de próximo passo
- [ ] Tutorial interativo no primeiro acesso
- [ ] Analytics de navegação

## 📧 Suporte

Para dúvidas sobre navegação, consulte:
1. Guia de Fluxo no Dashboard (expander)
2. Mapa de Análise (página dedicada)
3. Dicas nos rodapés das páginas

---

**Versão:** 2.0 (Com Mapa de Análise)
**Último update:** Novembro 2025
**Status:** ✅ Pronto para Produção
