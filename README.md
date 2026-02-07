# 👮‍♂️ BOT DE ESCALA MILITAR - GUIA COMPLETO

> **Bot do Telegram para ler PDFs de escalas militares e notificar policiais automaticamente.**

---

## 📋 SUMARIO

1. [O que este bot faz?](#o-que-este-bot-faz)
2. [Passo 1: Configuracao no Telegram](#passo-1-configuracao-no-telegram)
3. [Passo 2: Preparacao no GitHub](#passo-2-preparacao-no-github)
4. [Passo 3: Deploy no Render.com](#passo-3-deploy-no-rendercom)
5. [Passo 4: Como Usar o Bot](#passo-4-como-usar-o-bot)
6. [Solucao de Problemas](#solucao-de-problemas)

---

## O que este bot faz?

Este bot automatiza o processo de notificacao de escalas militares:

1. 📄 **Le PDFs** enviados a um canal do Telegram
2. 🔍 **Identifica nomes** de policiais na escala
3. 📨 **Envia mensagem privada** para cada policial escalado
4. ✅ **Botao de confirmacao** para registrar ciencia

**Fluxo de funcionamento:**
```
PDF no Canal → Bot le → Extrai nomes → Envia mensagem privada → Policial confirma
```

---

## PASSO 1: Configuracao no Telegram

### 1.1 Criar o Bot no @BotFather

O **@BotFather** eh o "pai" de todos os bots do Telegram. Vamos criar seu bot la:

1. **Abra o Telegram** no seu celular ou computador
2. **Busque por:** `@BotFather`
3. **Inicie uma conversa** clicando em "Iniciar" ou enviando `/start`
4. **Envie o comando:** `/newbot`
5. **Escolha um nome** para o bot (ex: "Bot Escala PM")
6. **Escolha um username** (deve terminar em "bot", ex: "escala_pm_bot")

✅ **Pronto!** O BotFather vai te enviar uma mensagem como esta:

```
Done! Congratulations on your new bot.
Use this token to access the HTTP API:
123456789:ABCdefGHIjklMNOpqrSTUvwxyz
```

**GUARDE ESTE TOKEN!** Ele eh a "senha" do seu bot. 

💾 **Salve em um arquivo de texto** ou anote no caderno. Voce vai precisar dele no Passo 3.

---

### 1.2 Descobrir o ID do Canal

O bot precisa saber qual canal vai monitorar para novas escalas.

#### Opcao A: Canal Publico (mais facil)

Se o canal for **publico** (tem um link como `t.me/nome_do_canal`):

1. Abra o canal no Telegram
2. Olhe o link do canal (ex: `t.me/escala_pm`)
3. O ID sera: `@escala_pm` ou o nome depois do `/`

#### Opcao B: Canal Privado (mais comum)

Se o canal for **privado** (so acessa por convite):

1. **Adicione o bot ao canal:**
   - Abra o canal
   - Clique no nome do canal (topo)
   - Clique em "Membros" ou "Adicionar Membros"
   - Busque pelo username do seu bot (ex: `@escala_pm_bot`)
   - Adicione como **administrador**
   - De permissao para: "Ler mensagens", "Enviar mensagens"

2. **Descubra o ID do canal:**
   - Envie uma mensagem qualquer no canal
   - Acesse este link no navegador:
     ```
     https://api.telegram.org/bot[SEU_TOKEN]/getUpdates
     ```
     Substitua `[SEU_TOKEN]` pelo token que voce guardou.
   
   - Procure por algo assim:
     ```json
     "chat":{"id":-1001234567890,"title":"Escala PM"...
     ```
   
   - O numero `-1001234567890` eh o ID do canal!

💾 **Anote este numero com sinal de menos!** Voce vai precisar dele no Passo 3.

---

## PASSO 2: Preparacao no GitHub

O **GitHub** eh onde vamos guardar os arquivos do bot. Eh como uma "nuvem" para codigos.

### 2.1 Criar Conta no GitHub

1. Acesse: **https://github.com**
2. Clique em **"Sign up"** (Cadastrar)
3. Preencha:
   - Email
   - Senha
   - Nome de usuario
4. Confirme seu email

### 2.2 Criar um Repositorio

Repositorio = "pasta" onde ficam os arquivos do projeto.

1. No GitHub, clique no botao **verde "New"** (ou "+")
2. Preencha:
   - **Repository name:** `bot-escala-militar`
   - **Description:** Bot de escala militar para Telegram
   - **Public** (deixe marcado)
   - **Add a README file** (NAO marque)
3. Clique em **"Create repository"**

### 2.3 Enviar os Arquivos

Agora vamos colocar os arquivos do bot no GitHub:

#### Metodo Facil (Upload direto):

1. No seu repositorio, clique em **"Add file"** → **"Upload files"**
2. Clique em **"choose your files"**
3. Selecione TODOS os arquivos que voce baixou:
   - `bot.py`
   - `pdf_parser.py`
   - `database.json`
   - `requirements.txt`
   - `render.yaml`
   - `web_server.py`
   - `.gitignore`
4. Em **"Commit changes"**, escreva:
   - Message: `Primeira versao do bot`
5. Clique em **"Commit changes"**

✅ **Pronto!** Seus arquivos estao no GitHub.

---

## PASSO 3: Deploy no Render.com

O **Render.com** vai manter seu bot online 24 horas por dia.

### 3.1 Criar Conta no Render

1. Acesse: **https://render.com**
2. Clique em **"Get Started for Free"**
3. Escolha **"Continue with GitHub"**
4. Autorize o Render a acessar seu GitHub
5. Complete o cadastro

### 3.2 Criar um Novo Servico

1. No painel do Render, clique em **"New"** (azul, no topo)
2. Escolha **"Blueprint"**
3. Clique em **"Connect a repository"**
4. Escolha o repositorio `bot-escala-militar`
5. Clique em **"Connect"**

### 3.3 Configurar as Variaveis de Ambiente

**ATENCAO:** Esta eh a parte mais importante!

1. No painel do seu servico, clique em **"Environment"**
2. Clique em **"Add Environment Variable"**
3. Adicione estas duas variaveis:

#### Variavel 1: BOT_TOKEN
- **Key:** `BOT_TOKEN`
- **Value:** Cole aqui o token que voce guardou do BotFather
- Exemplo: `123456789:ABCdefGHIjklMNOpqrSTUvwxyz`

#### Variavel 2: CANAL_ESCALA_ID
- **Key:** `CANAL_ESCALA_ID`
- **Value:** Cole aqui o ID do canal (com o sinal de menos)
- Exemplo: `-1001234567890`

4. Clique em **"Save Changes"**

### 3.4 Fazer o Deploy

1. Volte para a aba **"Settings"**
2. Clique em **"Manual Deploy"** → **"Deploy latest commit"**
3. Aguarde o processo (pode levar 2-3 minutos)
4. Quando aparecer **"Your service is live"**, esta pronto! 🎉

✅ **Seu bot esta ONLINE!**

---

## PASSO 4: Como Usar o Bot

### 4.1 Cadastro dos Policiais

Cada policial precisa se cadastrar para receber notificacoes.

#### Passo a passo para o policial:

1. **Abra uma conversa privada** com o bot:
   - Busque pelo username do bot (ex: `@escala_pm_bot`)
   - Clique em "Iniciar" ou envie `/start`

2. **Envie o comando de configuracao:**
   ```
   /configurar SD JOAO VICTOR
   ```
   
   **IMPORTANTE:** O nome deve ser **EXATAMENTE** como aparece na escala!
   
   ✅ Correto: `/configurar SD JOAO VICTOR`
   ❌ Errado: `/configurar Joao Victor` (sem o posto)
   ❌ Errado: `/configurar sd joao victor` (minusculo)

3. **Confirme o cadastro:**
   - Envie `/status` para verificar se esta tudo certo

### 4.2 Comandos Disponiveis

| Comando | Descricao |
|---------|-----------|
| `/start` | Inicia o bot e mostra boas-vindas |
| `/ajuda` | Mostra instrucoes de uso |
| `/configurar NOME` | Cadastra o policial (ex: `/configurar SD SILVA`) |
| `/status` | Verifica se esta cadastrado corretamente |
| `/recomecar` | Remove o cadastro atual |

### 4.3 Recebimento de Escalas

Quando alguem enviar um PDF no canal:

1. O bot **le automaticamente** o PDF
2. **Extrai os nomes** dos policiais
3. **Envia mensagem privada** para cada um:
   ```
   🚨 NOVA ESCALA DE SERVICO 🚨
   
   Ola, SD JOAO VICTOR!
   
   Voce foi escalado para o proximo plantao.
   
   📄 Escala: escala_janeiro.pdf
   📅 Data: 15/01/2024
   
   [Botao: ✅ CONFIRMAR CIENCIA]
   ```

4. O policial **clica no botao** para confirmar que leu

### 4.4 Confirmacao de Ciencia

Ao clicar em **"✅ CONFIRMAR CIENCIA"**:
- A mensagem e atualizada mostrando a confirmacao
- O administrador pode ver quem confirmou
- O policial tem comprovante de que viu a escala

---

## SOLUCAO DE PROBLEMAS

### ❌ Bot nao responde comandos

**Causas comuns:**
1. Bot nao esta no modo privado (deve ser conversa 1-a-1)
2. Token incorreto nas variaveis de ambiente
3. Servico parou no Render

**Solucao:**
- Verifique se esta em conversa privada (nao em grupo)
- No Render, va em "Logs" e veja se ha erros
- Reinicie o servico: "Manual Deploy" → "Deploy latest commit"

### ❌ PDF nao eh processado

**Causas comuns:**
1. Bot nao eh administrador do canal
2. ID do canal esta errado
3. Formato do PDF nao eh suportado

**Solucao:**
- Verifique se o bot esta como admin no canal
- Confira o ID do canal nas variaveis de ambiente
- Verifique os logs no Render

### ❌ Policial nao recebe notificacao

**Causas comuns:**
1. Nome cadastrado diferente do PDF
2. Policial nao iniciou conversa com o bot
3. Policial bloqueou o bot

**Solucao:**
- Verifique se o nome esta IDENTICO ao PDF (incluindo posto)
- Policial deve enviar `/start` para o bot primeiro
- Verifique se nao bloqueou o bot

### ❌ Bot para depois de um tempo (plano gratuito)

**Explicacao:**
No plano gratuito do Render, o bot "dorme" apos 15 minutos sem atividade.

**Solucoes:**
1. **Opcao 1:** Acesse a URL do web server periodicamente
2. **Opcao 2:** Use um servico de "ping" (como UptimeRobot) para acessar a cada 10 minutos
3. **Opcao 3:** Upgrade para plano pago ($7/mes)

---

## 📞 SUPORTE

Se tiver problemas:

1. Verifique os **logs no Render** (painel → "Logs")
2. Confira se as **variaveis de ambiente** estao corretas
3. Teste o bot localmente primeiro (veja abaixo)

### Teste Local (Avancado)

Se quiser testar no seu computador antes de colocar online:

1. Instale o Python 3.11: https://python.org
2. Abra o terminal e execute:
   ```bash
   pip install -r requirements.txt
   set BOT_TOKEN=seu_token_aqui
   set CANAL_ESCALA_ID=id_do_canal
   python bot.py
   ```

---

## 🎉 PARABENS!

Seu bot de escala militar esta pronto para uso!

**Resumo do que voce fez:**
1. ✅ Criou o bot no Telegram
2. ✅ Configurou o canal de escalas
3. ✅ Guardou os arquivos no GitHub
4. ✅ Colocou o bot online no Render
5. ✅ Policiais podem se cadastrar

**Proximos passos:**
- Compartilhe o username do bot com os policiais
- Ensine-os a usar `/configurar`
- Comece a postar as escalas no canal!

---

*Bot desenvolvido para automatizar escalas militares. Versao 1.0*
