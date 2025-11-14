import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
sys.path.append('/workspaces/realh')
from utils import formatar_moeda, obter_periodo_mes_comercial, exibir_logo, gerar_relatorio_pptx
from utils_template import preencher_template_pptx
import os

st.set_page_config(page_title="Relatório", page_icon="📄", layout="wide")

exibir_logo()

st.title("📊 Gerador de Apresentações Executivas")

st.markdown("""
Crie apresentações profissionais em PPTX para:
- 📊 Relatórios ao board executivo
- 💼 Briefings com time e liderança
- 👥 Compartilhamento com stakeholders
- 📋 Documentação de análises e decisões
""")

# Verificar se os dados foram carregados
if 'df_vendas' not in st.session_state:
    st.warning("⚠️ Por favor, carregue os dados na página inicial primeiro!")
    st.stop()

# Pegar dados do session_state
df_vendas = st.session_state['df_vendas']
df_vendas_original = st.session_state['df_vendas_original']
df_devolucoes = st.session_state.get('df_devolucoes', pd.DataFrame())
df_devolucoes_original = st.session_state.get('df_devolucoes_original', pd.DataFrame())
meses_comerciais_disponiveis = st.session_state.get('meses_comerciais_disponiveis', [])

st.markdown("---")

# ==============================
# ESCOLHER MODO DE GERAÇÃO
# ==============================
st.markdown("### 🎯 Modo de Geração")

col_modo1, col_modo2 = st.columns(2)

with col_modo1:
    modo_geracao = st.radio(
        "Escolha como criar sua apresentação:",
        options=["✅ Gerar do Zero (Automático)", "📋 Usar Template Customizado"],
        help="Opção A: Rápido e automático. Opção B: Totalmente customizado conforme seu design"
    )

if "Template" in modo_geracao:
    with col_modo2:
        st.info("""
        ℹ️ **Como usar:**
        1. Vá em ⚙️ Configurações
        2. Clique "Criar Template"
        3. Customize no PowerPoint
        4. Volte aqui e escolha o arquivo
        """)

st.markdown("---")

# ==============================
# CONFIGURAÇÃO DO RELATÓRIO
# ==============================
st.markdown("### ⚙️ Configuração do Relatório")

col_config1, col_config2 = st.columns(2)

with col_config1:
    st.markdown("#### 📅 Período")
    if meses_comerciais_disponiveis:
        mes_relatorio = st.selectbox(
            "Selecione o mês para o relatório:",
            meses_comerciais_disponiveis,
            help="Período que será incluído no relatório"
        )
    else:
        st.warning("Nenhum período disponível")
        st.stop()

with col_config2:
    st.markdown("#### 🎯 Seleção de Conteúdo")
    
    incluir_metricas = st.checkbox("✅ Incluir Métricas", value=True)
    incluir_graficos = st.checkbox("✅ Incluir Gráficos", value=True)
    incluir_top_clientes = st.checkbox("✅ Incluir Top Clientes", value=True)
    incluir_top_produtos = st.checkbox("✅ Incluir Top Produtos", value=True)
    incluir_top_vendedores = st.checkbox("✅ Incluir Top Vendedores", value=True)

st.markdown("---")

# ==============================
# FILTRAR DADOS DO PERÍODO
# ==============================
data_inicio, data_fim = obter_periodo_mes_comercial(mes_relatorio)

df_periodo = df_vendas_original[
    (df_vendas_original[st.session_state['col_data']] >= data_inicio) & 
    (df_vendas_original[st.session_state['col_data']] <= data_fim)
].copy()

if not df_devolucoes_original.empty:
    df_dev_periodo = df_devolucoes_original[
        (df_devolucoes_original[st.session_state['col_data']] >= data_inicio) & 
        (df_devolucoes_original[st.session_state['col_data']] <= data_fim)
    ].copy()
else:
    df_dev_periodo = pd.DataFrame()

st.markdown("### 📊 Pré-visualização do Relatório")

# ==============================
# CALCULAR MÉTRICAS
# ==============================
valor_total = df_periodo[st.session_state['col_valor']].sum()
clientes_unicos = df_periodo[st.session_state['col_codCliente']].nunique()
pedidos_unicos = df_periodo['Pedido_Unico'].nunique()
produtos_unicos = df_periodo[st.session_state['col_produto']].nunique()
vendedores_unicos = df_periodo[st.session_state['col_codVendedor']].nunique()
ticket_medio = valor_total / pedidos_unicos if pedidos_unicos > 0 else 0

if not df_dev_periodo.empty:
    valor_devolucoes = df_dev_periodo[st.session_state['col_valor']].sum()
    taxa_devolucao = (valor_devolucoes / valor_total * 100) if valor_total > 0 else 0
