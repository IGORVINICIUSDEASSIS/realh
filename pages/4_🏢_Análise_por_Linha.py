import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sys
sys.path.append('/workspaces/realh')
from utils import formatar_moeda, ordenar_mes_comercial, obter_periodo_mes_comercial, exibir_logo

st.set_page_config(page_title="Análise por Linha", page_icon="🏢", layout="wide")

exibir_logo()

st.title("🏢 Análise por Linha de Produto")

# Verificar se os dados foram carregados
if 'df_vendas' not in st.session_state:
    st.warning("⚠️ Por favor, carregue os dados na página inicial primeiro!")
    st.stop()

# Verificar se coluna Linha está configurada
col_linha = st.session_state.get('col_linha', 'Nenhuma')
if col_linha == "Nenhuma" or col_linha not in st.session_state['df_vendas'].columns:
    st.warning("⚠️ Configure a coluna 'Linha' na página inicial para visualizar esta análise.")
    st.stop()

# Pegar dados do session_state
df_vendas = st.session_state['df_vendas']
df_vendas_original = st.session_state['df_vendas_original']
df_devolucoes = st.session_state.get('df_devolucoes', pd.DataFrame())
df_devolucoes_original = st.session_state.get('df_devolucoes_original', pd.DataFrame())
meses_comerciais_disponiveis = st.session_state.get('meses_comerciais_disponiveis', [])

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
        
        st.sidebar.info(f"📅 {data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}")
    else:
        st.sidebar.info("📅 Exibindo todos os períodos")

# ==============================
# PROCESSAR DADOS POR LINHA
# ==============================
vendas_por_linha = df_vendas.groupby(col_linha)[st.session_state['col_valor']].sum().sort_values(ascending=False)

if not df_devolucoes.empty and col_linha in df_devolucoes.columns:
    devolucoes_por_linha = df_devolucoes.groupby(col_linha)[st.session_state['col_valor']].sum()
else:
    devolucoes_por_linha = pd.Series(dtype=float)

# Calcular quantidade e toneladas por linha
quantidade_por_linha = pd.Series(dtype=float)
toneladas_por_linha = pd.Series(dtype=float)

col_quantidade = st.session_state.get('col_quantidade', 'Nenhuma')
col_toneladas = st.session_state.get('col_toneladas', 'Nenhuma')

if col_quantidade != 'Nenhuma' and col_quantidade in df_vendas.columns:
    quantidade_por_linha = df_vendas.groupby(col_linha)[col_quantidade].sum()

if col_toneladas != 'Nenhuma' and col_toneladas in df_vendas.columns:
    toneladas_por_linha = df_vendas.groupby(col_linha)[col_toneladas].sum()

df_linhas_analise = pd.DataFrame({
    'Vendas': vendas_por_linha,
    'Devoluções': devolucoes_por_linha,
    'Quantidade': quantidade_por_linha,
    'Toneladas': toneladas_por_linha
}).fillna(0)

df_linhas_analise['Líquido'] = df_linhas_analise['Vendas'] - df_linhas_analise['Devoluções']
df_linhas_analise['Taxa Dev. (%)'] = (df_linhas_analise['Devoluções'] / df_linhas_analise['Vendas'] * 100).fillna(0)
df_linhas_analise = df_linhas_analise.sort_values('Vendas', ascending=False)

# ==============================
# ABAS DE ANÁLISE
# ==============================
tab_metricas, tab_insights, tab_detalhes, tab_evolucao = st.tabs(["📊 Visão Geral", "🔍 Insights", "📋 Detalhamento", "📈 Evolução"])

# ==============================
# ABA: VISÃO GERAL
# ==============================
with tab_metricas:
    st.markdown("### 💰 Vendas e Devoluções por Linha")
    
    # Cards para cada linha
    num_linhas = len(df_linhas_analise)
    cols = st.columns(min(num_linhas, 3))
    
    for idx, (linha, row) in enumerate(df_linhas_analise.iterrows()):
        with cols[idx % min(num_linhas, 3)]:
            st.markdown(f"#### 🏢 {linha}")
            st.metric("💰 Vendas", formatar_moeda(row['Vendas']))
            st.metric("↩️ Devoluções", formatar_moeda(row['Devoluções']))
            st.metric("💵 Líquido", formatar_moeda(row['Líquido']))
            st.metric("📉 Taxa Devolução", f"{row['Taxa Dev. (%)']:.1f}%")
            
            # Mostrar Quantidade ou Toneladas dependendo da linha
            if linha.upper() == 'HOMEOPET' and row['Quantidade'] > 0:
                st.metric("📦 Quantidade", f"{row['Quantidade']:,.0f} un")
            elif linha.upper() in ['NUTRIÇÃO', 'NUTRICAO'] and row['Toneladas'] > 0:
                st.metric("⚖️ Toneladas", f"{row['Toneladas']:,.2f} Tn")
            elif row['Quantidade'] > 0:
                st.metric("📦 Quantidade", f"{row['Quantidade']:,.0f} un")
            
            participacao = (row['Vendas'] / vendas_por_linha.sum() * 100) if vendas_por_linha.sum() > 0 else 0
            st.info(f"📊 Representa {participacao:.1f}% do total")

