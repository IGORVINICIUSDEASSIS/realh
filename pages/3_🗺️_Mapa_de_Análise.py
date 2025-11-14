import streamlit as st
import pandas as pd
import sys
sys.path.append('/workspaces/realh')
from utils import exibir_logo

st.set_page_config(page_title="Mapa de Análise", page_icon="🗺️", layout="wide")

exibir_logo()

st.title("🗺️ Mapa de Análise - Navegação Rápida")

st.markdown("""
Você quer **aprofundar a análise** sob um ângulo específico? 
Esta página ajuda você a navegar rapidamente para a segmentação que precisa!
""")

st.markdown("---")

# Verificar se os dados foram carregados
if 'df_vendas' not in st.session_state:
    st.warning("⚠️ Por favor, carregue os dados na página inicial primeiro!")
    st.stop()

# ==============================
# QUER APROFUNDAR A ANÁLISE?
# ==============================
st.markdown("### 🔍 Quer Aprofundar a Análise?")

st.markdown("""
Escolha por onde quer investigar e entender melhor a dinâmica do seu negócio:
""")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🏢 **Por Linha de Produto**")
    st.markdown("""
    Entenda a performance de cada linha de negócio.
    
    ✅ Ideal quando:
    - Uma linha tem performance diferente
    - Quer comparar dinâmica entre linhas
    - Precisa entender mix de portfólio
    """)
    if st.button("🔗 Ir para Análise por Linha", key="btn_linha"):
        st.switch_page("pages/4_🏢_Análise_por_Linha.py")

with col2:
    st.markdown("#### 📦 **Por Produto Específico**")
    st.markdown("""
    Analise em profundidade o desempenho de cada SKU.
    
    ✅ Ideal quando:
    - Um produto tem comportamento diferente
    - Quer entender dinâmica de produtos
    - Precisa de análise por item
    """)
    if st.button("🔗 Ir para Análise de Produtos", key="btn_produto"):
        st.switch_page("pages/6_📦_Análise_de_Produtos.py")

st.markdown("---")

col3, col4 = st.columns(2)

with col3:
    st.markdown("#### 👤 **Por Vendedor/Pessoa**")
    st.markdown("""
    Acompanhe a performance individual do seu time.
    
    ✅ Ideal quando:
    - Quer avaliar desempenho do time
    - Precisa identificar top performers
    - Necessita análise de qualidade de vendas
    """)
    if st.button("🔗 Ir para Análise de Vendedores", key="btn_vendedor"):
        st.switch_page("pages/7_👤_Análise_de_Vendedores.py")

with col4:
    st.markdown("#### 🌎 **Por Região/Gerente**")
    st.markdown("""
    Veja a performance por contexto geográfico e gestor.
    
    ✅ Ideal quando:
    - Uma região tem desempenho diferente
    - Quer comparar performance regional
    - Precisa de análise por gestor
    """)
    if st.button("🔗 Ir para Análise Regional", key="btn_regional"):
        st.switch_page("pages/8_🌎_Análise_por_Gerente_Regional.py")

st.markdown("---")

# ==============================
# PRECISA DE MAIS CONTEXTO?
# ==============================
st.markdown("### 📚 Precisa de Mais Contexto?")

col5, col6, col7 = st.columns(3)

with col5:
    st.markdown("#### 📊 **Voltar ao Dashboard**")
    st.markdown("Status atual dos processos")
    if st.button("🔗 Dashboard Principal", key="btn_dashboard"):
        st.switch_page("pages/0_📊_Dashboard.py")

with col6:
    st.markdown("#### 📈 **Ver Comparativos**")
    st.markdown("Comparação temporal")
    if st.button("🔗 Comparativos", key="btn_comparativo"):
        st.switch_page("pages/1_📈_Comparativos.py")

with col7:
    st.markdown("#### 💡 **Analisar Insights**")
    st.markdown("Oportunidades gerais de melhoria")
    if st.button("🔗 Insights", key="btn_insights"):
        st.switch_page("pages/2_💡_Insights.py")

st.markdown("---")

# ==============================
# DEVOLUÇÕES (se houver dados)
# ==============================
if not st.session_state.get('df_devolucoes', pd.DataFrame()).empty:
    st.markdown("### 💼 Análise de Devoluções")
    
    st.markdown("Entenda os padrões de devoluções em todas as categorias:")
    
    if st.button("🔗 Análise de Devoluções", key="btn_devolucoes"):
        st.switch_page("pages/3a_↩️_Análise_de_Devoluções.py")
    
    st.markdown("---")

