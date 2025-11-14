"""
EXPLICAÇÃO COMPLETA: Como Gráficos Funcionam com Templates

Pergunta: "Se colocar {{GRAFICO}}, o Python entende e coloca a imagem?"

Resposta: SIM! Mas funciona diferente de texto. Vou explicar.
"""

# ============================================================================
# PARTE 1: DIFERENÇA ENTRE TEXTO E GRÁFICOS
# ============================================================================

"""
╔═════════════════════════════════════════════════════════════════════╗
║                     TEXTO vs GRÁFICOS                               ║
╚═════════════════════════════════════════════════════════════════════╝

TEXTO - {{TITULO}}
──────────────────
Você escreve:   "Relatório {{TITULO}}"
Python substitui: "Relatório Vendas"
                  ↑ (texto simples)

É super simples! Python literalmente substitui o texto.


GRÁFICO - {{GRAFICO}}
──────────────────────
Você escreve:   "[{{GRAFICO}}]" ou apenas "{{GRAFICO}}"
Python faz:     
  1. Pega o gráfico Plotly que você criou
  2. Converte para IMAGEM (PNG)
  3. Remove o texto {{GRAFICO}}
  4. Insere a imagem no lugar
  
Resultado: Uma imagem bonita do gráfico no slide! 📊

É mais complexo porque envolve:
  ✓ Converter Plotly → PNG
  ✓ Remover placeholder de texto
  ✓ Inserir imagem
  ✓ Limpar arquivo temporário
"""

# ============================================================================
# PARTE 2: COMO FUNCIONA NA PRÁTICA
# ============================================================================

"""
FLUXO PASSO-A-PASSO:
═══════════════════

1. VOCÊ CRIA NO POWERPOINT:
   ┌──────────────────────────────┐
   │ Gráfico: {{NOME_GRAFICO}}   │
   │                              │
   │ [{{GRAFICO}}]               │
   └──────────────────────────────┘

2. VOCÊ EXECUTA O PYTHON:
   pptx_bytes = preencher_template_pptx(
       caminho_template='template.pptx',
       titulo="Vendas",
       metricas_dict={...},
       graficos_dict={
           "Top Clientes": fig_clientes,  # ← Plotly Figure
           "Top Produtos": fig_produtos   # ← Plotly Figure
       }
   )

3. PYTHON PROCESSA:
   a) Lê o arquivo PPTX
   b) Encontra "{{NOME_GRAFICO}}" → substitui por "Top Clientes"
   c) Encontra "{{GRAFICO}}" → VAI FAZER COISA DIFERENTE!
   
   d) Para cada gráfico em graficos_dict:
      • Converte fig_clientes para PNG temporário
      • Acha o placeholder {{GRAFICO}} no slide
      • REMOVE o texto {{GRAFICO}}
      • INSERE a imagem PNG
      • Deleta arquivo temporário

4. RESULTADO FINAL:
   ┌──────────────────────────────┐
   │ Gráfico: Top Clientes       │
   │                              │
   │ [IMAGEM DO GRÁFICO AQUI]    │
   │ (linda, colorida, completa) │
   └──────────────────────────────┘

5. VOCÊ BAIXA:
   ✅ Relatório pronto com gráfico inserido!
"""

# ============================================================================
# PARTE 3: EXEMPLOS DE CÓDIGO
# ============================================================================

"""
EXEMPLO 1: USANDO GRÁFICO NO TEMPLATE
──────────────────────────────────────

No PowerPoint você escreve:
┌─────────────────────────────────────┐
│ 📊 TOP 10 CLIENTES                  │
│                                      │
│ Período: {{PERIODO}}                │
│                                      │
│ [{{GRAFICO}}]                       │
│                                      │
│ Relatório confidencial              │
└─────────────────────────────────────┘


No Python você faz:
"""

import plotly.graph_objects as go
import pandas as pd
from utils_template import preencher_template_pptx

# Criar dados
dados = {
    'Cliente': ['A', 'B', 'C', 'D', 'E'],
    'Valor': [5000, 4000, 3000, 2000, 1000]
}
df = pd.DataFrame(dados)

