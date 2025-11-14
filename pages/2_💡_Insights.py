import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
sys.path.append('/workspaces/realh')
from utils import formatar_moeda, exibir_logo, exibir_top_com_alternancia

st.set_page_config(page_title="Insights", page_icon="💡", layout="wide")

exibir_logo()

st.title("💡 Insights - Análise Narrativa e Oportunidades")

st.markdown("""
Análise profunda com insights acionáveis e narrativa clara sobre o estado do negócio.
Este é o lugar para entender **quem merece atenção**, **o que está funcionando** e **por onde melhorar**.
""")

# Verificar se os dados foram carregados
if 'df_vendas' not in st.session_state:
    st.warning("⚠️ Por favor, carregue os dados na página inicial primeiro!")
    st.stop()

# Pegar dados do session_state
df_vendas = st.session_state['df_vendas']
df_devolucoes = st.session_state.get('df_devolucoes', pd.DataFrame())

st.markdown("---")

# ==============================
# MÉTRICAS PRINCIPAIS
# ==============================
st.markdown("### 📊 Visão Geral de Vendas")

valor_total = df_vendas[st.session_state['col_valor']].sum()
clientes_unicos = df_vendas[st.session_state['col_codCliente']].nunique()
produtos_unicos = df_vendas[st.session_state['col_produto']].nunique()
pedidos_totais = df_vendas['Pedido_Unico'].nunique()
vendedores_unicos = df_vendas[st.session_state['col_codVendedor']].nunique()
ticket_medio = valor_total / pedidos_totais if pedidos_totais > 0 else 0
ticket_por_cliente = valor_total / clientes_unicos if clientes_unicos > 0 else 0

col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("💰 Faturamento Total", formatar_moeda(valor_total))
col2.metric("🎯 Ticket Médio (Pedido)", formatar_moeda(ticket_medio))
col3.metric("👥 Clientes Únicos", f"{clientes_unicos:,}")
col4.metric("📦 Produtos Distintos", f"{produtos_unicos:,}")
col5.metric("🧑‍💼 Vendedores", f"{vendedores_unicos:,}")

st.markdown("---")

# ==============================
# ANÁLISE 1: CLIENTES - QUEM MERECE CUIDADO?
# ==============================
st.markdown("### 👥 Análise de Clientes - Quem Merece Atenção?")

vendas_por_cliente = df_vendas.groupby(st.session_state['col_codCliente'])[st.session_state['col_valor']].sum().reset_index()
vendas_por_cliente.columns = ['CodCliente', 'Vendas']
vendas_por_cliente = vendas_por_cliente.sort_values('Vendas', ascending=False)

# Adicionar nome do cliente
cliente_map = df_vendas[[st.session_state['col_codCliente'], st.session_state['col_cliente']]].drop_duplicates()
vendas_por_cliente = vendas_por_cliente.merge(cliente_map, left_on='CodCliente', right_on=st.session_state['col_codCliente'], how='left')

# Análise de devoluções por cliente
if not df_devolucoes.empty:
    dev_por_cliente = df_devolucoes.groupby(st.session_state['col_codCliente'])[st.session_state['col_valor']].sum().reset_index()
    dev_por_cliente.columns = ['CodCliente', 'Devolucoes']
    vendas_por_cliente = vendas_por_cliente.merge(dev_por_cliente, left_on='CodCliente', right_on='CodCliente', how='left').fillna(0)
    vendas_por_cliente['Taxa_Devolucao'] = (vendas_por_cliente['Devolucoes'] / vendas_por_cliente['Vendas'] * 100).round(2)
    vendas_por_cliente['Liquido'] = vendas_por_cliente['Vendas'] - vendas_por_cliente['Devolucoes']
else:
    vendas_por_cliente['Devolucoes'] = 0
    vendas_por_cliente['Taxa_Devolucao'] = 0
    vendas_por_cliente['Liquido'] = vendas_por_cliente['Vendas']

# Contagem de pedidos por cliente
pedidos_por_cliente = df_vendas.groupby(st.session_state['col_codCliente'])['Pedido_Unico'].nunique().reset_index()
pedidos_por_cliente.columns = ['CodCliente', 'Pedidos']
vendas_por_cliente = vendas_por_cliente.merge(pedidos_por_cliente, left_on='CodCliente', right_on='CodCliente', how='left')

# ===== INSIGHTS NARRATIVOS =====
st.markdown("#### 🎯 Análise Detalhada:")