# ==============================
# ANÁLISE TEMPORAL
# ==============================
st.markdown("### 📅 Análise de Tendências Temporais")

st.markdown("""
Veja como os indicadores evoluem ao longo do tempo:
- Séries históricas
- Padrões e sazonalidade
- Evolução de KPIs
""")

if st.button("🔗 Análise Temporal", key="btn_temporal"):
    st.switch_page("pages/5_📅_Análise_Temporal.py")

st.markdown("---")

# ==============================
# IDEIAS DE SOLUÇÕES
# ==============================
st.markdown("### 💡 Ideias de Soluções por Situação")

with st.expander("📋 Clique para expandir e ver sugestões de ações"):
    st.markdown("""
    
    #### 📉 Se você notou QUEDA em um indicador:
    
    **Investigação:**
    1. Vá para **Comparativos** → Compare o período atual com anterior
    2. Vá para **Gráficos/Evolução** → Veja quando começou a queda
    3. Use o **Mapa** → Isole por linha/produto/vendedor para encontrar a raiz
    
    **Possíveis Soluções:**
    - 🎯 **Por Linha**: Considere revisão de mix de produtos ou pricing da linha
    - 📦 **Por Produto**: Aumentar estoque? Melhorar embalagem? Reposicionar preço?
    - 👤 **Por Vendedor**: Capacitação, reorganização de rotas, revisão de cotas?
    - 🌎 **Por Região**: Investigar concorrência? Mudar gestor? Revisar modelo comercial?
    
    ---
    
    #### 📈 Se você notou CRESCIMENTO:
    
    **Aproveitar:**
    1. Identifique qual área está crescendo (linha, produto, vendedor, região)
    2. Entenda por quê está crescendo (produto novo? vendedor melhor? demanda?)
    3. Replique o sucesso em outras áreas
    
    **Possíveis Ações:**
    - 🎯 Aumentar investimento em canais que crescem
    - 📦 Expandir mix de produtos bem-sucedidos
    - 👤 Estudar práticas do vendedor/região de sucesso
    - 🌎 Usar como case de best practice para outras regiões
    
    ---
    
    #### ⏱️ Se você notou VOLATILIDADE (sobe e desce):
    
    **Investigação:**
    1. Vá para **Gráficos/Evolução** → Veja o padrão ao longo do tempo
    2. Procure por sazonalidade ou eventos
    3. Use **Mapa** → Entenda o que varia (produto? vendedor? região?)
    
    **Possíveis Soluções:**
    - 📅 Fazer previsão de demanda (sazonalidade)
    - 🎯 Ajustar cotas e expectativas para períodos sazonais
    - 📦 Manter estoque estratégico nos picos
    - 👤 Treinar time para períodos de alta demanda
    
    ---
    
    #### 🎯 Se você notou DESVIO EM RELAÇÃO AO ESPERADO:
    
    **Investigação:**
    1. Vá para **Insights** → Veja quais são as oportunidades sinalizadas
    2. Use **Mapa** → Isole a segmentação problemática
    3. Vá para **Gráficos** → Entenda se é tendência ou anomalia
    
    **Possíveis Soluções:**
    - 🔄 Revisar meta/forecast vs realidade
    - 📊 Ajustar modelo de previsão
    - 🎯 Implementar ações corretivas direcionadas
    - 👥 Comunicar mudança de expectativas ao time
    
    ---
    
    #### 💰 Se você notou PROBLEMA COM DEVOLUÇÕES:
    
    **Investigação:**
    1. Vá para **Insights** → Analise devoluções por categoria
    2. Use **Mapa** → Isole por produto/vendedor/linha para encontrar padrão
    3. Vá para **Gráficos** → Veja quando começou
    
    **Possíveis Soluções:**
    - 📦 Revisar qualidade do produto
    - 🚚 Melhorar logística e embalagem
    - 👤 Treinar vendedor (vendas inadequadas? vendas agressivas?)
    - 💬 Melhorar comunicação com cliente sobre especificações
    - 📞 Investigar se cliente recebe produto correto
    
    ---
    
    #### 🏆 Se você quer BENCHMARKING:
    
    **Investigação:**
    1. Vá para **Comparativos** → Compare diferentes períodos
    2. Use **Mapa** → Compare linhas/produtos/vendedores/regiões entre si
    3. Identifique o MELHOR e o PIOR
    
    **Possíveis Ações:**
    - 🎯 Usar melhor como referência de meta
    - 📚 Fazer análise de "por que aquele é melhor?"
    - 👥 Compartilhar práticas do melhor com os demais
    - 🎓 Treinar time com base nas melhores práticas
    
    """)