# Criar GRÁFICO PLOTLY (super importante!)
fig_grafico = go.Figure()
fig_grafico.add_trace(go.Bar(
    x=df['Cliente'],
    y=df['Valor'],
    marker_color='#00CC96'
))
fig_grafico.update_layout(
    title='Top Clientes',
    height=500
)

# PREENCHER TEMPLATE COM O GRÁFICO
resultado = preencher_template_pptx(
    caminho_template='template_relatorio.pptx',
    titulo='Vendas Real H',
    periodo='Nov 2024',
    metricas_dict={'Total': 'R$ 15.000'},
    graficos_dict={
        'grafico_clientes': fig_grafico  # ← Aqui entra o Plotly!
    }
)

# Salvar
with open('relatorio_com_grafico.pptx', 'wb') as f:
    f.write(resultado)

print("✅ Relatório com gráfico gerado!")

"""
RESULTADO:
──────────
No PowerPoint final:
  • "Período: Nov 2024" (texto substituído)
  • Imagem do gráfico no lugar do [{{GRAFICO}}]
  • Tudo pronto pra apresentar!
"""


# ============================================================================
# PARTE 4: COMO FUNCIONA A CONVERSÃO
# ============================================================================

"""
O PROCESSO INTERNO DE CONVERSÃO:
═════════════════════════════════

Seu código:
  graficos_dict = {
      '📊 Top Clientes': fig_plotly  # ← Plotly Figure object
  }

Python internamente faz:
  
  1. RECEBE O PLOTLY:
     fig_plotly = <Figure object>
     └─ Tipo: plotly.graph_objects.Figure
     └─ É um objeto com dados e estilo
  
  2. CONVERTE PARA PNG:
     import plotly.io as pio
     pio.write_image(fig_plotly, 'temp_grafico.png')
     └─ Usa "kaleido" (que precisa do Chrome)
     └─ Cria arquivo PNG temporário
     └─ Qualidade: 1200x700 pixels (bonita!)
  
  3. INSERE NO POWERPOINT:
     slide.shapes.add_picture('temp_grafico.png', ...)
     └─ Acha o placeholder {{GRAFICO}}
     └─ Remove o texto
     └─ Insere a imagem PNG
     └─ Posiciona no slide
  
  4. LIMPA LIXO:
     os.remove('temp_grafico.png')
     └─ Apaga arquivo temporário
     └─ Libera espaço do disco

RESULTADO FINAL:
  ✓ Um slide com o gráfico bonitão!
"""

# ============================================================================
# PARTE 5: LIMITAÇÕES E SOLUÇÕES
# ============================================================================

"""
LIMITAÇÃO 1: Um Gráfico por Slide
──────────────────────────────────

❌ Não funciona:
  [{{GRAFICO}}] [{{GRAFICO}}]  (dois gráficos no mesmo slide)

✅ Solução: Use vários slides
  Slide 1: [{{GRAFICO}}]
  Slide 2: [{{GRAFICO}}]

O Python vai substituir cada um em seu slide.


LIMITAÇÃO 2: Placeholder Deve Estar Sozinho
────────────────────────────────────────────

❌ Não funciona bem:
  "Veja aqui o gráfico: {{GRAFICO}} muito bom!"

✅ Melhor:
  "Veja aqui o gráfico:"
  [{{GRAFICO}}]
  "Muito impressionante, não?"

Porque Python remove TODO o parágrafo com {{GRAFICO}}.


LIMITAÇÃO 3: Só Funciona com Plotly
────────────────────────────────────

✅ Funciona:
  fig = go.Figure()  # Plotly
  fig.add_trace(...)

❌ Não funciona:
  plt.plot()  # Matplotlib direto
  
✅ Se quiser Matplotlib:
  1. Salve como PNG: plt.savefig('grafico.png')
  2. Depois insira manualmente no PowerPoint
  
  OU
  
  1. Converta Matplotlib para Plotly
  2. Use Plotly no template


LIMITAÇÃO 4: Precisa do Chrome Instalado
──────────────────────────────────────────

O kaleido (que converte Plotly em PNG) precisa do Chrome.
No seu sistema JÁ instalamos, então está tudo OK!

Se der erro de Chrome:
  from kaleido import get_chrome_sync
  get_chrome_sync()  # Instala automático
"""