else:
    valor_devolucoes = 0
    taxa_devolucao = 0

valor_liquido = valor_total - valor_devolucoes

# Dict de métricas
metricas_dict = {
    "💰 Faturamento Total": formatar_moeda(valor_total),
    "💵 Faturamento Líquido": formatar_moeda(valor_liquido),
    "↩️ Devoluções": formatar_moeda(valor_devolucoes),
    "👥 Clientes": f"{clientes_unicos:,}",
    "📦 Pedidos": f"{pedidos_unicos:,}",
    "🎯 Ticket Médio": formatar_moeda(ticket_medio),
    "🛍️ Produtos": f"{produtos_unicos:,}",
    "🧑‍💼 Vendedores": f"{vendedores_unicos:,}",
}

# Mostrar pré-visualização
col_prev1, col_prev2, col_prev3, col_prev4 = st.columns(4)

col_prev1.metric("💰 Faturamento", formatar_moeda(valor_total))
col_prev2.metric("💵 Líquido", formatar_moeda(valor_liquido))
col_prev3.metric("↩️ Devoluções", f"{taxa_devolucao:.1f}%")
col_prev4.metric("👥 Clientes", f"{clientes_unicos:,}")

st.markdown("---")

# ==============================
# PREPARAR TOPS
# ==============================
tops_dict = {}