# Tabbed insights
tab1, tab2, tab3, tab4 = st.tabs(["⚠️ Clientes em Risco", "📈 Clientes Estratégicos", "💪 Bons Clientes", "📊 Ranking Completo"])

with tab1:
    st.markdown("**Clientes que precisam de CUIDADO especial:**")
    
    # Critério 1: Alta taxa de devolução
    clientes_alto_dev = vendas_por_cliente[vendas_por_cliente['Taxa_Devolucao'] > 20].sort_values('Taxa_Devolucao', ascending=False)
    if not clientes_alto_dev.empty:
        st.warning("🔴 **Alta Taxa de Devolução (>20%)**")
        for idx, row in clientes_alto_dev.head(5).iterrows():
            col_narrativa1, col_narrativa2 = st.columns([3, 1])
            with col_narrativa1:
                st.markdown(f"""
                **{row[st.session_state['col_cliente']]}**
                - Vendas: {formatar_moeda(row['Vendas'])} | Devolvido: {formatar_moeda(row['Devolucoes'])} | Líquido: {formatar_moeda(row['Liquido'])}
                - Taxa de Devolução: **{row['Taxa_Devolucao']:.1f}%** ⚠️
                - Ação: Verificar qualidade do produto, processo de armazenamento ou especificações inadequadas
                """)
            with col_narrativa2:
                st.metric("Taxa %", f"{row['Taxa_Devolucao']:.1f}%")
    
    # Critério 2: Ticket muito baixo com muitos pedidos (cliente com baixa rentabilidade)
    vendas_por_cliente['Ticket_Cliente'] = vendas_por_cliente['Vendas'] / vendas_por_cliente['Pedidos']
    clientes_low_value = vendas_por_cliente[vendas_por_cliente['Ticket_Cliente'] < 500].sort_values('Pedidos', ascending=False)
    if not clientes_low_value.empty and len(clientes_low_value) > 0:
        st.warning("🟡 **Baixa Rentabilidade (Ticket < R$500)**")
        for idx, row in clientes_low_value.head(3).iterrows():
            st.markdown(f"""
            **{row[st.session_state['col_cliente']]}**
            - Fez {int(row['Pedidos'])} pedidos, mas ticket médio de apenas {formatar_moeda(row['Ticket_Cliente'])}
            - Total: {formatar_moeda(row['Vendas'])} com {int(row['Pedidos'])} transações
            - Ação: Aumentar ticket médio ou renegociar escala de compra
            """)

with tab2:
    st.markdown("**Clientes que DEVEM ser cultivados - São os pilares do negócio:**")
    
    clientes_top = vendas_por_cliente.head(10)
    concentracao_top3 = clientes_top.head(3)['Vendas'].sum() / valor_total * 100
    concentracao_top10 = clientes_top['Vendas'].sum() / valor_total * 100
    
    st.info(f"""
    📊 **Concentração de Receita:**
    - Top 3 clientes: **{concentracao_top3:.1f}%** da receita
    - Top 10 clientes: **{concentracao_top10:.1f}%** da receita
    
    🎯 **Recomendação:** Esses clientes são críticos. Manter relacionamento forte e oferecê-los novos produtos/serviços.
    """)
    
    for idx, row in clientes_top.iterrows():
        col_top1, col_top2, col_top3 = st.columns([2, 1, 1])
        with col_top1:
            st.markdown(f"**{idx+1}º. {row[st.session_state['col_cliente']]}**")
            st.markdown(f"- Vendas: {formatar_moeda(row['Vendas'])}")
            st.markdown(f"- Pedidos: {int(row['Pedidos'])} | Ticket: {formatar_moeda(row['Ticket_Cliente'])}")
        with col_top2:
            st.metric("% do Total", f"{row['Vendas']/valor_total*100:.1f}%")
        with col_top3:
            if row['Taxa_Devolucao'] > 0:
                st.metric("Devol %", f"{row['Taxa_Devolucao']:.1f}%")

with tab3:
    st.markdown("**Clientes com performance NORMAL - Potencial de crescimento:**")
    
    clientes_medio = vendas_por_cliente[(vendas_por_cliente['Taxa_Devolucao'] <= 10) & 
                                        (vendas_por_cliente['Vendas'] > 0) & 
                                        (~vendas_por_cliente[st.session_state['col_cliente']].isin(clientes_top[st.session_state['col_cliente']]))].head(10)
    
    if not clientes_medio.empty:
        st.success("✅ Clientes com baixa devolução que podem crescer:")
        for idx, row in clientes_medio.iterrows():
            st.markdown(f"""
            **{row[st.session_state['col_cliente']]}**
            - Vendas: {formatar_moeda(row['Vendas'])} | Pedidos: {int(row['Pedidos'])} | Taxa Dev: {row['Taxa_Devolucao']:.1f}%
            - Potencial: Aumentar frequência ou ticket médio
            """)