# ============================================================================
# PARTE 6: EXEMPLOS COMPLETOS
# ============================================================================

"""
EXEMPLO 2: MÚLTIPLOS GRÁFICOS
─────────────────────────────

Python:
  graficos_dict = {
      '📊 Top Clientes': fig1,
      '📊 Top Produtos': fig2,
      '📊 Top Vendedores': fig3
  }

PowerPoint precisa ter:
  Slide 1: [{{GRAFICO}}]  ← Vai receber fig1
  Slide 2: [{{GRAFICO}}]  ← Vai receber fig2
  Slide 3: [{{GRAFICO}}]  ← Vai receber fig3

Python vai substituir um por um!


EXEMPLO 3: GRÁFICO + TABELA NO MESMO SLIDE
───────────────────────────────────────────

PowerPoint:
┌────────────────────────────────────────┐
│ TOP 10 CLIENTES - {{PERIODO}}          │
├────────────────────────────────────────┤
│ Gráfico:          │ Tabela:            │
│                   │                    │
│ [{{GRAFICO}}]     │ {{TABELA}}         │
│                   │                    │
└────────────────────────────────────────┘

Python:
  graficos_dict = {'top_clientes': fig}
  # Mas {{TABELA}} é substituído como texto!
  
Resultado:
  • Gráfico aparece do lado esquerdo
  • Tabela (em texto) aparece do lado direito
  • Fica assim: GRÁFICO | TABELA


EXEMPLO 4: GRÁFICO COM TÍTULO DINÂMICO
───────────────────────────────────────

PowerPoint:
┌────────────────────────────────────────┐
│ GRÁFICO: {{NOME_GRAFICO}}              │
│                                        │
│ [{{GRAFICO}}]                          │
│                                        │
│ Período: {{PERIODO}}                   │
└────────────────────────────────────────┘

Python:
  graficos_dict = {'top_clientes': fig}
  # {{NOME_GRAFICO}} substituído como texto
  # [{{GRAFICO}}] substituído por imagem

Resultado:
  • Título dinâmico
  • Gráfico em alta qualidade
  • Tudo automático!
"""

# ============================================================================
# PARTE 7: RESUMO RÁPIDO
# ============================================================================

"""
╔════════════════════════════════════════════════════════════════════╗
║         GRÁFICOS EM TEMPLATES - RESUMO RÁPIDO                      ║
╚════════════════════════════════════════════════════════════════════╝

PERGUNTA: "Se colocar {{GRAFICO}}, funciona?"

RESPOSTA: SIM! Mas assim:

1. VOCÊ CRIA NO POWERPOINT:
   [{{GRAFICO}}]

2. VOCÊ PASSA PARA O PYTHON:
   graficos_dict = {
       'meu_grafico': fig_plotly
   }
   
   preencher_template_pptx(
       template='arquivo.pptx',
       graficos_dict=graficos_dict
   )

3. PYTHON FAZ A MÁGICA:
   • Converte Plotly → PNG
   • Remove {{GRAFICO}}
   • Insere imagem PNG
   • Limpa arquivos temporários

4. VOCÊ RECEBE:
   ✅ Relatório com gráfico bonito pronto!

═════════════════════════════════════════════════════════════════════

DIFERENÇA:
──────────

{{TITULO}}  → Substitui por TEXTO
{{GRAFICO}} → Substitui por IMAGEM

═════════════════════════════════════════════════════════════════════

REQUISITOS:
───────────
✓ Arquivo template.pptx com [{{GRAFICO}}]
✓ Variável graficos_dict com Plotly figures
✓ Chrome instalado (já tem no seu sistema)
✓ Arquivo kaleido (já instalou)

═════════════════════════════════════════════════════════════════════

RESULTADO FINAL:
────────────────
Um relatório PPTX profissional com:
  ✓ Textos preenchidos
  ✓ Gráficos em alta qualidade
  ✓ Design customizado
  ✓ Pronto para baixar! 🎉
"""

print(__doc__)
