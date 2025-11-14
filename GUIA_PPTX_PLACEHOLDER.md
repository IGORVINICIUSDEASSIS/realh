╔════════════════════════════════════════════════════════════════════════════╗
║                   GUIA COMPLETO: PPTX COM PLACEHOLDER                      ║
║                     Tutorial em Português - 100% Prático                   ║
╚════════════════════════════════════════════════════════════════════════════╝

📚 ÍNDICE:
────────────────────────────────────────────────────────────────────────────
1. O que é placeholder?
2. Como criar no PowerPoint
3. Como o Python funciona
4. Placeholders disponíveis
5. Passo-a-passo prático
6. Dicas e truques
7. Erros comuns
8. Arquivos do projeto


════════════════════════════════════════════════════════════════════════════
1️⃣ O QUE É PLACEHOLDER?
════════════════════════════════════════════════════════════════════════════

Um placeholder é um "espaço reservado" que você coloca no PowerPoint.
Quando o Python executa, ele SUBSTITUI esse espaço pelo valor real.

ANALOGIA:
────────
É como um formulário de carta:

  Carta tradicional:
  ┌─────────────────────────────────────┐
  │ Olá [NOME],                         │
  │ Bem-vindo em [DIA] de [MÊS]!        │
  └─────────────────────────────────────┘

  No PowerPoint:
  ┌─────────────────────────────────────┐
  │ Relatório {{TITULO}} - {{PERIODO}}  │
  └─────────────────────────────────────┘

  Depois Python substitui:
  ┌─────────────────────────────────────┐
  │ Relatório Vendas - Novembro 2024    │
  └─────────────────────────────────────┘

RESULTADO: Você cria UMA VEZ e usa várias vezes! 🎉


════════════════════════════════════════════════════════════════════════════
2️⃣ COMO CRIAR NO POWERPOINT
════════════════════════════════════════════════════════════════════════════

MÉTODO 1: POWERPOINT DESKTOP (Windows/Mac)
───────────────────────────────────────────

Passo 1: Abrir PowerPoint
  • Clique no botão Windows
  • Procure por "PowerPoint"
  • Abra PowerPoint
  • Clique em "Apresentação em Branco"

Passo 2: Inserir Caixa de Texto
  • No menu superior, clique em "INSERIR"
  • Procure por "Caixa de Texto"
  • Clique em "Caixa de Texto"
  • No slide, clique e arraste para desenhar uma caixa

Passo 3: Digitar Placeholder
  • Dentro da caixa de texto, digite:
    {{TITULO}}
  
  ⚠️ IMPORTANTE: Escreva EXATAMENTE assim:
     - Duas chaves de abertura: {{
     - Texto em MAIÚSCULA: TITULO
     - Duas chaves de fechamento: }}

Passo 4: Formatar (Opcional)
  • Selecione o texto
  • Use a barra de formatação para:
    - Aumentar fonte: selecione e ajuste tamanho
    - Mudar cor: selecione e escolha cor
    - Mudar alinhamento: centro, esquerda, direita
    - Deixar negrito: Ctrl+N

Passo 5: Salvar
  • Ctrl+S ou Arquivo → Salvar
  • Nome: template_relatorio.pptx
  • Formato: PowerPoint (*.pptx)
  • Pasta: /workspaces/realh/


MÉTODO 2: OFFICE 365 ONLINE
────────────────────────────

Passo 1: Acessar
  • Abra office.com no navegador
  • Faça login com sua conta Microsoft
  • Clique em "PowerPoint"
  • Clique em "Apresentação em Branco"

Passo 2: Inserir Caixa de Texto
  • Menu superior → Inserir
  • Clique em "Caixa de Texto"
  • Desenhe no slide

Passo 3-4: Igual ao método 1
  • Digitar {{TITULO}}
  • Formatar como quiser

Passo 5: Baixar
  • Arquivo → Baixar como → PowerPoint (*.pptx)
  • Mova para: /workspaces/realh/