with tab4:
    st.markdown("**Ranking Completo de Clientes:**")
    ranking_display = vendas_por_cliente[[st.session_state['col_cliente'], 'Vendas', 'Pedidos', 'Ticket_Cliente', 'Devolucoes', 'Taxa_Devolucao', 'Liquido']].copy()
    ranking_display['Vendas'] = ranking_display['Vendas'].apply(formatar_moeda)
    ranking_display['Ticket_Cliente'] = ranking_display['Ticket_Cliente'].apply(formatar_moeda)
    ranking_display['Devolucoes'] = ranking_display['Devolucoes'].apply(formatar_moeda)
    ranking_display['Liquido'] = ranking_display['Liquido'].apply(formatar_moeda)
    ranking_display['Taxa_Devolucao'] = ranking_display['Taxa_Devolucao'].apply(lambda x: f"{x:.1f}%")
    ranking_display['Pedidos'] = ranking_display['Pedidos'].astype(int)
    
    ranking_display.columns = ['Cliente', 'Vendas', 'Pedidos', 'Ticket Médio', 'Devoluções', 'Taxa Dev %', 'Líquido']
    st.dataframe(ranking_display.head(20), use_container_width=True)

st.markdown("---")

# ==============================
# ANÁLISE 2: PRODUTOS - QUEM ESTÁ FUNCIONANDO?
# ==============================
st.markdown("### 📦 Análise de Produtos - O Que Está Funcionando?")

vendas_por_produto = df_vendas.groupby(st.session_state['col_produto'])[st.session_state['col_valor']].sum().reset_index()
vendas_por_produto.columns = ['Produto', 'Vendas']
vendas_por_produto = vendas_por_produto.sort_values('Vendas', ascending=False)

# Análise de devoluções por produto
if not df_devolucoes.empty:
    dev_por_produto = df_devolucoes.groupby(st.session_state['col_produto'])[st.session_state['col_valor']].sum().reset_index()
    dev_por_produto.columns = ['Produto', 'Devolucoes']
    vendas_por_produto = vendas_por_produto.merge(dev_por_produto, on='Produto', how='left').fillna(0)
    vendas_por_produto['Taxa_Devolucao'] = (vendas_por_produto['Devolucoes'] / vendas_por_produto['Vendas'] * 100).round(2)
    vendas_por_produto['Liquido'] = vendas_por_produto['Vendas'] - vendas_por_produto['Devolucoes']
else:
    vendas_por_produto['Devolucoes'] = 0
    vendas_por_produto['Taxa_Devolucao'] = 0
    vendas_por_produto['Liquido'] = vendas_por_produto['Vendas']

# Contagem de vendas por produto
vendas_count_por_produto = df_vendas.groupby(st.session_state['col_produto']).size().reset_index(name='Quantidade_Itens')
vendas_por_produto = vendas_por_produto.merge(vendas_count_por_produto, on='Produto', how='left')

tab_prod1, tab_prod2, tab_prod3 = st.tabs(["🏆 Estrelas", "⚠️ Problemas", "📊 Ranking"])

with tab_prod1:
    st.markdown("**Produtos que BRILHAM - Alto desempenho e baixa devolução:**")
    
    produtos_bons = vendas_por_produto[(vendas_por_produto['Taxa_Devolucao'] < 5) & 
                                        (vendas_por_produto['Vendas'] > vendas_por_produto['Vendas'].quantile(0.5))].head(5)
    
    if not produtos_bons.empty:
        for idx, row in produtos_bons.iterrows():
            col_prod1, col_prod2 = st.columns([3, 1])
            with col_prod1:
                st.success(f"""
                **{row['Produto']}** ✨
                - Vendas: {formatar_moeda(row['Vendas'])} | {int(row['Quantidade_Itens'])} unidades vendidas
                - Taxa Devolução: {row['Taxa_Devolucao']:.1f}% (excelente!)
                - Líquido: {formatar_moeda(row['Liquido'])}
                """)
            with col_prod2:
                st.metric("Desempenho", "⭐⭐⭐")

