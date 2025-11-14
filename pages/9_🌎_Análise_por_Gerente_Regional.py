import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
sys.path.append('/workspaces/realh')
from utils import (obter_periodo_mes_comercial, exibir_logo, ordenar_mes_comercial, safe_strftime, formatar_moeda, exibir_top_com_alternancia)

st.set_page_config(page_title="Análise por Gerente Regional", page_icon="🌎", layout="wide")

exibir_logo()

st.title("🌎 Análise por Gerente Regional")

# Verificar se os dados foram carregados
if 'df_vendas' not in st.session_state:
    st.warning("⚠️ Por favor, carregue os dados na página inicial primeiro!")
    st.stop()

# Verificar se coluna Gerente Regional está configurada
col_gerente_regional = st.session_state.get('col_gerente_regional', 'Nenhuma')
if col_gerente_regional == "Nenhuma" or col_gerente_regional not in st.session_state['df_vendas'].columns:
    st.warning("⚠️ Configure a coluna 'Ger. Regional' na página inicial para visualizar esta análise.")
    st.stop()

# Pegar dados do session_state
df_vendas = st.session_state['df_vendas']
df_vendas_original = st.session_state['df_vendas_original']
df_devolucoes = st.session_state.get('df_devolucoes', pd.DataFrame())
df_devolucoes_original = st.session_state.get('df_devolucoes_original', pd.DataFrame())
meses_comerciais_disponiveis = st.session_state.get('meses_comerciais_disponiveis', [])

col_quantidade = st.session_state.get('col_quantidade', 'Nenhuma')
col_toneladas = st.session_state.get('col_toneladas', 'Nenhuma')

# Colunas de hierarquia
col_diretor = st.session_state.get('col_diretor', 'Nenhuma')
col_gerente = st.session_state.get('col_gerente', 'Nenhuma')
col_supervisor = st.session_state.get('col_supervisor', 'Nenhuma')
col_coordenador = st.session_state.get('col_coordenador', 'Nenhuma')
col_consultor = st.session_state.get('col_consultor', 'Nenhuma')
col_vendedor_leaf = st.session_state.get('col_vendedor_leaf', 'Nenhuma')

# ==============================
# FILTRO DE MÊS COMERCIAL NA SIDEBAR
# ==============================
st.sidebar.markdown("### 📅 Filtro de Período")

if meses_comerciais_disponiveis:
    filtro_mes_opcoes = ['Todos os Meses'] + list(meses_comerciais_disponiveis)
    mes_selecionado = st.sidebar.selectbox(
        "Selecione o Mês Comercial:",
        filtro_mes_opcoes,
        help="Mês comercial vai do dia 16 ao dia 15 do mês seguinte"
    )
    
    # Aplicar filtro de mês (sobre os dados já filtrados pelos filtros globais)
    if mes_selecionado != 'Todos os Meses':
        data_inicio, data_fim = obter_periodo_mes_comercial(mes_selecionado)
        df_vendas = df_vendas[
            (df_vendas[st.session_state['col_data']] >= data_inicio) & 
            (df_vendas[st.session_state['col_data']] <= data_fim)
        ].copy()
        
        if not df_devolucoes.empty:
            df_devolucoes = df_devolucoes[
                (df_devolucoes[st.session_state['col_data']] >= data_inicio) & 
                (df_devolucoes[st.session_state['col_data']] <= data_fim)
            ].copy()
        
        st.sidebar.info(f"📅 {safe_strftime(data_inicio)} a {safe_strftime(data_fim)}")
    else:
        st.sidebar.info("📅 Exibindo todos os períodos")

# ==============================
# PROCESSAR DADOS POR GERENTE REGIONAL
# ==============================
vendas_por_gerente = df_vendas.groupby(col_gerente_regional)[st.session_state['col_valor']].sum().sort_values(ascending=False)

if not df_devolucoes.empty and col_gerente_regional in df_devolucoes.columns:
    devolucoes_por_gerente = df_devolucoes.groupby(col_gerente_regional)[st.session_state['col_valor']].sum()
else:
    devolucoes_por_gerente = pd.Series(dtype=float)