════════════════════════════════════════════════════════════════════════════
3️⃣ COMO O PYTHON FUNCIONA
════════════════════════════════════════════════════════════════════════════

O Python executa estes passos automaticamente:

┌─ PASSO 1: ABRIR ─────────────────────────────────────────────────────────┐
│                                                                             │
│  prs = Presentation('template_relatorio.pptx')                           │
│                                                                             │
│  Python abre seu arquivo PPTX e carrega na memória                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─ PASSO 2: PERCORRER SLIDES ──────────────────────────────────────────────┐
│                                                                             │
│  for slide in prs.slides:                                                │
│      print(f"Slide {slide_numero}")                                       │
│                                                                             │
│  Python examina CADA slide um por um                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─ PASSO 3: PERCORRER FORMAS ──────────────────────────────────────────────┐
│                                                                             │
│  for shape in slide.shapes:                                              │
│      print(f"Forma: {shape.name}")                                        │
│                                                                             │
│  Python examina CADA caixa de texto do slide                             │
│  (Formas podem ser: caixas de texto, imagens, tabelas, etc)             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─ PASSO 4: VERIFICAR SE É CAIXA DE TEXTO ────────────────────────────────┐
│                                                                             │
│  if hasattr(shape, 'text_frame'):                                        │
│      print("É uma caixa de texto!")                                      │
│                                                                             │
│  Python verifica se a forma tem texto                                     │
│  (Nem todas as formas têm texto - imagens não têm)                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─ PASSO 5: PERCORRER PARÁGRAFOS ──────────────────────────────────────────┐
│                                                                             │
│  for paragraph in shape.text_frame.paragraphs:                           │
│      print(f"Parágrafo: {paragraph.text}")                                │
│                                                                             │
│  Cada caixa de texto pode ter vários parágrafos                          │
│  Python vai um por um                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─ PASSO 6: PERCORRER "RUNS" (PEDAÇOS DE TEXTO) ──────────────────────────┐
│                                                                             │
│  for run in paragraph.runs:                                              │
│      print(f"Texto: {run.text}")                                          │
│                                                                             │
│  Cada parágrafo pode ter vários "runs"                                   │
│  Um "run" é um pedaço de texto com mesma formatação                      │
│                                                                             │
│  Exemplo:                                                                  │
│  ┌──────────────────────────────────┐                                    │
│  │ Relatório {{TITULO}} - {{DATA}}   │                                   │
│  └──────────────────────────────────┘                                    │
│      ^1^          ^2^      ^3^                                            │
│      Run 1: "Relatório "                                                  │
│      Run 2: "{{TITULO}} - " (pode estar em negrito)                      │
│      Run 3: "{{DATA}}"                                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─ PASSO 7: PROCURAR PLACEHOLDER ──────────────────────────────────────────┐
│                                                                             │
│  if '{{TITULO}}' in run.text:                                            │
│      print("Encontrei um placeholder!")                                   │
│                                                                             │
│  Python procura por {{TITULO}} dentro do texto                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─ PASSO 8: SUBSTITUIR ────────────────────────────────────────────────────┐
│                                                                             │
│  run.text = run.text.replace('{{TITULO}}', 'Vendas Real H')             │
│                                                                             │
│  Python REMOVE {{TITULO}} e COLOCA o valor real no lugar                │
│                                                                             │
│  ANTES:  run.text = "Relatório {{TITULO}} de Nov"                       │
│  DEPOIS: run.text = "Relatório Vendas Real H de Nov"                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─ PASSO 9: SALVAR ────────────────────────────────────────────────────────┐
│                                                                             │
│  prs.save('relatorio_preenchido.pptx')                                   │
│                                                                             │
│  Python salva o arquivo novo com tudo substituído                        │
│  Agora você tem um relatório pronto para baixar!                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

RESULTADO: ✅ Seu relatório está pronto!