if incluir_top_clientes:
    top_clientes = df_periodo.groupby(st.session_state['col_cliente'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(10).reset_index()
    top_clientes.columns = ['Cliente', 'Valor']
    top_clientes['Valor'] = top_clientes['Valor'].apply(formatar_moeda)
    tops_dict["👥 Top 10 Clientes"] = top_clientes

if incluir_top_produtos:
    top_produtos = df_periodo.groupby(st.session_state['col_produto'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(10).reset_index()
    top_produtos.columns = ['Produto', 'Valor']
    top_produtos['Valor'] = top_produtos['Valor'].apply(formatar_moeda)
    tops_dict["🛍️ Top 10 Produtos"] = top_produtos

if incluir_top_vendedores:
    top_vendedores = df_periodo.groupby(st.session_state['col_vendedor'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(10).reset_index()
    top_vendedores.columns = ['Vendedor', 'Valor']
    top_vendedores['Valor'] = top_vendedores['Valor'].apply(formatar_moeda)
    tops_dict["🧑‍💼 Top 10 Vendedores"] = top_vendedores

# ==============================
# PREPARAR GRÁFICOS
# ==============================
graficos_dict = {}

if incluir_graficos:
    # Gráfico: Top Clientes
    if incluir_top_clientes:
        top_clientes_grafico = df_periodo.groupby(st.session_state['col_cliente'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(10)
        
        fig_clientes = go.Figure()
        fig_clientes.add_trace(go.Bar(
            y=top_clientes_grafico.index,
            x=top_clientes_grafico.values,
            orientation='h',
            marker_color='#00CC96',
            text=[formatar_moeda(x) for x in top_clientes_grafico.values],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>%{x}<extra></extra>'
        ))
        fig_clientes.update_layout(
            title="Top 10 Clientes por Faturamento",
            xaxis_title="Valor (R$)",
            yaxis_title="",
            height=600,
            margin=dict(l=250, r=100, t=50, b=50),
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False,
            font=dict(size=12)
        )
        graficos_dict["📊 Top 10 Clientes"] = fig_clientes
    
    # Gráfico: Top Produtos
    if incluir_top_produtos:
        top_produtos_grafico = df_periodo.groupby(st.session_state['col_produto'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(10)
        
        fig_produtos = go.Figure()
        fig_produtos.add_trace(go.Bar(
            y=top_produtos_grafico.index,
            x=top_produtos_grafico.values,
            orientation='h',
            marker_color='#636EFA',
            text=[formatar_moeda(x) for x in top_produtos_grafico.values],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>%{x}<extra></extra>'
        ))
        fig_produtos.update_layout(
            title="Top 10 Produtos por Faturamento",
            xaxis_title="Valor (R$)",
            yaxis_title="",
            height=600,
            margin=dict(l=250, r=100, t=50, b=50),
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False,
            font=dict(size=12)
        )
        graficos_dict["📊 Top 10 Produtos"] = fig_produtos
    
    # Gráfico: Top Vendedores
    if incluir_top_vendedores:
        top_vendedores_grafico = df_periodo.groupby(st.session_state['col_vendedor'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(10)
        
        fig_vendedores = go.Figure()
        fig_vendedores.add_trace(go.Bar(
            y=top_vendedores_grafico.index,
            x=top_vendedores_grafico.values,
            orientation='h',
            marker_color='#FFA15A',
            text=[formatar_moeda(x) for x in top_vendedores_grafico.values],
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>%{x}<extra></extra>'
        ))
        fig_vendedores.update_layout(
            title="Top 10 Vendedores por Faturamento",
            xaxis_title="Valor (R$)",
            yaxis_title="",
            height=600,
            margin=dict(l=250, r=100, t=50, b=50),
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False,
            font=dict(size=12)
        )
        graficos_dict["📊 Top 10 Vendedores"] = fig_vendedores

# ==============================
# GERAR RELATÓRIO
# ==============================
st.markdown("### 📥 Download do Relatório")

if "Gerar do Zero" in modo_geracao:
    # ===== OPÇÃO A: GERAR DO ZERO =====
    col_btn1, col_btn2 = st.columns([0.3, 0.7])

    with col_btn1:
        if st.button("🎯 Gerar Relatório PPTX", use_container_width=True, key="btn_zero"):
            with st.spinner("⏳ Gerando apresentação..."):
                try:
                    pptx_bytes = gerar_relatorio_pptx(
                        titulo="Relatório de Vendas - Real H",
                        periodo=mes_relatorio,
                        metricas_dict=metricas_dict if incluir_metricas else {},
                        tops_dict=tops_dict,
                        graficos_dict=graficos_dict if incluir_graficos else None
                    )
                    
                    st.success("✅ Relatório gerado com sucesso!")
                    
                    # Botão de download
                    st.download_button(
                        label="⬇️ Baixar Apresentação",
                        data=pptx_bytes,
                        file_name=f"Relatorio_Vendas_{mes_relatorio}.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"❌ Erro ao gerar relatório: {str(e)}")

    with col_btn2:
        st.info("💡 Clique no botão ao lado para gerar e baixar o relatório em PowerPoint!")

else:
    # ===== OPÇÃO B: USAR TEMPLATE =====
    st.info("📋 **Usando Template Customizado**")
    
    col_template1, col_template2 = st.columns(2)
    
    with col_template1:
        # Procurar templates disponíveis
        templates_disponiveis = []
        if os.path.exists('template_relatorio.pptx'):
            templates_disponiveis.append('template_relatorio.pptx')
        if os.path.exists('template_relatorio_customizado.pptx'):
            templates_disponiveis.append('template_relatorio_customizado.pptx')
        
        if templates_disponiveis:
            template_selecionado = st.selectbox(
                "Escolha o template:",
                templates_disponiveis,
                help="Templates disponíveis na pasta do projeto"
            )
        else:
            st.warning("❌ Nenhum template encontrado!")
            st.info("1. Vá em ⚙️ Configurações\n2. Clique 'Criar Template Padrão'\n3. Customize no PowerPoint\n4. Salve como 'template_relatorio_customizado.pptx'")
            st.stop()
    
    with col_template2:
        # Opção de upload
        template_upload = st.file_uploader(
            "Ou faça upload do seu template:",
            type="pptx",
            help="Envie um arquivo .pptx customizado"
        )
    
    col_btn1, col_btn2 = st.columns([0.3, 0.7])
    
    with col_btn1:
        if st.button("🎯 Gerar Relatório com Template", use_container_width=True, key="btn_template"):
            with st.spinner("⏳ Preenchendo template..."):
                try:
                    # Usar upload ou arquivo local
                    if template_upload:
                        import tempfile
                        with tempfile.NamedTemporaryFile(suffix='.pptx', delete=False) as tmp:
                            tmp.write(template_upload.read())
                            caminho_template = tmp.name
                    else:
                        caminho_template = template_selecionado
                    
                    # Preencher template
                    pptx_bytes = preencher_template_pptx(
                        caminho_template=caminho_template,
                        titulo="Relatório de Vendas - Real H",
                        periodo=mes_relatorio,
                        metricas_dict=metricas_dict if incluir_metricas else {},
                        graficos_dict=graficos_dict if incluir_graficos else None
                    )
                    
                    st.success("✅ Relatório gerado com sucesso!")
                    
                    # Botão de download
                    st.download_button(
                        label="⬇️ Baixar Apresentação",
                        data=pptx_bytes,
                        file_name=f"Relatorio_Vendas_{mes_relatorio}.pptx",
                        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"❌ Erro ao gerar relatório: {str(e)}")
                    import traceback
                    st.error(traceback.format_exc())
    
    with col_btn2:
        st.info("💡 Template será preenchido com os dados e cores serão mantidas!")