# Calcular quantidade e toneladas por gerente
quantidade_por_gerente = pd.Series(dtype=float)
toneladas_por_gerente = pd.Series(dtype=float)

if col_quantidade != 'Nenhuma' and col_quantidade in df_vendas.columns:
    quantidade_por_gerente = df_vendas.groupby(col_gerente_regional)[col_quantidade].sum()

if col_toneladas != 'Nenhuma' and col_toneladas in df_vendas.columns:
    toneladas_por_gerente = df_vendas.groupby(col_gerente_regional)[col_toneladas].sum()

df_gerentes_analise = pd.DataFrame({
    'Vendas': vendas_por_gerente,
    'Devoluções': devolucoes_por_gerente,
    'Quantidade': quantidade_por_gerente,
    'Toneladas': toneladas_por_gerente
}).fillna(0)

df_gerentes_analise['Líquido'] = df_gerentes_analise['Vendas'] - df_gerentes_analise['Devoluções']
df_gerentes_analise['Taxa Dev. (%)'] = (df_gerentes_analise['Devoluções'] / df_gerentes_analise['Vendas'] * 100).fillna(0)
df_gerentes_analise = df_gerentes_analise.sort_values('Vendas', ascending=False)

# ==============================
# ABAS DE ANÁLISE
# ==============================
tab_visao_geral, tab_detalhes, tab_hierarquia, tab_evolucao, tab_comparativo = st.tabs(["📊 Visão Geral", "🔍 Detalhes do Gerente", "🌳 Hierarquia", "📈 Evolução", "⚖️ Comparativo"])

# ==============================
# ABA: VISÃO GERAL
# ==============================
with tab_visao_geral:
    st.markdown("### 📊 Resumo Geral por Gerente Regional")
    
    # KPIs gerais
    col1, col2, col3, col4, col5 = st.columns(5)
    
    col1.metric("👥 Total de Gerentes", len(df_gerentes_analise))
    col2.metric("💰 Faturamento Total", formatar_moeda(df_gerentes_analise['Vendas'].sum()))
    col3.metric("↩️ Devoluções Total", formatar_moeda(df_gerentes_analise['Devoluções'].sum()))
    col4.metric("💵 Líquido Total", formatar_moeda(df_gerentes_analise['Líquido'].sum()))
    
    taxa_dev_media = (df_gerentes_analise['Devoluções'].sum() / df_gerentes_analise['Vendas'].sum() * 100) if df_gerentes_analise['Vendas'].sum() > 0 else 0
    col5.metric("📉 Taxa Dev. Média", f"{taxa_dev_media:.1f}%")
    
    st.markdown("---")
    
    # Top Gerentes
    col_top1, col_top2 = st.columns(2)
    
    with col_top1:
        top_10_vendas = df_gerentes_analise.nlargest(10, 'Vendas')[['Vendas', 'Quantidade', 'Toneladas']].reset_index()
        top_10_vendas.columns = ['Gerente', 'Faturamento', 'Quantidade', 'Toneladas']
        top_10_vendas['Faturamento'] = top_10_vendas['Faturamento'].apply(formatar_moeda)
        top_10_vendas_display = top_10_vendas[['Gerente', 'Faturamento']]
        exibir_top_com_alternancia(top_10_vendas_display, "🏆 Top Gerentes por Faturamento", "gerentes_top_vendas", tipo_grafico='bar')
    
    with col_top2:
        top_10_dev = df_gerentes_analise[df_gerentes_analise['Devoluções'] > 0].nlargest(10, 'Taxa Dev. (%)')[['Devoluções', 'Taxa Dev. (%)']].reset_index()
        if len(top_10_dev) > 0:
            top_10_dev.columns = ['Gerente', 'Devoluções', 'Taxa (%)']
            top_10_dev['Devoluções'] = top_10_dev['Devoluções'].apply(formatar_moeda)
            top_10_dev['Taxa (%)'] = top_10_dev['Taxa (%)'].apply(lambda x: f"{x:.1f}%")
            exibir_top_com_alternancia(top_10_dev, "⚠️ Gerentes com Devolução", "gerentes_top_dev", tipo_grafico='bar')
        else:
            st.info("Nenhuma devolução registrada")
    
    st.markdown("---")
    
    # Gráfico de distribuição
    st.markdown("#### 📊 Distribuição de Vendas por Gerente Regional")
    
    fig_dist = go.Figure()
    
    fig_dist.add_trace(go.Bar(
        x=df_gerentes_analise.index,
        y=df_gerentes_analise['Vendas'],
        name='Vendas',
        marker_color='#00CC96',
        text=df_gerentes_analise['Vendas'].apply(lambda x: formatar_moeda(x)),
        textposition='outside'
    ))
    
    fig_dist.update_layout(
        title="Faturamento por Gerente Regional",
        xaxis_title="Gerente Regional",
        yaxis_title="Vendas (R$)",
        height=500,
        showlegend=False
    )
    
    st.plotly_chart(fig_dist, use_container_width=True)

