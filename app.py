import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import tempfile
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend sem interface gráfica

# ==============================
# CONFIGURAÇÃO DA PÁGINA
# ==============================
st.set_page_config(
    page_title="Relatórios Automáticos - Real H",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Relatórios Automáticos - Real H")

# ==============================
# UPLOAD DO ARQUIVO
# ==============================
uploaded_file = st.file_uploader("Envie sua planilha (.xlsx ou .csv)", type=["xlsx", "csv"])

if uploaded_file:
    # Ler o arquivo
    if uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file, sep=";", decimal=",")

    st.success("✅ Planilha carregada com sucesso!")
    st.write("### Visualização dos dados:")
    st.dataframe(df.head())

    # ==============================
    # SELEÇÃO DE CAMPOS IMPORTANTES
    # ==============================
    st.sidebar.header("⚙️ Configurações dos Campos")

    col_cliente = st.sidebar.selectbox("Coluna de Cliente:", df.columns, index=df.columns.get_loc("Cliente") if "Cliente" in df.columns else 0)
    col_vendedor = st.sidebar.selectbox("Coluna de Vendedor:", df.columns, index=df.columns.get_loc("Vendedor") if "Vendedor" in df.columns else 0)
    col_produto = st.sidebar.selectbox("Coluna de Produto:", df.columns, index=df.columns.get_loc("Produto") if "Produto" in df.columns else 0)
    col_valor = st.sidebar.selectbox("Coluna de Valor Líquido Total:", df.columns, index=df.columns.get_loc("Vlr. Líq. Total") if "Vlr. Líq. Total" in df.columns else 0)
    col_data = st.sidebar.selectbox("Coluna de Data:", df.columns, index=df.columns.get_loc("Data Emissão") if "Data Emissão" in df.columns else 0)
    col_pedido = st.sidebar.selectbox("Coluna de Nº Pedido:", df.columns, index=df.columns.get_loc("Nº Pedido") if "Nº Pedido" in df.columns else 0)
    col_tipo = st.sidebar.selectbox("Coluna de Tipo:", df.columns, index=df.columns.get_loc("Tipo") if "Tipo" in df.columns else 0)
    col_regiao = st.sidebar.selectbox("Coluna de Região (opcional):", ["Nenhuma"] + list(df.columns), index=df.columns.get_loc("Regional.") + 1 if "Regional." in df.columns else 0)

    # ==============================
    # FILTRAR APENAS TIPO "VEN"
    # ==============================
    df_filtrado = df[df[col_tipo] == "VEN"].copy()
    
    if df_filtrado.empty:
        st.error("⚠️ Nenhum registro com Tipo = 'VEN' encontrado!")
        st.stop()
    
    st.info(f"✅ Filtrado: {len(df_filtrado)} registros com Tipo = 'VEN' (de {len(df)} totais)")
    
    # ==============================
    # CRIAR COLUNA CALCULADA ÚNICA
    # ==============================
    df_filtrado['Pedido_Unico'] = df_filtrado[col_cliente].astype(str) + "_" + df_filtrado[col_pedido].astype(str)
    
    # Converter datas
    df_filtrado[col_data] = pd.to_datetime(df_filtrado[col_data], errors="coerce")

    # ==============================
    # MÉTRICAS GERAIS
    # ==============================
    st.markdown("## 📈 Indicadores Gerais")

    valor_total = df_filtrado[col_valor].sum()
    clientes_unicos = df_filtrado[col_cliente].nunique()
    produtos_unicos = df_filtrado[col_produto].nunique()
    vendedores_unicos = df_filtrado[col_vendedor].nunique()
    pedidos_unicos = df_filtrado['Pedido_Unico'].nunique()  # NOVA MÉTRICA
    ticket_medio = valor_total / clientes_unicos if clientes_unicos > 0 else 0
    ticket_medio_pedido = valor_total / pedidos_unicos if pedidos_unicos > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Faturamento Total", f"R$ {valor_total:,.2f}")
    col2.metric("👥 Clientes Atendidos", clientes_unicos)
    col3.metric("📦 Pedidos Únicos", pedidos_unicos)  # NOVA MÉTRICA
    col4.metric("🎯 Ticket Médio/Pedido", f"R$ {ticket_medio_pedido:,.2f}")

    col5, col6, col7 = st.columns(3)
    col5.metric("🛍️ Produtos Diferentes", produtos_unicos)
    col6.metric("🧑‍💼 Vendedores", vendedores_unicos)
    col7.metric("📊 Ticket Médio/Cliente", f"R$ {ticket_medio:,.2f}")

    st.markdown("---")

    # ==============================
    # GRÁFICOS INTERATIVOS
    # ==============================
    graficos_para_pdf = []

    # CLIENTES - Top 15 + Tabela completa
    st.subheader("📊 Faturamento por Cliente")
    todos_clientes = df_filtrado.groupby(col_cliente)[col_valor].sum().sort_values(ascending=False).reset_index()
    
    col_grafico, col_filtro = st.columns([3, 1])
    with col_filtro:
        mostrar_todos_clientes = st.checkbox("Mostrar todos os clientes", value=False, key="clientes")
    
    if mostrar_todos_clientes:
        st.dataframe(
            todos_clientes.style.format({col_valor: "R$ {:,.2f}"}),
            use_container_width=True,
            height=400
        )
    else:
        top_clientes = todos_clientes.head(15)
        fig_clientes = px.bar(top_clientes, y=col_cliente, x=col_valor, 
                              orientation='h', text_auto='.2s',
                              title="Top 15 Clientes", color_discrete_sequence=['#1f77b4'],
                              height=500)
        fig_clientes.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
        fig_clientes.update_traces(textposition='outside')
        st.plotly_chart(fig_clientes, use_container_width=True)
        graficos_para_pdf.append(('top_clientes', fig_clientes))
        st.caption(f"Exibindo top 15 de {len(todos_clientes)} clientes")

    st.markdown("---")

    # PRODUTOS - Top 15 + Tabela completa
    st.subheader("🏆 Faturamento por Produto")
    todos_produtos = df_filtrado.groupby(col_produto)[col_valor].sum().sort_values(ascending=False).reset_index()
    
    col_grafico2, col_filtro2 = st.columns([3, 1])
    with col_filtro2:
        mostrar_todos_produtos = st.checkbox("Mostrar todos os produtos", value=False, key="produtos")
    
    if mostrar_todos_produtos:
        st.dataframe(
            todos_produtos.style.format({col_valor: "R$ {:,.2f}"}),
            use_container_width=True,
            height=400
        )
    else:
        top_produtos = todos_produtos.head(15)
        fig_produtos = px.bar(top_produtos, y=col_produto, x=col_valor,
                             orientation='h', text_auto='.2s',
                             title="Top 15 Produtos", color_discrete_sequence=['#ff7f0e'],
                             height=500)
        fig_produtos.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
        fig_produtos.update_traces(textposition='outside')
        st.plotly_chart(fig_produtos, use_container_width=True)
        graficos_para_pdf.append(('top_produtos', fig_produtos))
        st.caption(f"Exibindo top 15 de {len(todos_produtos)} produtos")

    st.markdown("---")

    # VENDEDORES - Top 15 + Tabela completa
    st.subheader("🧑‍💼 Faturamento por Vendedor")
    todos_vendedores = df_filtrado.groupby(col_vendedor)[col_valor].sum().sort_values(ascending=False).reset_index()
    
    col_grafico3, col_filtro3 = st.columns([3, 1])
    with col_filtro3:
        mostrar_todos_vendedores = st.checkbox("Mostrar todos os vendedores", value=False, key="vendedores")
    
    if mostrar_todos_vendedores:
        st.dataframe(
            todos_vendedores.style.format({col_valor: "R$ {:,.2f}"}),
            use_container_width=True,
            height=400
        )
    else:
        altura_vendedores = min(600, max(300, len(todos_vendedores) * 40))
        fig_vendedores = px.bar(todos_vendedores, y=col_vendedor, x=col_valor,
                               orientation='h', text_auto='.2s',
                               title="Todos os Vendedores", color_discrete_sequence=['#2ca02c'],
                               height=altura_vendedores)
        fig_vendedores.update_layout(yaxis={'categoryorder':'total ascending'}, showlegend=False)
        fig_vendedores.update_traces(textposition='outside')
        st.plotly_chart(fig_vendedores, use_container_width=True)
        graficos_para_pdf.append(('todos_vendedores', fig_vendedores))
        if len(todos_vendedores) > 15:
            st.caption(f"Exibindo todos os {len(todos_vendedores)} vendedores")

    st.markdown("---")

    st.subheader("📅 Evolução de Vendas ao Longo do Tempo")
    vendas_tempo = df_filtrado.groupby(df_filtrado[col_data].dt.to_period("M"))[col_valor].sum().reset_index()
    vendas_tempo[col_data] = vendas_tempo[col_data].astype(str)
    fig_tempo = px.line(vendas_tempo, x=col_data, y=col_valor, markers=True, 
                       title="Faturamento por Mês", color_discrete_sequence=['#d62728'])
    st.plotly_chart(fig_tempo, use_container_width=True)
    graficos_para_pdf.append(('evolucao_vendas', fig_tempo))

    st.subheader("📦 Pedidos por Mês")
    pedidos_mes = df_filtrado.groupby(df_filtrado[col_data].dt.to_period("M"))['Pedido_Unico'].nunique().reset_index()
    pedidos_mes[col_data] = pedidos_mes[col_data].astype(str)
    fig_pedidos = px.bar(pedidos_mes, x=col_data, y='Pedido_Unico', text_auto=True,
                        title="Quantidade de Pedidos por Mês", color_discrete_sequence=['#9467bd'])
    fig_pedidos.update_layout(yaxis_title="Pedidos Únicos")
    st.plotly_chart(fig_pedidos, use_container_width=True)
    graficos_para_pdf.append(('pedidos_mes', fig_pedidos))

    if col_regiao != "Nenhuma":
        st.subheader("🌎 Faturamento por Região")
        vendas_regiao = df_filtrado.groupby(col_regiao)[col_valor].sum().sort_values(ascending=False).reset_index()
        fig_regiao = px.bar(vendas_regiao, x=col_regiao, y=col_valor, text_auto='.2s', 
                           title="Faturamento por Região", color_discrete_sequence=['#8c564b'])
        st.plotly_chart(fig_regiao, use_container_width=True)
        graficos_para_pdf.append(('faturamento_regiao', fig_regiao))

    # ==============================
    # FUNÇÃO PARA GERAR PDF
    # ==============================
    def gerar_grafico_matplotlib(dados, coluna_x, coluna_y, titulo, cor='#1f77b4', orientacao='h'):
        """Gera gráfico com matplotlib para o PDF"""
        fig, ax = plt.subplots(figsize=(10, max(6, len(dados) * 0.3)))
        
        if orientacao == 'h':
            ax.barh(dados[coluna_x], dados[coluna_y], color=cor)
            ax.set_xlabel('Valor (R$)')
            ax.set_ylabel(coluna_x)
            
            # Adicionar valores nas barras
            for i, v in enumerate(dados[coluna_y]):
                ax.text(v, i, f' R$ {v:,.0f}', va='center', fontsize=8)
        else:
            ax.bar(dados[coluna_x], dados[coluna_y], color=cor)
            ax.set_ylabel('Valor (R$)')
            ax.set_xlabel(coluna_x)
            plt.xticks(rotation=45, ha='right')
            
        ax.set_title(titulo, fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        
        # Salvar em buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close()
        return buf
    
    def gerar_pdf():
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), 
                               rightMargin=30, leftMargin=30,
                               topMargin=30, bottomMargin=30)
        
        elementos = []
        styles = getSampleStyleSheet()
        
        # Título
        titulo_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f77b4'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        titulo = Paragraph(f"Relatório Real H - {datetime.now().strftime('%d/%m/%Y')}", titulo_style)
        elementos.append(titulo)
        elementos.append(Spacer(1, 20))
        
        # Tabela de Métricas
        metricas_data = [
            ['Métrica', 'Valor'],
            ['Faturamento Total', f'R$ {valor_total:,.2f}'],
            ['Clientes Atendidos', f'{clientes_unicos}'],
            ['Pedidos Únicos', f'{pedidos_unicos}'],
            ['Ticket Médio/Pedido', f'R$ {ticket_medio_pedido:,.2f}'],
            ['Produtos Diferentes', f'{produtos_unicos}'],
            ['Vendedores', f'{vendedores_unicos}']
        ]
        
        tabela = Table(metricas_data, colWidths=[4*inch, 3*inch])
        tabela.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f77b4')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elementos.append(tabela)
        elementos.append(PageBreak())
        
        # Gráfico Top Clientes
        top15_clientes = todos_clientes.head(15)
        img_clientes = gerar_grafico_matplotlib(top15_clientes, col_cliente, col_valor, 
                                                'Top 15 Clientes', '#1f77b4', 'h')
        elementos.append(Image(img_clientes, width=9*inch, height=5*inch))
        elementos.append(PageBreak())
        
        # Gráfico Top Produtos
        top15_produtos = todos_produtos.head(15)
        img_produtos = gerar_grafico_matplotlib(top15_produtos, col_produto, col_valor,
                                               'Top 15 Produtos', '#ff7f0e', 'h')
        elementos.append(Image(img_produtos, width=9*inch, height=5*inch))
        elementos.append(PageBreak())
        
        # Gráfico Vendedores
        img_vendedores = gerar_grafico_matplotlib(todos_vendedores, col_vendedor, col_valor,
                                                 'Faturamento por Vendedor', '#2ca02c', 'h')
        elementos.append(Image(img_vendedores, width=9*inch, height=5*inch))
        elementos.append(PageBreak())
        
        # Gráfico Evolução Temporal
        fig_tempo_mat, ax = plt.subplots(figsize=(10, 5))
        vendas_tempo_pdf = df_filtrado.groupby(df_filtrado[col_data].dt.to_period("M"))[col_valor].sum().reset_index()
        vendas_tempo_pdf[col_data] = vendas_tempo_pdf[col_data].astype(str)
        ax.plot(vendas_tempo_pdf[col_data], vendas_tempo_pdf[col_valor], marker='o', linewidth=2, color='#d62728')
        ax.set_title('Evolução de Vendas ao Longo do Tempo', fontsize=14, fontweight='bold')
        ax.set_xlabel('Mês')
        ax.set_ylabel('Faturamento (R$)')
        ax.grid(alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        buf_tempo = BytesIO()
        plt.savefig(buf_tempo, format='png', dpi=150, bbox_inches='tight')
        buf_tempo.seek(0)
        plt.close()
        elementos.append(Image(buf_tempo, width=9*inch, height=5*inch))
        
        if col_regiao != "Nenhuma":
            elementos.append(PageBreak())
            vendas_regiao_pdf = df_filtrado.groupby(col_regiao)[col_valor].sum().sort_values(ascending=False).reset_index()
            img_regiao = gerar_grafico_matplotlib(vendas_regiao_pdf, col_regiao, col_valor,
                                                 'Faturamento por Região', '#8c564b', 'h')
            elementos.append(Image(img_regiao, width=9*inch, height=5*inch))
        
        doc.build(elementos)
        buffer.seek(0)
        return buffer

    # ==============================
    # BOTÕES DE DOWNLOAD
    # ==============================
    st.markdown("---")
    st.markdown("## 📥 Exportar Dados")
    
    col_download1, col_download2 = st.columns(2)
    
    with col_download1:
        st.download_button(
            "📊 Baixar dados agregados (CSV)",
            data=df_filtrado.to_csv(index=False).encode("utf-8"),
            file_name=f"relatorio_realh_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with col_download2:
        if st.button("📄 Gerar PDF Completo"):
            with st.spinner("Gerando PDF com todos os gráficos..."):
                pdf_buffer = gerar_pdf()
                st.download_button(
                    "📥 Baixar PDF",
                    data=pdf_buffer,
                    file_name=f"relatorio_completo_realh_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf"
                )
                st.success("✅ PDF gerado com sucesso!")

else:
    st.info("👆 Envie uma planilha para começar a gerar relatórios.")