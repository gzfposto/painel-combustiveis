# ⛽ Painel do Mercado de Combustíveis

Painel automático para acompanhar o mercado de combustíveis de um posto
Ipiranga na Serra Gaúcha. Roda **100% na nuvem e de graça**: o GitHub
Actions coleta os dados às **8h e às 18h (Brasília)** e publica uma página
no GitHub Pages, que você abre no celular.

**O que mostra (Fase 1):**

- Brent e WTI (US$/barril): fechamento diário, com histórico salvo
- Dólar PTAX (venda), pela API SGS do Banco Central
- Brent convertido em reais (R$/barril e R$/litro), com médias móveis de 20 e 50 dias
- Variação no dia, na semana e no mês, com setas e cores
- Notícias do Google News (Petrobras, diesel, gasolina, ANP, ICMS...) dos
  últimos 7 dias, sem repetidas
- Planilhas (CSV) com o histórico, para abrir no Excel

---

## Passo a passo da instalação

Leva uns 15 minutos. Você só vai usar o navegador, sem instalar nada.

### 1. Crie uma conta no GitHub

Acesse <https://github.com/signup> e crie uma conta gratuita. Guarde o
nome de usuário, porque ele faz parte do endereço do painel.

### 2. Crie o repositório

O repositório é a "pasta na nuvem" onde ficam o código e os dados.

1. Acesse <https://github.com/new>.
2. **Repository name:** `painel-combustiveis` (ou outro nome, sem espaços).
3. Marque **Public**. O GitHub Pages gratuito só funciona em repositórios
   públicos. Só vão ficar públicos os dados de mercado; nada do seu posto
   vai para lá.
4. Marque **Add a README file**.
5. Clique em **Create repository**.

### 3. Ative o GitHub Pages

1. No repositório, clique em **Settings** (engrenagem, no topo).
2. No menu da esquerda, clique em **Pages**.
3. Em **Build and deployment → Source**, escolha **GitHub Actions**.
   Não precisa salvar, a escolha já vale.

### 4. Libere o robô para salvar o histórico

1. Ainda em **Settings**, no menu da esquerda: **Actions → General**.
2. Role até **Workflow permissions**.
3. Marque **Read and write permissions** e clique em **Save**.

### 5. Envie os arquivos do painel

Atenção: a pasta `.github` começa com ponto, e o Mac esconde esse tipo de
pasta. **No Finder, aperte `Cmd + Shift + .` (ponto)** para mostrar os
arquivos ocultos antes de arrastar.

1. Volte à página inicial do repositório (clique no nome dele no topo).
2. Clique em **Add file → Upload files**.
3. Abra no Finder a pasta deste projeto, selecione **todo o conteúdo dela**
   (`.github`, `painel`, `dados`, `config.yaml`, `requirements.txt`,
   `README.md`, `.gitignore`) e arraste para a página do GitHub.
4. Lá embaixo, clique em **Commit changes**.
5. Confira se o arquivo `.github/workflows/atualizar.yml` apareceu no
   repositório. Se não apareceu, veja a seção *Problemas comuns* abaixo.

### 6. Rode pela primeira vez

O envio dos arquivos já dispara a primeira execução sozinho. Para
acompanhar ou rodar de novo:

1. Clique na aba **Actions**.
2. À esquerda, clique em **Atualizar painel**.
3. Para rodar agora: botão **Run workflow → Run workflow**.
4. Espere a bolinha ficar verde ✅ (2 a 4 minutos). Na primeira vez ele
   baixa 2 anos de histórico.

### 7. Abra o painel

O endereço é:

```
https://SEU-USUARIO.github.io/painel-combustiveis/
```

O link também aparece em **Settings → Pages**. No celular, abra no
navegador e use **Compartilhar → Adicionar à Tela de Início**: ele fica
como um aplicativo.

---

## Uso no dia a dia

- **Atualização:** automática às 8h e às 18h. O GitHub às vezes atrasa
  os agendamentos em 10 a 30 minutos, o que é normal.
- **Ajustes:** abra o `config.yaml` no GitHub, clique no lápis ✏️, edite e
  clique em **Commit changes**. Dá para trocar os termos de busca das
  notícias, quantos dias aparecem nos gráficos, o nome do posto e ligar
  ou desligar módulos. O painel é refeito sozinho em seguida.