# ==============================
# ABA: DETALHES DO GERENTE
# ==============================
with tab_detalhes:
    st.markdown("### 🔍 Análise Detalhada por Gerente Regional")
    
    # Seletor de gerente
    gerente_selecionado = st.selectbox("Selecione um gerente regional:", df_gerentes_analise.index.tolist())
    
    if gerente_selecionado:
        df_gerente_sel = df_vendas[df_vendas[col_gerente_regional] == gerente_selecionado]
        row_gerente = df_gerentes_analise.loc[gerente_selecionado]
        
        # KPIs do gerente
        st.markdown(f"#### 🌎 {gerente_selecionado}")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        col1.metric("💰 Vendas", formatar_moeda(row_gerente['Vendas']))
        col2.metric("↩️ Devoluções", formatar_moeda(row_gerente['Devoluções']))
        col3.metric("💵 Líquido", formatar_moeda(row_gerente['Líquido']))
        col4.metric("📉 Taxa Dev.", f"{row_gerente['Taxa Dev. (%)']:.1f}%")
        
        participacao = (row_gerente['Vendas'] / vendas_por_gerente.sum() * 100) if vendas_por_gerente.sum() > 0 else 0
        col5.metric("📊 Part. Total", f"{participacao:.2f}%")
        
        st.markdown("---")
        
        # Métricas da equipe
        st.markdown("#### 👥 Métricas da Equipe")
        
        col_a, col_b, col_c, col_d = st.columns(4)
        
        col_a.metric("📦 Pedidos", df_gerente_sel['Pedido_Unico'].nunique())
        col_b.metric("👥 Clientes", df_gerente_sel[st.session_state['col_codCliente']].nunique())
        col_c.metric("🛍️ Produtos", df_gerente_sel[st.session_state['col_produto']].nunique())
        
        # Contar vendedores da equipe
        num_vendedores = df_gerente_sel[st.session_state['col_vendedor']].nunique()
        col_d.metric("👤 Vendedores", num_vendedores)
        
        # Quantidade e Toneladas
        if col_quantidade != 'Nenhuma' and col_quantidade in df_gerente_sel.columns:
            col_a.metric("📦 Quantidade", f"{row_gerente['Quantidade']:,.0f} un")
        
        if col_toneladas != 'Nenhuma' and col_toneladas in df_gerente_sel.columns:
            col_b.metric("⚖️ Toneladas", f"{row_gerente['Toneladas']:,.2f} Tn")
        
        st.markdown("---")
        
        # Top 5 da equipe
        col_top1, col_top2 = st.columns(2)
        
        with col_top1:
            st.markdown("##### 👤 Top 5 Vendedores da Equipe")
            top_vendedores = df_gerente_sel.groupby(st.session_state['col_vendedor'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(5)
            for idx, (vendedor, valor) in enumerate(top_vendedores.items(), 1):
                st.write(f"{idx}. **{vendedor}**: {formatar_moeda(valor)}")
        
        with col_top2:
            st.markdown("##### 👥 Top 5 Clientes")
            top_clientes = df_gerente_sel.groupby(st.session_state['col_cliente'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(5)
            for idx, (cliente, valor) in enumerate(top_clientes.items(), 1):
                st.write(f"{idx}. **{cliente}**: {formatar_moeda(valor)}")
        
        st.markdown("---")
        
        # Top 5 Produtos
        col_prod1, col_prod2 = st.columns(2)
        
        with col_prod1:
            st.markdown("##### 🛍️ Top 5 Produtos por Valor")
            top_produtos = df_gerente_sel.groupby(st.session_state['col_produto'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(5)
            for idx, (produto, valor) in enumerate(top_produtos.items(), 1):
                st.write(f"{idx}. **{produto}**: {formatar_moeda(valor)}")
        
        with col_prod2:
            if col_quantidade != 'Nenhuma' and col_quantidade in df_gerente_sel.columns:
                st.markdown("##### 📦 Top 5 Produtos por Quantidade")
                top_qtde = df_gerente_sel.groupby(st.session_state['col_produto'])[col_quantidade].sum().sort_values(ascending=False).head(5)
                for idx, (produto, qtde) in enumerate(top_qtde.items(), 1):
                    st.write(f"{idx}. **{produto}**: {qtde:,.0f} un")

# ==============================
# ABA: HIERARQUIA
# ==============================
with tab_hierarquia:
    st.markdown("### 🌳 Estrutura Hierárquica")
    
    # Seletor de gerente para hierarquia
    gerente_hierarquia = st.selectbox("Selecione um gerente regional:", df_gerentes_analise.index.tolist(), key="gerente_hierarquia")
    
    if gerente_hierarquia:
        df_gerente_hier = df_vendas[df_vendas[col_gerente_regional] == gerente_hierarquia]
        
        st.markdown(f"#### 🌎 Estrutura de {gerente_hierarquia}")
        
        # Mostrar níveis hierárquicos disponíveis abaixo do gerente regional
        niveis_disponiveis = []
        
        if col_supervisor != 'Nenhuma' and col_supervisor in df_gerente_hier.columns:
            niveis_disponiveis.append(('Supervisor', col_supervisor))
        
        if col_coordenador != 'Nenhuma' and col_coordenador in df_gerente_hier.columns:
            niveis_disponiveis.append(('Coordenador', col_coordenador))
        
        if col_consultor != 'Nenhuma' and col_consultor in df_gerente_hier.columns:
            niveis_disponiveis.append(('Consultor', col_consultor))
        
        if col_vendedor_leaf != 'Nenhuma' and col_vendedor_leaf in df_gerente_hier.columns:
            niveis_disponiveis.append(('Vendedor', col_vendedor_leaf))
        else:
            # Se não tiver vendedor_leaf, usar col_vendedor padrão
            niveis_disponiveis.append(('Vendedor', st.session_state['col_vendedor']))
        
        # Criar tabs para cada nível hierárquico
        if len(niveis_disponiveis) > 0:
            tab_names = [nivel[0] for nivel in niveis_disponiveis]
            tabs_hierarquia = st.tabs([f"👥 {nome}" for nome in tab_names])
            
            for idx, (nivel_nome, nivel_coluna) in enumerate(niveis_disponiveis):
                with tabs_hierarquia[idx]:
                    st.markdown(f"#### 📊 Performance por {nivel_nome}")
                    
                    # Análise por nível
                    vendas_nivel = df_gerente_hier.groupby(nivel_coluna)[st.session_state['col_valor']].sum().sort_values(ascending=False)
                    
                    # Top performers do nível
                    st.markdown(f"##### 🏆 Top 10 {nivel_nome}s")
                    top_nivel = vendas_nivel.head(10)
                    
                    for pos, (nome, valor) in enumerate(top_nivel.items(), 1):
                        # Calcular métricas adicionais
                        df_pessoa = df_gerente_hier[df_gerente_hier[nivel_coluna] == nome]
                        clientes = df_pessoa[st.session_state['col_codCliente']].nunique()
                        pedidos = df_pessoa['Pedido_Unico'].nunique()
                        
                        col_rank1, col_rank2, col_rank3, col_rank4 = st.columns([3, 2, 1, 1])
                        with col_rank1:
                            st.write(f"**{pos}. {nome}**")
                        with col_rank2:
                            st.write(f"💰 {formatar_moeda(valor)}")
                        with col_rank3:
                            st.write(f"👥 {clientes} clientes")
                        with col_rank4:
                            st.write(f"📦 {pedidos} pedidos")
                    
                    st.markdown("---")
                    
                    # Gráfico de distribuição do nível
                    fig_nivel = go.Figure()
                    
                    df_top_20 = vendas_nivel.head(20)
                    
                    fig_nivel.add_trace(go.Bar(
                        x=df_top_20.index,
                        y=df_top_20.values,
                        marker_color='#636EFA',
                        text=[formatar_moeda(x) for x in df_top_20.values],
                        textposition='outside'
                    ))
                    
                    fig_nivel.update_layout(
                        title=f"Top 20 {nivel_nome}s - {gerente_hierarquia}",
                        xaxis_title=nivel_nome,
                        yaxis_title="Vendas (R$)",
                        height=500
                    )
                    
                    st.plotly_chart(fig_nivel, use_container_width=True)
        else:
            st.info("⚠️ Configure os níveis hierárquicos na página inicial para visualizar a estrutura.")

# ==============================
# ABA: EVOLUÇÃO
# ==============================
with tab_evolucao:
    st.markdown("### 📈 Evolução Temporal")
    
    # Seletor de gerente para evolução
    gerente_evolucao = st.selectbox("Selecione um gerente regional:", df_gerentes_analise.index.tolist(), key="gerente_evolucao")
    
    if gerente_evolucao:
        df_gerente_evolucao = df_vendas_original[df_vendas_original[col_gerente_regional] == gerente_evolucao]
        
        # Gráfico de Evolução de Vendas
        st.markdown("#### 💰 Evolução do Valor de Vendas")
        vendas_por_mes = df_gerente_evolucao.groupby('Mes_Comercial')[st.session_state['col_valor']].sum().reset_index()
        vendas_por_mes['Ordem'] = vendas_por_mes['Mes_Comercial'].apply(ordenar_mes_comercial)
        vendas_por_mes = vendas_por_mes.sort_values('Ordem')
        
        fig_vendas = go.Figure()
        fig_vendas.add_trace(go.Scatter(
            x=vendas_por_mes['Mes_Comercial'],
            y=vendas_por_mes[st.session_state['col_valor']],
            mode='lines+markers',
            name='Vendas',
            line=dict(color='#00CC96', width=3),
            marker=dict(size=10),
            fill='tozeroy',
            fillcolor='rgba(0, 204, 150, 0.1)'
        ))
        
        fig_vendas.update_layout(
            title=f"Evolução de Vendas - {gerente_evolucao}",
            xaxis_title="Mês Comercial",
            yaxis_title="Valor (R$)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig_vendas, use_container_width=True)
        
        # Gráfico de Evolução de Quantidade e Toneladas
        col_ev1, col_ev2 = st.columns(2)
        
        with col_ev1:
            if col_quantidade != 'Nenhuma' and col_quantidade in df_gerente_evolucao.columns:
                st.markdown("#### 📦 Evolução da Quantidade")
                qtde_por_mes = df_gerente_evolucao.groupby('Mes_Comercial')[col_quantidade].sum().reset_index()
                qtde_por_mes['Ordem'] = qtde_por_mes['Mes_Comercial'].apply(ordenar_mes_comercial)
                qtde_por_mes = qtde_por_mes.sort_values('Ordem')
                
                fig_qtde = go.Figure()
                fig_qtde.add_trace(go.Scatter(
                    x=qtde_por_mes['Mes_Comercial'],
                    y=qtde_por_mes[col_quantidade],
                    mode='lines+markers',
                    line=dict(color='#636EFA', width=2),
                    marker=dict(size=8),
                    fill='tozeroy',
                    fillcolor='rgba(99, 110, 250, 0.1)'
                ))
                
                fig_qtde.update_layout(
                    title="Quantidade",
                    xaxis_title="Mês Comercial",
                    yaxis_title="Quantidade (un)",
                    height=300
                )
                
                st.plotly_chart(fig_qtde, use_container_width=True)
        
        with col_ev2:
            if col_toneladas != 'Nenhuma' and col_toneladas in df_gerente_evolucao.columns:
                st.markdown("#### ⚖️ Evolução das Toneladas")
                ton_por_mes = df_gerente_evolucao.groupby('Mes_Comercial')[col_toneladas].sum().reset_index()
                ton_por_mes['Ordem'] = ton_por_mes['Mes_Comercial'].apply(ordenar_mes_comercial)
                ton_por_mes = ton_por_mes.sort_values('Ordem')
                
                fig_ton = go.Figure()
                fig_ton.add_trace(go.Scatter(
                    x=ton_por_mes['Mes_Comercial'],
                    y=ton_por_mes[col_toneladas],
                    mode='lines+markers',
                    line=dict(color='#EF553B', width=2),
                    marker=dict(size=8),
                    fill='tozeroy',
                    fillcolor='rgba(239, 85, 59, 0.1)'
                ))
                
                fig_ton.update_layout(
                    title="Toneladas",
                    xaxis_title="Mês Comercial",
                    yaxis_title="Toneladas (Tn)",
                    height=300
                )
                
                st.plotly_chart(fig_ton, use_container_width=True)
        
        st.markdown("---")
        
        # Evolução dos top vendedores da equipe
        st.markdown("#### 👤 Evolução dos Top 5 Vendedores da Equipe")
        
        top_vendedores_equipe = df_gerente_evolucao.groupby(st.session_state['col_vendedor'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(5).index.tolist()
        
        vendas_vendedores_mes = df_gerente_evolucao[df_gerente_evolucao[st.session_state['col_vendedor']].isin(top_vendedores_equipe)].groupby(['Mes_Comercial', st.session_state['col_vendedor']])[st.session_state['col_valor']].sum().reset_index()
        vendas_vendedores_mes['Ordem'] = vendas_vendedores_mes['Mes_Comercial'].apply(ordenar_mes_comercial)
        vendas_vendedores_mes = vendas_vendedores_mes.sort_values('Ordem')
        
        fig_vendedores = go.Figure()
        cores = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A']
        
        for idx, vendedor in enumerate(top_vendedores_equipe):
            dados_vendedor = vendas_vendedores_mes[vendas_vendedores_mes[st.session_state['col_vendedor']] == vendedor]
            fig_vendedores.add_trace(go.Scatter(
                x=dados_vendedor['Mes_Comercial'],
                y=dados_vendedor[st.session_state['col_valor']],
                mode='lines+markers',
                name=vendedor,
                line=dict(color=cores[idx], width=2),
                marker=dict(size=6)
            ))
        
        fig_vendedores.update_layout(
            title=f"Performance dos Top 5 Vendedores - {gerente_evolucao}",
            xaxis_title="Mês Comercial",
            yaxis_title="Valor (R$)",
            hovermode='x unified',
            height=500,
            showlegend=True
        )
        
        st.plotly_chart(fig_vendedores, use_container_width=True)

# ==============================
# ABA: COMPARATIVO
# ==============================
with tab_comparativo:
    st.markdown("### ⚖️ Comparativo entre Gerentes Regionais")
    
    st.info("📊 Selecione dois gerentes regionais para comparar suas performances")
    
    # Seletores de gerentes
    col_sel1, col_sel2 = st.columns(2)
    
    with col_sel1:
        gerente_a = st.selectbox("Gerente Regional A:", df_gerentes_analise.index.tolist(), key="gerente_a")
    
    with col_sel2:
        gerentes_disponiveis_b = [g for g in df_gerentes_analise.index.tolist() if g != gerente_a]
        gerente_b = st.selectbox("Gerente Regional B:", gerentes_disponiveis_b, key="gerente_b") if gerentes_disponiveis_b else None
    
    if gerente_a and gerente_b:
        df_gerente_a = df_vendas_original[df_vendas_original[col_gerente_regional] == gerente_a]
        df_gerente_b = df_vendas_original[df_vendas_original[col_gerente_regional] == gerente_b]
        
        # KPIs Comparativos
        st.markdown("---")
        st.markdown("#### 📊 Comparação de KPIs")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        # Vendas
        vendas_a = df_gerente_a[st.session_state['col_valor']].sum()
        vendas_b = df_gerente_b[st.session_state['col_valor']].sum()
        delta_vendas = ((vendas_a - vendas_b) / vendas_b * 100) if vendas_b > 0 else 0
        
        with col1:
            st.metric("💰 Vendas - A", formatar_moeda(vendas_a))
            st.metric("💰 Vendas - B", formatar_moeda(vendas_b), delta=f"{delta_vendas:+.1f}%")
        
        # Clientes
        clientes_a = df_gerente_a[st.session_state['col_codCliente']].nunique()
        clientes_b = df_gerente_b[st.session_state['col_codCliente']].nunique()
        
        with col2:
            st.metric("👥 Clientes - A", f"{clientes_a:,}")
            st.metric("👥 Clientes - B", f"{clientes_b:,}", delta=f"{clientes_a - clientes_b:+,}")
        
        # Pedidos
        pedidos_a = df_gerente_a['Pedido_Unico'].nunique()
        pedidos_b = df_gerente_b['Pedido_Unico'].nunique()
        
        with col3:
            st.metric("📦 Pedidos - A", f"{pedidos_a:,}")
            st.metric("📦 Pedidos - B", f"{pedidos_b:,}", delta=f"{pedidos_a - pedidos_b:+,}")
        
        # Ticket Médio
        ticket_a = vendas_a / pedidos_a if pedidos_a > 0 else 0
        ticket_b = vendas_b / pedidos_b if pedidos_b > 0 else 0
        delta_ticket = ((ticket_a - ticket_b) / ticket_b * 100) if ticket_b > 0 else 0
        
        with col4:
            st.metric("🎯 Ticket Médio - A", formatar_moeda(ticket_a))
            st.metric("🎯 Ticket Médio - B", formatar_moeda(ticket_b), delta=f"{delta_ticket:+.1f}%")
        
        # Vendedores
        vendedores_a = df_gerente_a[st.session_state['col_vendedor']].nunique()
        vendedores_b = df_gerente_b[st.session_state['col_vendedor']].nunique()
        
        with col5:
            st.metric("👤 Vendedores - A", vendedores_a)
            st.metric("👤 Vendedores - B", vendedores_b, delta=f"{vendedores_a - vendedores_b:+}")
        
        st.markdown("---")
        
        # Gráfico de Evolução Comparativa
        st.markdown("#### 📈 Evolução Comparativa de Vendas")
        
        # Preparar dados de evolução
        vendas_a_mes = df_gerente_a.groupby('Mes_Comercial')[st.session_state['col_valor']].sum().reset_index()
        vendas_a_mes['Ordem'] = vendas_a_mes['Mes_Comercial'].apply(ordenar_mes_comercial)
        vendas_a_mes = vendas_a_mes.sort_values('Ordem')
        
        vendas_b_mes = df_gerente_b.groupby('Mes_Comercial')[st.session_state['col_valor']].sum().reset_index()
        vendas_b_mes['Ordem'] = vendas_b_mes['Mes_Comercial'].apply(ordenar_mes_comercial)
        vendas_b_mes = vendas_b_mes.sort_values('Ordem')
        
        fig_comp = go.Figure()
        
        fig_comp.add_trace(go.Scatter(
            x=vendas_a_mes['Mes_Comercial'],
            y=vendas_a_mes[st.session_state['col_valor']],
            mode='lines+markers',
            name=gerente_a,
            line=dict(color='#00CC96', width=3),
            marker=dict(size=10),
            fill='tozeroy',
            fillcolor='rgba(0, 204, 150, 0.1)'
        ))
        
        fig_comp.add_trace(go.Scatter(
            x=vendas_b_mes['Mes_Comercial'],
            y=vendas_b_mes[st.session_state['col_valor']],
            mode='lines+markers',
            name=gerente_b,
            line=dict(color='#636EFA', width=3),
            marker=dict(size=10),
            fill='tozeroy',
            fillcolor='rgba(99, 110, 250, 0.1)'
        ))
        
        fig_comp.update_layout(
            title="Evolução de Vendas - Comparativo",
            xaxis_title="Mês Comercial",
            yaxis_title="Valor (R$)",
            hovermode='x unified',
            height=500,
            showlegend=True
        )
        
        st.plotly_chart(fig_comp, use_container_width=True)
        
        st.markdown("---")
        
        # Comparação de Quantidade e Toneladas
        col_comp1, col_comp2 = st.columns(2)
        
        with col_comp1:
            if col_quantidade != 'Nenhuma' and col_quantidade in df_gerente_a.columns:
                st.markdown("#### 📦 Quantidade")
                
                qtde_a = df_gerente_a[col_quantidade].sum()
                qtde_b = df_gerente_b[col_quantidade].sum()
                
                fig_qtde = go.Figure()
                
                fig_qtde.add_trace(go.Bar(
                    x=[gerente_a, gerente_b],
                    y=[qtde_a, qtde_b],
                    marker_color=['#00CC96', '#636EFA'],
                    text=[f"{qtde_a:,.0f} un", f"{qtde_b:,.0f} un"],
                    textposition='outside'
                ))
                
                fig_qtde.update_layout(
                    title="Comparação de Quantidade Total",
                    yaxis_title="Quantidade (un)",
                    height=400,
                    showlegend=False
                )
                
                st.plotly_chart(fig_qtde, use_container_width=True)
        
        with col_comp2:
            if col_toneladas != 'Nenhuma' and col_toneladas in df_gerente_a.columns:
                st.markdown("#### ⚖️ Toneladas")
                
                ton_a = df_gerente_a[col_toneladas].sum()
                ton_b = df_gerente_b[col_toneladas].sum()
                
                fig_ton = go.Figure()
                
                fig_ton.add_trace(go.Bar(
                    x=[gerente_a, gerente_b],
                    y=[ton_a, ton_b],
                    marker_color=['#00CC96', '#636EFA'],
                    text=[f"{ton_a:,.2f} Tn", f"{ton_b:,.2f} Tn"],
                    textposition='outside'
                ))
                
                fig_ton.update_layout(
                    title="Comparação de Toneladas Total",
                    yaxis_title="Toneladas (Tn)",
                    height=400,
                    showlegend=False
                )
                
                st.plotly_chart(fig_ton, use_container_width=True)
        
        st.markdown("---")
        
        # Comparação de Top Produtos
        st.markdown("#### 🛍️ Comparação de Top 5 Produtos")
        
        col_prod_a, col_prod_b = st.columns(2)
        
        with col_prod_a:
            st.markdown(f"##### {gerente_a}")
            top_prod_a = df_gerente_a.groupby(st.session_state['col_produto'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(5)
            for idx, (produto, valor) in enumerate(top_prod_a.items(), 1):
                st.write(f"{idx}. **{produto}**: {formatar_moeda(valor)}")
        
        with col_prod_b:
            st.markdown(f"##### {gerente_b}")
            top_prod_b = df_gerente_b.groupby(st.session_state['col_produto'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(5)
            for idx, (produto, valor) in enumerate(top_prod_b.items(), 1):
                st.write(f"{idx}. **{produto}**: {formatar_moeda(valor)}")
        
        st.markdown("---")
        
        # Comparação de Top Vendedores
        st.markdown("#### 👤 Comparação de Top 5 Vendedores")
        
        col_vend_a, col_vend_b = st.columns(2)
        
        with col_vend_a:
            st.markdown(f"##### {gerente_a}")
            top_vend_a = df_gerente_a.groupby(st.session_state['col_vendedor'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(5)
            for idx, (vendedor, valor) in enumerate(top_vend_a.items(), 1):
                st.write(f"{idx}. **{vendedor}**: {formatar_moeda(valor)}")
        
        with col_vend_b:
            st.markdown(f"##### {gerente_b}")
            top_vend_b = df_gerente_b.groupby(st.session_state['col_vendedor'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(5)
            for idx, (vendedor, valor) in enumerate(top_vend_b.items(), 1):
                st.write(f"{idx}. **{vendedor}**: {formatar_moeda(valor)}")
    else:
        st.info("👆 Selecione dois gerentes regionais para comparar")