with tab_prod2:
    st.markdown("**Produtos COM PROBLEMAS - Precisam de atenção imediata:**")
    
    produtos_ruins = vendas_por_produto[vendas_por_produto['Taxa_Devolucao'] > 15].sort_values('Taxa_Devolucao', ascending=False)
    
    if not produtos_ruins.empty:
        st.error(f"⚠️ {len(produtos_ruins)} produto(s) com taxa de devolução > 15%")
        for idx, row in produtos_ruins.iterrows():
            st.error(f"""
            **{row['Produto']}** 🔴
            - Vendas: {formatar_moeda(row['Vendas'])} | Devolvidas: {formatar_moeda(row['Devolucoes'])} | Taxa: **{row['Taxa_Devolucao']:.1f}%**
            - Ação Urgente: Investigar motivos das devoluções (qualidade? armazenamento? especificação?)
            """)
    else:
        st.success("✅ Nenhum produto com alta taxa de devolução! Parabéns!")

with tab_prod3:
    st.markdown("**Ranking de Produtos:**")
    ranking_prod = vendas_por_produto[['Produto', 'Vendas', 'Quantidade_Itens', 'Devolucoes', 'Taxa_Devolucao', 'Liquido']].copy()
    ranking_prod['Vendas'] = ranking_prod['Vendas'].apply(formatar_moeda)
    ranking_prod['Devolucoes'] = ranking_prod['Devolucoes'].apply(formatar_moeda)
    ranking_prod['Liquido'] = ranking_prod['Liquido'].apply(formatar_moeda)
    ranking_prod['Quantidade_Itens'] = ranking_prod['Quantidade_Itens'].astype(int)
    ranking_prod['Taxa_Devolucao'] = ranking_prod['Taxa_Devolucao'].apply(lambda x: f"{x:.1f}%")
    
    ranking_prod.columns = ['Produto', 'Vendas', 'Unidades', 'Devoluções', 'Taxa Dev %', 'Líquido']
    st.dataframe(ranking_prod.head(15), use_container_width=True)

st.markdown("---")

# ==============================
# ANÁLISE 3: VENDEDORES - QUEM ESTÁ PERFORMANDO?
# ==============================
st.markdown("### 🧑‍💼 Análise de Vendedores - Desempenho Individual")

vendas_por_vendedor = df_vendas.groupby(st.session_state['col_codVendedor'])[st.session_state['col_valor']].sum().reset_index()
vendas_por_vendedor.columns = ['CodVendedor', 'Vendas']
vendas_por_vendedor = vendas_por_vendedor.sort_values('Vendas', ascending=False)

# Adicionar nome do vendedor
vendedor_map = df_vendas[[st.session_state['col_codVendedor'], st.session_state['col_vendedor']]].drop_duplicates()
vendas_por_vendedor = vendas_por_vendedor.merge(vendedor_map, left_on='CodVendedor', right_on=st.session_state['col_codVendedor'], how='left')

# Análise de devoluções por vendedor
if not df_devolucoes.empty:
    dev_por_vendedor = df_devolucoes.groupby(st.session_state['col_codVendedor'])[st.session_state['col_valor']].sum().reset_index()
    dev_por_vendedor.columns = ['CodVendedor', 'Devolucoes']
    vendas_por_vendedor = vendas_por_vendedor.merge(dev_por_vendedor, left_on='CodVendedor', right_on='CodVendedor', how='left').fillna(0)
    vendas_por_vendedor['Taxa_Devolucao'] = (vendas_por_vendedor['Devolucoes'] / vendas_por_vendedor['Vendas'] * 100).round(2)
else:
    vendas_por_vendedor['Devolucoes'] = 0
    vendas_por_vendedor['Taxa_Devolucao'] = 0

# Clientes por vendedor
clientes_por_vendedor = df_vendas.groupby(st.session_state['col_codVendedor'])[st.session_state['col_codCliente']].nunique().reset_index()
clientes_por_vendedor.columns = ['CodVendedor', 'Clientes_Unicos']
vendas_por_vendedor = vendas_por_vendedor.merge(clientes_por_vendedor, left_on='CodVendedor', right_on='CodVendedor', how='left')

st.markdown("#### 📊 Comparativo de Performance:")

col_vend1, col_vend2 = st.columns(2)

with col_vend1:
    st.markdown("**Top Vendedores (Receita):**")
    top_vend = vendas_por_vendedor.head(5)
    for idx, row in top_vend.iterrows():
        st.markdown(f"""
        {idx+1}º. **{row[st.session_state['col_vendedor']]}**
        - Vendas: {formatar_moeda(row['Vendas'])}
        - Clientes: {int(row['Clientes_Unicos'])} | Taxa Dev: {row['Taxa_Devolucao']:.1f}%
        """)