════════════════════════════════════════════════════════════════════════════
4️⃣ PLACEHOLDERS DISPONÍVEIS NO SEU SISTEMA
════════════════════════════════════════════════════════════════════════════

{{TITULO}}
──────────
Substitui: Pelo título do relatório
Exemplo: "Relatório de Vendas - Real H"
Use em: Capa, cabeçalho

No PowerPoint: "Relatório {{TITULO}} - Período {{PERIODO}}"
Resultado:     "Relatório de Vendas - Real H - Período Nov 2024"


{{PERIODO}}
───────────
Substitui: Pelo período selecionado
Exemplo: "Novembro/2024" ou "Nov 2024"
Use em: Capa, cabeçalho, rodapé

No PowerPoint: "Período: {{PERIODO}}"
Resultado:     "Período: Novembro/2024"


{{METRICAS}}
────────────
Substitui: Por uma lista de métricas
Exemplo: "• Vendas Totais: R$ 1.500.000
          • Clientes: 500
          • Produtos: 150"
Use em: Slide de resumo/métricas

No PowerPoint: "{{METRICAS}}"
Resultado:     (A lista completa aparece aqui)


{{GRAFICO}}
───────────
Substitui: Por uma imagem do gráfico (PNG)
Exemplo: Uma imagem do gráfico de barras
Use em: Slides de visualização

ESPECIAL: Quando você usa {{GRAFICO}}, Python:
  1. REMOVE o placeholder de texto
  2. INSERE a imagem no lugar
  3. A imagem fica do tamanho do slide!

No PowerPoint: "[{{GRAFICO}}]"
Resultado:     Uma imagem bonita do seu gráfico!


{{NOME_GRAFICO}}
────────────────
Substitui: Pelo nome do gráfico
Exemplo: "Top 10 Clientes", "Evolução de Vendas"
Use em: Título acima do gráfico

No PowerPoint: "Gráfico: {{NOME_GRAFICO}}"
Resultado:     "Gráfico: Top 10 Clientes"


════════════════════════════════════════════════════════════════════════════
5️⃣ PASSO-A-PASSO PRÁTICO COMPLETO
════════════════════════════════════════════════════════════════════════════

🎯 OBJETIVO: Criar um template customizado para seus relatórios

TEMPO ESTIMADO: 10 minutos


ETAPA 1: GERAR TEMPLATE BASE (Python)
──────────────────────────────────────

No seu sistema já existe:
  /workspaces/realh/template_relatorio.pptx

Este arquivo foi gerado automaticamente com:
  ✓ Capa com logo
  ✓ Slide de métricas
  ✓ Slide de gráficos
  ✓ Placeholders já inseridos

Você pode começar a editar ESSE arquivo!


ETAPA 2: ABRIR NO POWERPOINT
────────────────────────────

Opção A: Se você tem PowerPoint instalado
  1. Clique com botão direito em template_relatorio.pptx
  2. Escolha "Abrir com" → "PowerPoint"
  3. Espere abrir (pode demorar um pouco)

Opção B: Se usa Office 365 Online
  1. Vá para office.com
  2. Clique em "Abrir" ou "Carregar"
  3. Procure por template_relatorio.pptx
  4. Abra-o

Opção C: Se não tem PowerPoint
  1. Use LibreOffice Impress (gratuito)
  2. Ou use Google Slides (online gratuito)
  3. Abra o arquivo - ambos suportam PPTX


ETAPA 3: EXPLORAR O TEMPLATE
────────────────────────────

Quando abrir, você verá:

  SLIDE 1: Capa
  ├─ Logo no topo
  ├─ Texto: "{{TITULO}}"
  └─ Texto: "Período: {{PERIODO}}"

  SLIDE 2: Métricas
  ├─ Logo no canto
  ├─ Título: "📊 Métricas Principais"
  └─ Caixa grande: "{{METRICAS}}"

  SLIDE 3: Gráfico
  ├─ Logo no canto
  ├─ Título: "📊 Gráfico - {{NOME_GRAFICO}}"
  └─ Placeholder: "[{{GRAFICO}}]"