# ==============================
# ABA: INSIGHTS
# ==============================
with tab_insights:
    st.markdown("### 🔍 Insights por Linha")
    
    col_ins1, col_ins2 = st.columns(2)
    
    with col_ins1:
        st.markdown("#### 🏆 Linha com Maior Faturamento")
        if len(vendas_por_linha) > 0:
            melhor_linha = vendas_por_linha.index[0]
            melhor_valor = vendas_por_linha.iloc[0]
            participacao_melhor = (melhor_valor / vendas_por_linha.sum() * 100)
            
            st.success(f"**{melhor_linha}**")
            st.write(f"💰 Faturamento: {formatar_moeda(melhor_valor)}")
            st.write(f"📊 Participação: {participacao_melhor:.1f}%")
            
            df_melhor = df_vendas[df_vendas[col_linha] == melhor_linha]
            clientes_melhor = df_melhor[st.session_state['col_codCliente']].nunique()
            pedidos_melhor = df_melhor['Pedido_Unico'].nunique()
            st.write(f"👥 Clientes: {clientes_melhor:,}")
            st.write(f"📦 Pedidos: {pedidos_melhor:,}")
    
    with col_ins2:
        st.markdown("#### ⚠️ Linha com Maior Taxa de Devolução")
        if len(df_linhas_analise[df_linhas_analise['Taxa Dev. (%)'] > 0]) > 0:
            linha_maior_dev = df_linhas_analise.sort_values('Taxa Dev. (%)', ascending=False).index[0]
            taxa_dev = df_linhas_analise.loc[linha_maior_dev, 'Taxa Dev. (%)']
            valor_dev = df_linhas_analise.loc[linha_maior_dev, 'Devoluções']
            
            st.warning(f"**{linha_maior_dev}**")
            st.write(f"📉 Taxa Devolução: {taxa_dev:.1f}%")
            st.write(f"↩️ Valor Devolvido: {formatar_moeda(valor_dev)}")
            
            if not df_devolucoes.empty:
                df_dev_linha = df_devolucoes[df_devolucoes[col_linha] == linha_maior_dev]
                clientes_dev = df_dev_linha[st.session_state['col_codCliente']].nunique()
                pedidos_dev = df_dev_linha['Pedido_Unico'].nunique()
                st.write(f"👥 Clientes com Devolução: {clientes_dev:,}")
                st.write(f"📦 Pedidos Devolvidos: {pedidos_dev:,}")
        else:
            st.info("Nenhuma devolução registrada")
    
    st.markdown("---")
    st.markdown("#### 📊 Comparativo de Performance")
    
    # Gráfico comparativo
    fig_comparativo = go.Figure()
    
    fig_comparativo.add_trace(go.Bar(
        name='Vendas',
        x=df_linhas_analise.index,
        y=df_linhas_analise['Vendas'],
        marker_color='#00CC96'
    ))
    
    fig_comparativo.add_trace(go.Bar(
        name='Devoluções',
        x=df_linhas_analise.index,
        y=df_linhas_analise['Devoluções'],
        marker_color='#EF553B'
    ))
    
    fig_comparativo.update_layout(
        title="Vendas vs Devoluções por Linha",
        xaxis_title="Linha",
        yaxis_title="Valor (R$)",
        barmode='group',
        height=400
    )
    
    st.plotly_chart(fig_comparativo, use_container_width=True)
    
    # Evolução temporal
    if mes_selecionado == 'Todos os Meses':
        st.markdown("---")
        st.markdown("#### 📈 Evolução Temporal por Linha")
        
        vendas_linha_mes = df_vendas_original.groupby(['Mes_Comercial', col_linha])[st.session_state['col_valor']].sum().reset_index()
        
        fig_evolucao = go.Figure()
        cores_linhas = ['#00CC96', '#636EFA', '#EF553B', '#FFA15A', '#19D3F3']
        
        for idx, linha in enumerate(df_linhas_analise.index):
            dados_linha = vendas_linha_mes[vendas_linha_mes[col_linha] == linha]
            dados_linha['Ordem'] = dados_linha['Mes_Comercial'].apply(ordenar_mes_comercial)
            dados_linha = dados_linha.sort_values('Ordem')
            
            fig_evolucao.add_trace(go.Scatter(
                x=dados_linha['Mes_Comercial'],
                y=dados_linha[st.session_state['col_valor']],
                mode='lines+markers',
                name=linha,
                line=dict(color=cores_linhas[idx % len(cores_linhas)], width=3),
                marker=dict(size=8)
            ))
        
        fig_evolucao.update_layout(
            title="Evolução de Vendas por Mês Comercial",
            xaxis_title="Mês Comercial",
            yaxis_title="Vendas (R$)",
            hovermode='x unified',
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig_evolucao, use_container_width=True)