with col_vend2:
    st.markdown("**Vendedores com Melhor Taxa (Menor Devolução):**")
    vendedores_com_devol = vendas_por_vendedor[vendas_por_vendedor['Devolucoes'] > 0].sort_values('Taxa_Devolucao')
    if not vendedores_com_devol.empty:
        for idx, row in vendedores_com_devol.head(5).iterrows():
            st.markdown(f"""
            **{row[st.session_state['col_vendedor']]}**
            - Taxa Devolução: {row['Taxa_Devolucao']:.1f}%
            - Vendas: {formatar_moeda(row['Vendas'])} | Dev: {formatar_moeda(row['Devolucoes'])}
            """)

# Gráfico de comparação
fig_vend = go.Figure()

fig_vend.add_trace(go.Bar(
    x=vendas_por_vendedor[st.session_state['col_vendedor']],
    y=vendas_por_vendedor['Vendas'],
    name='Vendas',
    marker_color='#00CC96'
))

fig_vend.update_layout(
    title="Vendas por Vendedor",
    xaxis_title="Vendedor",
    yaxis_title="Valor (R$)",
    height=400
)

st.plotly_chart(fig_vend, use_container_width=True)

st.markdown("---")

# ==============================
# PONTOS POSITIVOS E NEGATIVOS (RESUMO FINAL)
# ==============================
st.markdown("### 🎯 Resumo Executivo - Pontos Positivos e Negativos")

col_pos, col_neg = st.columns(2)

with col_pos:
    st.success("### ✅ Pontos Positivos")
    
    pontos_pos = []
    
    # Diversificação
    if clientes_unicos > 50:
        pontos_pos.append(f"👥 Boa base de clientes ({clientes_unicos})")
    
    # Produtos
    if produtos_unicos > 20:
        pontos_pos.append(f"📦 Bom mix de produtos ({produtos_unicos})")
    
    # Taxa média de devolução baixa
    taxa_media_dev = df_devolucoes[st.session_state['col_valor']].sum() / valor_total * 100 if not df_devolucoes.empty else 0
    if taxa_media_dev < 10:
        pontos_pos.append(f"🎯 Taxa de devolução controlada ({taxa_media_dev:.1f}%)")
    
    # Ticket adequado
    if ticket_medio > 1000:
        pontos_pos.append(f"💰 Ticket médio saudável ({formatar_moeda(ticket_medio)})")
    
    if len(pontos_pos) == 0:
        pontos_pos.append("🔄 Continuar monitorando métricas")
    
    for ponto in pontos_pos:
        st.markdown(f"- {ponto}")

with col_neg:
    st.error("### ❌ Pontos Negativos & Atenções")
    
    pontos_neg = []
    
    # Concentração
    top1_percent = vendas_por_cliente.iloc[0]['Vendas'] / valor_total * 100
    if top1_percent > 30:
        pontos_neg.append(f"⚠️ Alto risco: {top1_percent:.1f}% da receita em 1 cliente")
    
    # Produtos com problemas
    produtos_ruins = vendas_por_produto[vendas_por_produto['Taxa_Devolucao'] > 15]
    if not produtos_ruins.empty:
        pontos_neg.append(f"🔴 {len(produtos_ruins)} produto(s) com alta devolução")
    
    # Taxa de devolução
    if taxa_media_dev > 15:
        pontos_neg.append(f"⚠️ Taxa de devolução elevada ({taxa_media_dev:.1f}%)")
    
    # Ticket baixo
    if ticket_medio < 500:
        pontos_neg.append(f"💭 Ticket médio baixo ({formatar_moeda(ticket_medio)})")
    
    if len(pontos_neg) == 0:
        pontos_neg.append("✅ Sem problemas críticos identificados")
    
    for ponto in pontos_neg:
        st.markdown(f"- {ponto}")

st.markdown("---")

# ==============================
# PRÓXIMOS PASSOS
# ==============================
st.markdown("### 🎬 Próximos Passos Recomendados")

with st.expander("💡 Ações Recomendadas", expanded=False):
    st.markdown("""
    1. **Proteger Relacionamentos Críticos** - Top clientes merecem atenção 1-on-1
    2. **Investigar Devoluções** - Vá para **↩️ Análise de Devoluções** se taxa > 10%
    3. **Análise Temporal** - Vá para **📅 Análise Temporal** para ver tendências
    4. **Segmentação** - Use **🗺️ Mapa de Análise** para entender por linha/produto/região
    5. **Qualidade** - Se muitas devoluções, verificar especificações e processos
    """)