Todos os placeholders já estão prontos!


ETAPA 4: CUSTOMIZAR (A PARTE LEGAL!)
────────────────────────────────────

Agora você pode deixar do seu jeito:

EXEMPLO DE CUSTOMIZAÇÃO:

  ┌─ CAPA ────────────────────────────────────┐
  │ [LOGO GRANDE AQUI]                       │
  │                                            │
  │ Relatório {{TITULO}}                     │
  │ {{PERIODO}}                              │
  │                                            │
  │ EMPRESA: Real H                          │
  │ Preparado em: [DATA de hoje]            │
  └────────────────────────────────────────────┘

  Dicas para customizar:
  • Aumente a logo (mais profissional)
  • Mude as cores para suas cores
  • Adicione rodapé com "Confidencial" ou "Real H"
  • Adicione números de página (Inserir → Números)
  • Mude fontes (Arial, Calibri, etc)
  • Deixe tudo "seu estilo"

  ⚠️ IMPORTANTE: Não apague os {{PLACEHOLDERS}}!
     Eles precisam estar lá para o Python encontrar!


ETAPA 5: TESTAR PLACEHOLDER
──────────────────────────

Antes de salvar, verifique:

  ✓ {{TITULO}} está visível?
  ✓ {{PERIODO}} está visível?
  ✓ {{METRICAS}} está visível?
  ✓ {{GRAFICO}} está visível?
  ✓ Nenhum foi deletado por acaso?

Se tudo OK, prossiga para ETAPA 6.


ETAPA 6: SALVAR
───────────────

Windows/Mac:
  1. Ctrl+S ou Arquivo → Salvar Como
  2. Nome: template_relatorio_customizado.pptx
  3. Formato: PowerPoint (*.pptx) - IMPORTANTE!
  4. Pasta: Mesma do projeto (onde está app.py)

Online (office.com):
  1. Arquivo → Baixar como → PowerPoint
  2. Salve com nome: template_relatorio_customizado.pptx
  3. Mova para: /workspaces/realh/

Google Slides:
  1. Arquivo → Download → Microsoft PowerPoint
  2. Nomeie: template_relatorio_customizado.pptx
  3. Mova para a pasta do projeto


ETAPA 7: VOLTAR AO APP E USAR
──────────────────────────────

1. Abra o app em http://localhost:8501
2. Vá para: 📄 Relatório
3. Escolha: "📋 Usar Template Customizado"
4. Selecione: template_relatorio_customizado.pptx
5. Configure os dados (período, métricas, gráficos)
6. Clique: "🎯 Gerar Relatório com Template"
7. Espere gerar
8. Baixe: "⬇️ Baixar Apresentação"

PRONTO! 🎉

Seu relatório vai estar:
  ✓ Com seu design customizado
  ✓ Com os dados reais preenchidos
  ✓ Pronto para apresentar ou enviar!


════════════════════════════════════════════════════════════════════════════
6️⃣ DICAS E TRUQUES
════════════════════════════════════════════════════════════════════════════

DICA 1: Copiar Formato Usando Template
───────────────────────────────────────
Se você tem um design que gosta em outro PPTX:

  1. Abra seu PPTX bonito no PowerPoint
  2. Copie um slide (Ctrl+C)
  3. Abra template_relatorio_customizado.pptx
  4. Cole o slide (Ctrl+V)
  5. Delete o slide original
  6. Ajuste os placeholders no novo slide
  7. Salve!


DICA 2: Múltiplos Templates
────────────────────────────
Você pode criar vários templates!

  template_relatorio_simples.pptx (minimalista)
  template_relatorio_colorido.pptx (alegre)
  template_relatorio_formal.pptx (corporativo)

Na hora de gerar, escolha qual quer usar!