- **Histórico:** fica na pasta `dados/` do repositório e também pode ser
  baixado pelos links no rodapé da página.
- **Se uma fonte falhar** (um site fora do ar, por exemplo), o painel não
  para: aparece um aviso amarelo no topo e os outros dados continuam
  sendo atualizados.

### Como ler o painel

- **▲ laranja** = subiu (pressão de **custo** para quem compra combustível).
  **▼ verde** = caiu (alívio).
- **Semana / mês** comparam com o último fechamento de 7 e de 30 dias atrás.
- **Brent em reais** é o Brent em dólar multiplicado pela PTAX do mesmo dia.
  É o número que mais se aproxima da pressão sobre o preço de importação.
- **Médias móveis:** preço **acima** das médias de 20 e 50 dias indica
  tendência de alta; **abaixo**, de baixa. Quando a média de 20 cruza a de
  50, costuma ser uma mudança de tendência.

---

## Problemas comuns

**A pasta `.github` não subiu.** Crie o arquivo pelo próprio site: **Add
file → Create new file**, digite no nome exatamente
`.github/workflows/atualizar.yml` (as barras criam as pastas), cole o
conteúdo do arquivo `atualizar.yml` deste projeto e clique em **Commit
changes**.

**Execução com ❌ vermelho.** Clique na execução e depois no passo com
erro para ver a mensagem. As causas mais comuns:

- *"Permission denied" / erro 403 ao salvar:* faltou o passo 4.
- *Erro em "deploy-pages":* faltou o passo 3 (Source = GitHub Actions).

**O GitHub mandou e-mail dizendo que desativou o agendamento.** Isso
acontece em repositórios sem atividade há 60 dias. Vá em **Actions →
Atualizar painel** e clique em **Enable workflow**.

---

## Como o código está organizado

```
.github/workflows/atualizar.yml   agenda (8h/18h) e publicação no Pages
config.yaml                       configurações (editáveis sem programar)
requirements.txt                  bibliotecas Python usadas
dados/                            histórico em CSV/JSON (gravado pelo robô)
painel/
  main.py                         roda tudo e gera a página
  indicadores.py                  Brent em R$, médias móveis, variações
  armazenamento.py                leitura/gravação do histórico
  fontes/                         um arquivo por fonte de dados
    petroleo.py                   Brent e WTI (Yahoo; reservas: Yahoo direto, FRED)
    ptax.py                       Dólar PTAX (Banco Central, SGS série 1)
    noticias.py                   RSS do Google News
    abicom.py   (Fase 2)          defasagem Abicom (esqueleto)
    anp.py      (Fase 2)          preços semanais ANP por município (esqueleto)
    cepea.py    (Fase 2)          indicadores CEPEA de etanol (esqueleto)
  analises/
    resumo_ia.py (Fase 2)         resumo diário pelo Claude (pronto, desligado)
  templates/
    index.html.j2                 a página
    secoes/_modelo.html.j2        modelo de seção para os módulos novos
```

### Fase 2: como acrescentar os próximos módulos

Cada fonte é um arquivo em `painel/fontes/` com uma função
`coletar(config)`. Os arquivos `abicom.py`, `anp.py` e `cepea.py` já
existem e explicam no topo o que fazer. Para cada um:

1. Implementar `coletar()` (o arquivo tem as instruções e os links).
2. Copiar `templates/secoes/_modelo.html.j2` como
   `templates/secoes/<nome>.html.j2` e ajustar. A seção entra na página
   sozinha.
3. Em `config.yaml`, mudar o módulo para `ativo: true`.

Se um módulo novo der erro, o resto do painel continua funcionando.

**Resumo diário com o Claude:** o código em `painel/analises/resumo_ia.py`
já está pronto. Para ligar:

1. Crie uma chave de API em <https://platform.claude.com> (cobrança por
   uso; cada resumo custa poucos centavos).
2. No GitHub: **Settings → Secrets and variables → Actions → New
   repository secret**. Name: `ANTHROPIC_API_KEY`, Secret: a chave.
3. Em `requirements.txt`, apague o `#` da linha `# anthropic>=1.0`.
4. Em `config.yaml`, mude `resumo_ia: ativo:` para `true`.

O resumo aparece no topo da página, com base nos indicadores e nas
manchetes do dia.

### Rodar no próprio computador (opcional)

```bash
pip install -r requirements.txt
python -m painel.main
```

A página é gerada em `site/index.html`.