st.markdown("---")

# ==============================
# PRONTO PARA COMUNICAR?
# ==============================
st.markdown("### 📊 Pronto para Comunicar?")

col8, col9 = st.columns(2)

with col8:
    st.markdown("#### 📊 **Gerar Apresentação**")
    st.markdown("""
    Crie apresentações profissionais para:
    - Relatórios ao board
    - Briefings com time
    - Compartilhamento com stakeholders
    - Documentação de decisões
    """)
    if st.button("🔗 Gerar Apresentação", key="btn_relatorio"):
        st.switch_page("pages/9_📄_Relatório.py")

with col9:
    st.markdown("#### ⚙️ **Configurações**")
    st.markdown("""
    Personalize seus templates e veja:
    - Tutoriais de uso
    - Documentação de placeholders
    - Comparação de opções
    """)
    if st.button("🔗 Configurações", key="btn_config"):
        st.switch_page("pages/10_⚙️_Configurações_Relatório.py")

st.markdown("---")

# ==============================
# FLUXO VISUAL
# ==============================
st.markdown("### 🎬 Resumo do Fluxo de Análise")

st.markdown("""
```
┌──────────────────────────────────────────────────────────┐
│  1. Dashboard                                            │
│     "Como está o negócio? Qual é o status?"            │
│     ↓ (Identifiquei algo que precisa investigar)       │
├──────────────────────────────────────────────────────────┤
│  2. Comparativos                                         │
│     "Isso cresceu ou caiu? É melhora ou piora?"        │
│     ↓ (Entendi a mudança. Mas por quê?)                │
├──────────────────────────────────────────────────────────┤
│  3. Insights                                             │
│     "Onde estão as oportunidades? O que otimizar?"     │
│     ↓ (Achei! Preciso entender melhor essa área)       │
├──────────────────────────────────────────────────────────┤
│  4. 🗺️ Mapa de Análise                                    │
│     "Vou investigar por qual ângulo?"                  │
│     ↓ (Escolha: Linha? Produto? Vendedor? Região?)    │
├──────────────────────────────────────────────────────────┤
│  5. Segmentação Escolhida                               │
│     "Entendi o detalhe. E agora, qual é a ação?"      │
│     ↓ (Vejo ideias de solução acima!)                 │
├──────────────────────────────────────────────────────────┤
│  6. Gerar Apresentação                                  │
│     "Vou comunicar ao board/time"                      │
│     ↓ (Escolha: automática ou template)               │
└──────────────────────────────────────────────────────────┘
```
""")

st.markdown("---")

# ==============================
# DICAS
# ==============================
with st.expander("💡 **Pro Tips** - Clique para ver dicas avançadas"):
    st.markdown("""
    ### Dicas Para Usar Este Dashboard:
    
    **📊 Use o Dashboard como seu "monitor do negócio":**
    - Abra todos os dias para revisar KPIs
    - Veja tendências mesmo quando tudo está bem
    - Use como base para reuniões diárias
    
    **🔍 Investigação Estruturada:**
    - Sempre comece com a visão geral (Dashboard)
    - Depois vá para comparação temporal (Comparativos)
    - Depois procure oportunidades (Insights)
    - Por fim, segmente para encontrar raiz (Mapa)
    
    **📈 Monitoramento vs Reação:**
    - Idealmente, você está monitorando, não reagindo
    - Se estiver sempre reagindo, revise se as metas são realistas
    - Use dados históricos para fazer previsões
    
    **💬 Comunicação:**
    - Nunca leve só números, leve também a interpretação
    - Use apresentações para alinhar decisões
    - Mostre contexto (o que era, o que é, o que será)
    
    **🎯 Orientação por Dados:**
    - Leve dados para TODA decisão
    - Questione "por quê" até encontrar a raiz
    - A solução vem da compreensão da causa
    
    **🚀 Melhoria Contínua:**
    - Não é apenas reportar o problema
    - É monitorar, entender, agir e depois validar se funcionou
    - Use este dashboard para fechar o ciclo PDCA
    """)