DICA 3: Reutilizar Layout
──────────────────────────
Se você quer que vários slides tenham o mesmo layout:

  1. Crie um slide com o design que gosta
  2. Clique com botão direito
  3. Escolha "Layout de Slide"
  4. Escolha "Blank" ou customize
  5. Quando adicionar novo slide, mantenha o mesmo design


DICA 4: Temas do PowerPoint
───────────────────────────
PowerPoint tem temas prontos muito bonitos:

  1. Clique em "Design" no menu
  2. Escolha um tema que gosta
  3. Todos os slides mudam de uma vez!
  4. Depois customize com suas cores


DICA 5: Adicionar Rodapé
───────────────────────
Deixa bem profissional:

  1. Insira → Rodapé
  2. Escreva: "© Real H - Confidencial"
  3. Marque "Aplicar a todos os slides"
  4. Pronto!


DICA 6: Numeração de Slides
────────────────────────────
Para slides aparecerem numerados:

  1. Inserir → Número de Slide
  2. Escolha posição (canto, centro, etc)
  3. Marque "Aplicar a todos"


DICA 7: Animar Objetos
──────────────────────
Se quiser deixar mais dinâmico:

  1. Selecione um objeto (texto, imagem)
  2. Clique em "Animações"
  3. Escolha uma animação (Aparecer, Deslizar, etc)
  4. Configure o tempo


════════════════════════════════════════════════════════════════════════════
7️⃣ ERROS COMUNS (E COMO EVITAR)
════════════════════════════════════════════════════════════════════════════

❌ ERRO 1: Placeholder com Espaço
─────────────────────────────────

Errado:  {{ TITULO }}  (com espaços)
Certo:   {{TITULO}}    (sem espaços)

Python procura EXATAMENTE por "{{TITULO}}"
Com espaço, não encontra!

DICA: Sempre digite sem espaço entre as chaves!


❌ ERRO 2: Misturar Maiúsculas/Minúsculas
────────────────────────────────────────

Errado:  {{titulo}}  ou  {{Titulo}}
Certo:   {{TITULO}}

Python é sensível a maiúsculas.
Se escrever diferente, não substitui!

DICA: Sempre use TUDO em MAIÚSCULA


❌ ERRO 3: Deletar Placeholder Sem Querer
──────────────────────────────────────────

Ao editar o PowerPoint, pode deletar o {{TITULO}} acidentalmente.

SOLUÇÃO:
  1. Pressione Ctrl+Z para desfazer
  2. Ou reescreva o placeholder
  3. Tenha cuidado ao deletar outros textos!


❌ ERRO 4: Salvar no Formato Errado
───────────────────────────────────

Errado: .pptm (com macros)
Errado: .ppt  (versão antiga)
Errado: .odp  (OpenOffice)
Certo:  .pptx (PowerPoint moderno)

DICA: Sempre salve como .pptx!


❌ ERRO 5: Colocar Placeholder Fora de Alcance
───────────────────────────────────────────────

Se você colocar {{TITULO}} em:
  ❌ Slide Master (background)
  ❌ Espaço de marcador (que não é caixa)
  ❌ Dentro de smart art

Python pode não encontrar!

DICA: Sempre use caixas de texto normais (Inserir → Caixa de Texto)


❌ ERRO 6: Placeholder Incompleto
─────────────────────────────────

Errado: {{TITULO (faltou fechar)
Errado: TITULO}} (faltou abrir)
Certo:  {{TITULO}}

DICA: Sempre verifique as duplas de chaves!


❌ ERRO 7: Arquivo PPTX Corrompido
──────────────────────────────────

Se o PowerPoint disser "Arquivo corrompido":

  1. Tente abrir com LibreOffice Impress
  2. Se abrir, salve como NOVO arquivo
  3. Se não abrir, use o template_relatorio.pptx novamente
  4. Não salve no meio de edição!


║ LEMBRETE: Antes de salvar, sempre:
║   ✓ Verifique os placeholders {{ESTÃO INTACTOS}}
║   ✓ Salve como .pptx
║   ✓ Teste antes de usar em produção
╚════════════════════════════════════════════════════════════════════════════