# ==============================
# ABA: DETALHAMENTO
# ==============================
with tab_detalhes:
    st.markdown("### 📋 Detalhamento Completo por Linha")
    
    # Tabela resumo
    df_linhas_display = df_linhas_analise.copy()
    df_linhas_display['Vendas'] = df_linhas_display['Vendas'].apply(formatar_moeda)
    df_linhas_display['Devoluções'] = df_linhas_display['Devoluções'].apply(formatar_moeda)
    df_linhas_display['Líquido'] = df_linhas_display['Líquido'].apply(formatar_moeda)
    df_linhas_display['Taxa Dev. (%)'] = df_linhas_display['Taxa Dev. (%)'].apply(lambda x: f"{x:.2f}%")
    df_linhas_display['Quantidade'] = df_linhas_display['Quantidade'].apply(lambda x: f"{x:,.0f}" if x > 0 else "-")
    df_linhas_display['Toneladas'] = df_linhas_display['Toneladas'].apply(lambda x: f"{x:,.2f}" if x > 0 else "-")
    
    st.dataframe(df_linhas_display, use_container_width=True)
    
    # Análise individual
    st.markdown("---")
    st.markdown("#### 🔍 Análise Individual por Linha")
    
    linha_selecionada = st.selectbox("Selecione uma linha:", df_linhas_analise.index.tolist())
    
    if linha_selecionada:
        df_linha_sel = df_vendas[df_vendas[col_linha] == linha_selecionada]
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📦 Pedidos", df_linha_sel['Pedido_Unico'].nunique())
        col2.metric("👥 Clientes", df_linha_sel[st.session_state['col_codCliente']].nunique())
        col3.metric("🛍️ Produtos", df_linha_sel[st.session_state['col_produto']].nunique())
        
        ticket_medio_linha = df_linha_sel[st.session_state['col_valor']].sum() / df_linha_sel['Pedido_Unico'].nunique() if df_linha_sel['Pedido_Unico'].nunique() > 0 else 0
        col4.metric("🎯 Ticket Médio", formatar_moeda(ticket_medio_linha))
        
        col_det1, col_det2 = st.columns(2)
        
        with col_det1:
            st.markdown("##### 🏆 Top 5 Produtos")
            top_produtos_linha = df_linha_sel.groupby(st.session_state['col_produto'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(5)
            for idx, (produto, valor) in enumerate(top_produtos_linha.items(), 1):
                st.write(f"{idx}. **{produto}**: {formatar_moeda(valor)}")
        
        with col_det2:
            st.markdown("##### 👥 Top 5 Clientes")
            top_clientes_linha = df_linha_sel.groupby(st.session_state['col_cliente'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(5)
            for idx, (cliente, valor) in enumerate(top_clientes_linha.items(), 1):
                st.write(f"{idx}. **{cliente}**: {formatar_moeda(valor)}")
        
        st.markdown("---")
        
        # Top 5 por Quantidade e Toneladas para a linha selecionada
        col_top1, col_top2 = st.columns(2)
        
        with col_top1:
            st.markdown("##### 📦 Top 5 Produtos por Quantidade")
            if col_quantidade != 'Nenhuma' and col_quantidade in df_linha_sel.columns:
                top_qtde = df_linha_sel.groupby(st.session_state['col_produto']).agg({
                    col_quantidade: 'sum',
                    st.session_state['col_valor']: 'sum'
                }).sort_values(col_quantidade, ascending=False).head(5)
                for idx, (produto, row) in enumerate(top_qtde.iterrows(), 1):
                    st.write(f"{idx}. **{produto}**: {row[col_quantidade]:,.0f} un ({formatar_moeda(row[st.session_state['col_valor']])})")
            else:
                st.info("Dados de quantidade não disponíveis")
        
        with col_top2:
            st.markdown("##### ⚖️ Top 5 Produtos por Toneladas")
            if col_toneladas != 'Nenhuma' and col_toneladas in df_linha_sel.columns:
                top_ton = df_linha_sel.groupby(st.session_state['col_produto']).agg({
                    col_toneladas: 'sum',
                    st.session_state['col_valor']: 'sum'
                }).sort_values(col_toneladas, ascending=False).head(5)
                for idx, (produto, row) in enumerate(top_ton.iterrows(), 1):
                    st.write(f"{idx}. **{produto}**: {row[col_toneladas]:,.2f} Tn ({formatar_moeda(row[st.session_state['col_valor']])})")
            else:
                st.info("Dados de toneladas não disponíveis")

# ==============================
# ABA: EVOLUÇÃO
# ==============================
with tab_evolucao:
    st.markdown("### 📈 Evolução por Mês Comercial")
    
    # Seletor de linha para análise de evolução
    linha_evolucao = st.selectbox("Selecione uma linha para análise:", df_linhas_analise.index.tolist(), key="linha_evolucao")
    
    if linha_evolucao:
        df_linha_evolucao = df_vendas_original[df_vendas_original[col_linha] == linha_evolucao]
        
        # Preparar dicionário de agregação
        agg_dict = {st.session_state['col_valor']: 'sum'}
        
        if col_quantidade != 'Nenhuma' and col_quantidade in df_linha_evolucao.columns:
            agg_dict[col_quantidade] = 'sum'
        
        if col_toneladas != 'Nenhuma' and col_toneladas in df_linha_evolucao.columns:
            agg_dict[col_toneladas] = 'sum'
        
        # Agrupar por mês comercial e produto
        evolucao_vendas = df_linha_evolucao.groupby(['Mes_Comercial', st.session_state['col_produto']]).agg(agg_dict).reset_index()
        
        # Ordenar por mês comercial
        evolucao_vendas['Ordem'] = evolucao_vendas['Mes_Comercial'].apply(ordenar_mes_comercial)
        evolucao_vendas = evolucao_vendas.sort_values('Ordem')
        
        # Gráfico de Evolução de Vendas
        st.markdown("#### 💰 Evolução do Valor de Vendas")
        vendas_por_mes = df_linha_evolucao.groupby('Mes_Comercial')[st.session_state['col_valor']].sum().reset_index()
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
            title=f"Evolução de Vendas - {linha_evolucao}",
            xaxis_title="Mês Comercial",
            yaxis_title="Valor (R$)",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig_vendas, use_container_width=True)
        
        # Gráfico de Evolução de Quantidade
        if col_quantidade != 'Nenhuma' and col_quantidade in df_linha_evolucao.columns:
            st.markdown("#### 📦 Evolução da Quantidade")
            qtde_por_mes = df_linha_evolucao.groupby('Mes_Comercial')[col_quantidade].sum().reset_index()
            qtde_por_mes['Ordem'] = qtde_por_mes['Mes_Comercial'].apply(ordenar_mes_comercial)
            qtde_por_mes = qtde_por_mes.sort_values('Ordem')
            
            fig_qtde = go.Figure()
            fig_qtde.add_trace(go.Scatter(
                x=qtde_por_mes['Mes_Comercial'],
                y=qtde_por_mes[col_quantidade],
                mode='lines+markers',
                name='Quantidade',
                line=dict(color='#636EFA', width=3),
                marker=dict(size=10),
                fill='tozeroy',
                fillcolor='rgba(99, 110, 250, 0.1)'
            ))
            
            fig_qtde.update_layout(
                title=f"Evolução de Quantidade - {linha_evolucao}",
                xaxis_title="Mês Comercial",
                yaxis_title="Quantidade (un)",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig_qtde, use_container_width=True)
        
        # Gráfico de Evolução de Toneladas
        if col_toneladas != 'Nenhuma' and col_toneladas in df_linha_evolucao.columns:
            st.markdown("#### ⚖️ Evolução das Toneladas")
            ton_por_mes = df_linha_evolucao.groupby('Mes_Comercial')[col_toneladas].sum().reset_index()
            ton_por_mes['Ordem'] = ton_por_mes['Mes_Comercial'].apply(ordenar_mes_comercial)
            ton_por_mes = ton_por_mes.sort_values('Ordem')
            
            fig_ton = go.Figure()
            fig_ton.add_trace(go.Scatter(
                x=ton_por_mes['Mes_Comercial'],
                y=ton_por_mes[col_toneladas],
                mode='lines+markers',
                name='Toneladas',
                line=dict(color='#EF553B', width=3),
                marker=dict(size=10),
                fill='tozeroy',
                fillcolor='rgba(239, 85, 59, 0.1)'
            ))
            
            fig_ton.update_layout(
                title=f"Evolução de Toneladas - {linha_evolucao}",
                xaxis_title="Mês Comercial",
                yaxis_title="Toneladas (Tn)",
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig_ton, use_container_width=True)
        
        # Top 10 Produtos na Evolução
        st.markdown("---")
        st.markdown("#### 🏆 Top 10 Produtos por Período")
        
        top_produtos = df_linha_evolucao.groupby(st.session_state['col_produto'])[st.session_state['col_valor']].sum().sort_values(ascending=False).head(10).index.tolist()
        
        tab_valor, tab_qtde, tab_ton = st.tabs(["💰 Por Valor", "📦 Por Quantidade", "⚖️ Por Toneladas"])
        
        with tab_valor:
            df_top_valor = evolucao_vendas[evolucao_vendas[st.session_state['col_produto']].isin(top_produtos)]
            
            fig_top_valor = go.Figure()
            cores = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52']
            
            for idx, produto in enumerate(top_produtos):
                dados_produto = df_top_valor[df_top_valor[st.session_state['col_produto']] == produto]
                fig_top_valor.add_trace(go.Scatter(
                    x=dados_produto['Mes_Comercial'],
                    y=dados_produto[st.session_state['col_valor']],
                    mode='lines+markers',
                    name=produto,
                    line=dict(color=cores[idx % len(cores)], width=2),
                    marker=dict(size=6)
                ))
            
            fig_top_valor.update_layout(
                title="Evolução dos Top 10 Produtos por Valor",
                xaxis_title="Mês Comercial",
                yaxis_title="Valor (R$)",
                hovermode='x unified',
                height=500,
                showlegend=True
            )
            
            st.plotly_chart(fig_top_valor, use_container_width=True)
        
        with tab_qtde:
            if col_quantidade != 'Nenhuma' and col_quantidade in df_linha_evolucao.columns:
                df_top_qtde = evolucao_vendas[evolucao_vendas[st.session_state['col_produto']].isin(top_produtos)]
                
                fig_top_qtde = go.Figure()
                
                for idx, produto in enumerate(top_produtos):
                    dados_produto = df_top_qtde[df_top_qtde[st.session_state['col_produto']] == produto]
                    fig_top_qtde.add_trace(go.Scatter(
                        x=dados_produto['Mes_Comercial'],
                        y=dados_produto[col_quantidade],
                        mode='lines+markers',
                        name=produto,
                        line=dict(color=cores[idx % len(cores)], width=2),
                        marker=dict(size=6)
                    ))
                
                fig_top_qtde.update_layout(
                    title="Evolução dos Top 10 Produtos por Quantidade",
                    xaxis_title="Mês Comercial",
                    yaxis_title="Quantidade (un)",
                    hovermode='x unified',
                    height=500,
                    showlegend=True
                )
                
                st.plotly_chart(fig_top_qtde, use_container_width=True)
            else:
                st.info("Dados de quantidade não disponíveis")
        
        with tab_ton:
            if col_toneladas != 'Nenhuma' and col_toneladas in df_linha_evolucao.columns:
                df_top_ton = evolucao_vendas[evolucao_vendas[st.session_state['col_produto']].isin(top_produtos)]
                
                fig_top_ton = go.Figure()
                
                for idx, produto in enumerate(top_produtos):
                    dados_produto = df_top_ton[df_top_ton[st.session_state['col_produto']] == produto]
                    fig_top_ton.add_trace(go.Scatter(
                        x=dados_produto['Mes_Comercial'],
                        y=dados_produto[col_toneladas],
                        mode='lines+markers',
                        name=produto,
                        line=dict(color=cores[idx % len(cores)], width=2),
                        marker=dict(size=6)
                    ))
                
                fig_top_ton.update_layout(
                    title="Evolução dos Top 10 Produtos por Toneladas",
                    xaxis_title="Mês Comercial",
                    yaxis_title="Toneladas (Tn)",
                    hovermode='x unified',
                    height=500,
                    showlegend=True
                )
                
                st.plotly_chart(fig_top_ton, use_container_width=True)
            else:
                st.info("Dados de toneladas não disponíveis")

