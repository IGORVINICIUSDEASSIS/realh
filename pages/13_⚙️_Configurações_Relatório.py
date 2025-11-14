import streamlit as st
import pandas as pd
from utils import gerar_relatorio_pptx, formatar_moeda, obter_periodo_mes_comercial
from utils_template import gerar_template_padrao, preencher_template_pptx
import os

st.set_page_config(page_title="⚙️ Configurações", layout="wide", initial_sidebar_state="expanded")
exibir_logo = True
if exibir_logo:
    from utils import exibir_logo
    exibir_logo()

st.title("⚙️ Configurações de Apresentações")

st.markdown("""
Aqui você pode personalizar como criar suas apresentações executivas:
- **Opção A**: Gerar do zero (automático e rápido)
- **Opção B**: Usar um template customizado (design profissional próprio)
""")

# ===== CRIAR TEMPLATE =====
st.header("1️⃣ Criar Template Customizado")

col1, col2 = st.columns([0.4, 0.6])

with col1:
    if st.button("📋 Gerar Template Base", use_container_width=True):
        try:
            gerar_template_padrao('template_relatorio.pptx')
            st.success("✅ Template criado com sucesso!")
            st.info("""
            **Próximos passos:**
            1. Abra o arquivo `template_relatorio.pptx` no PowerPoint
            2. Customize o design, cores, fonts conforme sua marca
            3. Mantenha os placeholders: {{TITULO}}, {{PERIODO}}, {{METRICAS}}, {{GRAFICO}}
            4. Salve como `template_relatorio_customizado.pptx`
            5. Use a Opção B ao gerar apresentação para preenchimento automático!
            """)
        except Exception as e:
            st.error(f"❌ Erro: {str(e)}")

with col2:
    st.info("""
    **Por que usar template?**
    
    ✅ Design consistente com marca
    ✅ Rápido (customiza 1x, usa infinitas vezes)
    ✅ Profissional (seu layout preservado)
    ✅ Dados atualizados automaticamente
    """)

# ===== EXEMPLOS DE PLACEHOLDERS =====
st.header("2️⃣ Placeholders Disponíveis")

st.markdown("""
Use estes placeholders no seu template do PowerPoint. O Python vai substituir automaticamente:

| Placeholder | Substituído por |
|---|---|
| `{{TITULO}}` | Título do relatório |
| `{{PERIODO}}` | Período selecionado |
| `{{METRICAS}}` | Lista de métricas principais |
| `{{GRAFICO}}` | Imagem dos gráficos |
| `{{NOME_GRAFICO}}` | Nome do gráfico |

**Exemplo de uso no PowerPoint:**
- Texto: "Relatório {{TITULO}} - {{PERIODO}}"
- Resultado: "Relatório Vendas Real H - Nov/2024"
""")

# ===== COMPARAÇÃO DAS OPÇÕES =====
st.header("3️⃣ Comparação de Opções")

col1, col2 = st.columns(2)

with col1:
    st.subheader("✅ Opção A: Gerar do Zero")
    st.markdown("""
    **Vantagens:**
    - ✅ Automático e rápido
    - ✅ Design consistente
    - ✅ Sem necessidade de customizar
    - ✅ Atualizar design = atualizar código
    
    **Desvantagens:**
    - ❌ Menos flexibilidade visual
    - ❌ Precisa de código para alterar design
    
    **Ideal para:**
    - Relatórios padronizados
    - Sistemas automatizados
    """)

with col2:
    st.subheader("📋 Opção B: Usar Template")
    st.markdown("""
    **Vantagens:**
    - ✅ Design 100% customizável
    - ✅ Sem conhecer código
    - ✅ Reutilizável várias vezes
    - ✅ Equipe não-técnica pode alterar
    
    **Desvantagens:**
    - ❌ Precisa customizar no PowerPoint
    - ❌ Manutenção do template
    
    **Ideal para:**
    - Design corporativo específico
    - Múltiplos relatórios
    - Equipes que usam PowerPoint
    """)

# ===== COMO USAR =====
st.header("4️⃣ Tutorial: Como Usar Template")

with st.expander("📚 Ver tutorial completo"):
    st.markdown("""
    ### Passo 1: Gerar Template
    1. Clique em "📋 Criar Template Padrão"
    2. Arquivo `template_relatorio.pptx` é criado
    
    ### Passo 2: Customizar no PowerPoint
    1. Abra `template_relatorio.pptx` no PowerPoint
    2. Altere cores, fonts, layout como quiser
    3. **Importante:** Mantenha os placeholders como `{{TITULO}}`, `{{PERIODO}}`, etc
    4. Salve como `template_relatorio_customizado.pptx`
    
    ### Passo 3: Usar na Página de Relatório
    1. Vá para "📄 Relatório"
    2. Selecione a opção "📋 Usar Template"
    3. Escolha seu arquivo customizado
    4. Gere o relatório!
    
    ### Dica: Onde colocar o template
    - Coloque na pasta raiz do projeto
    - Ou em `/workspaces/realh/template_relatorio_customizado.pptx`
    """)

# ===== INFORMAÇÕES TÉCNICAS =====
st.header("5️⃣ Informações Técnicas")

with st.expander("🔧 Ver detalhes técnicos"):
    st.markdown("""
    ### Placeholders em Diferentes Formatos
    
    **Texto:**
    ```
    {{TITULO}}
    {{PERIODO}}
    {{METRICAS}}
    ```
    
    **Imagem (Gráficos):**
    ```
    [{{GRAFICO}}]
    ```
    
    ### Limitações
    - Placeholders devem estar EXATAMENTE como escrito (com as chaves)
    - Um placeholder por célula de texto
    - Gráficos substituem o texto, não adicionam ao lado
    
    ### Formato de Saída
    - Sempre PPTX (PowerPoint 2007+)
    - Compatível com: PowerPoint, LibreOffice, Google Slides
    """)

st.divider()
st.info("💡 **Dica:** Use a Opção A para começar, depois migre para Opção B quando quiser mais controle visual!")