════════════════════════════════════════════════════════════════════════════
8️⃣ ARQUIVOS DO PROJETO
════════════════════════════════════════════════════════════════════════════

Aqui estão os arquivos que você precisa conhecer:

📁 /workspaces/realh/
├── template_relatorio.pptx              ← Template padrão (Python criou)
├── template_relatorio_customizado.pptx  ← Sua customização (você cria)
├── utils_template.py                    ← Funções de template
├── pages/
│   ├── 8_📄_Relatório.py               ← Interface para gerar
│   └── 9_⚙️_Configurações_Relatório.py ← Configurações e guias
└── TUTORIAL_PPTX_COM_PLACEHOLDER.py    ← Este arquivo!


📄 template_relatorio.pptx
──────────────────────────
O que é: Template automático gerado pelo Python
Para quê: Base pronta com placeholders
Como usar: Abra no PowerPoint → customize → salve como customizado

Conteúdo:
  • Slide 1: Capa com {{TITULO}} e {{PERIODO}}
  • Slide 2: Métricas com {{METRICAS}}
  • Slide 3: Gráfico com {{GRAFICO}}
  • Todas as caixas já têm placeholders inseridos


📄 template_relatorio_customizado.pptx
───────────────────────────────────────
O que é: Sua versão personalizada
Para quê: Usar como base para os relatórios
Como criar: Copie e customize template_relatorio.pptx

Este arquivo:
  ✓ Fica em /workspaces/realh/
  ✓ Você cria no PowerPoint
  ✓ O Python automaticamente procura por este nome
  ✓ Se não encontrar, oferece opção de upload


📄 utils_template.py
──────────────────
O que é: Código Python que faz a mágica acontecer
Para quê: Funções para ler e preencher templates

Funções principais:
  • gerar_template_padrao() - Cria template novo
  • preencher_template_pptx() - Substitui placeholders


📄 pages/8_📄_Relatório.py
─────────────────────────
O que é: Página onde você gera relatórios
Para quê: Interface visual para usuário
Funcionalidades:
  • Escolher entre Opção A (do zero) ou B (template)
  • Se template: Selecionar arquivo
  • Se template: Fazer upload também
  • Gerar e baixar relatório


📄 pages/9_⚙️_Configurações_Relatório.py
────────────────────────────────────────
O que é: Página de configurações e tutorial
Para quê: Gerenciar e entender templates
Conteúdo:
  • Botão para criar novo template
  • Tutorial visual
  • Comparação de opções
  • Informações técnicas


════════════════════════════════════════════════════════════════════════════
🎯 RESUMO FINAL: O QUE FAZER AGORA
════════════════════════════════════════════════════════════════════════════

PASSO 1: Abrir template base
  └─ Arquivo: /workspaces/realh/template_relatorio.pptx
     Ação: Abra no PowerPoint

PASSO 2: Customizar design
  └─ Mude cores, fontes, adicione logo
     ⚠️ Não apague os {{PLACEHOLDERS}}!

PASSO 3: Salvar customizado
  └─ Nome: template_relatorio_customizado.pptx
     Local: Mesma pasta (/workspaces/realh/)
     Formato: .pptx

PASSO 4: Usar no app
  └─ Vá em 📄 Relatório
     Escolha "📋 Usar Template"
     Selecione seu arquivo customizado

PASSO 5: Gerar relatório
  └─ Configure os dados
     Clique "Gerar"
     Baixe seu relatório pronto! 🎉

════════════════════════════════════════════════════════════════════════════

✨ PARABÉNS! Agora você sabe criar PPTX com placeholders! ✨

Qualquer dúvida, releia este documento ou acesse:
  • Tutorial visual no app (⚙️ Configurações)
  • Arquivo Python (TUTORIAL_PPTX_COM_PLACEHOLDER.py)
  • Comunidade: Stack Overflow, Reddit, etc

BOM TRABALHO! 🚀
