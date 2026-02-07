"""
BOT DE ESCALA MILITAR - Cerebro Principal
=========================================
Bot do Telegram para ler PDFs de escalas militares e notificar policiais.

Funcionalidades:
- Ler PDFs de um canal do Telegram
- Extrair nomes de policiais
- Enviar mensagem privada para cada policial
- Sistema de confirmacao de ciencia
- Cadastro de policiais via comando /configurar

Autor: Bot Escala Militar
Versao: 1.0
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# Importa nosso parser de PDF
from pdf_parser import PDFParser

# Configuracao de logging (registra tudo que acontece)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============== CONFIGURACOES ==============
# Estas variaveis serao preenchidas pelas Environment Variables no Render

# Token do Bot (vem do @BotFather)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# ID do canal onde a escala eh postada (ex: -1001234567890)
CANAL_ESCALA_ID = os.environ.get("CANAL_ESCALA_ID", "")

# Nome do arquivo do banco de dados
ARQUIVO_DB = "database.json"

# ============== BANCO DE DADOS ==============

class BancoDeDados:
    """
    Classe para gerenciar o banco de dados JSON.
    Armazena informacoes dos policiais cadastrados.
    """
    
    def __init__(self, arquivo: str = ARQUIVO_DB):
        self.arquivo = arquivo
        self.dados = self.carregar()
    
    def carregar(self) -> dict:
        """Carrega os dados do arquivo JSON."""
        try:
            with open(self.arquivo, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Se o arquivo nao existe, cria estrutura padrao
            dados_padrao = {
                "policiais": {},  # nome -> {chat_id, data_cadastro}
                "escalas_processadas": [],  # IDs das mensagens ja processadas
                "confirmacoes": {}  # mensagem_id -> {policial: confirmou}
            }
            self.salvar(dados_padrao)
            return dados_padrao
    
    def salvar(self, dados: dict = None):
        """Salva os dados no arquivo JSON."""
        if dados is None:
            dados = self.dados
        with open(self.arquivo, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
    
    def cadastrar_policial(self, nome_completo: str, chat_id: int) -> bool:
        """
        Cadastra um novo policial no banco de dados.
        
        Args:
            nome_completo: Nome como aparece na escala (ex: "SD JOAO VICTOR")
            chat_id: ID do chat do Telegram do policial
            
        Returns:
            True se cadastrou, False se ja existia
        """
        nome_normalizado = nome_completo.upper().strip()
        
        if nome_normalizado in self.dados["policiais"]:
            return False
        
        self.dados["policiais"][nome_normalizado] = {
            "chat_id": chat_id,
            "data_cadastro": datetime.now().isoformat(),
            "nome_completo": nome_completo
        }
        self.salvar()
        return True
    
    def buscar_policial_por_nome(self, nome_escala: str) -> Optional[dict]:
        """
        Busca um policial pelo nome como aparece na escala.
        
        Args:
            nome_escala: Nome extraido do PDF (ex: "SD JOAO VICTOR")
            
        Returns:
            Dicionario com dados do policial ou None se nao encontrado
        """
        nome_normalizado = nome_escala.upper().strip()
        
        # Busca exata primeiro
        if nome_normalizado in self.dados["policiais"]:
            return self.dados["policiais"][nome_normalizado]
        
        # Se nao achou, tenta busca parcial (por exemplo, so pelo nome)
        for nome_cadastrado, dados in self.dados["policiais"].items():
            # Remove o posto e compara so o nome
            partes_escala = nome_normalizado.split()
            partes_cadastrado = nome_cadastrado.split()
            
            # Se o nome (sem posto) estiver contido
            if len(partes_escala) > 1 and len(partes_cadastrado) > 1:
                nome_sem_posto_escala = ' '.join(partes_escala[1:])
                nome_sem_posto_cadastrado = ' '.join(partes_cadastrado[1:])
                
                if nome_sem_posto_escala == nome_sem_posto_cadastrado:
                    return dados
        
        return None
    
    def ja_processou_escala(self, mensagem_id: int) -> bool:
        """Verifica se uma escala ja foi processada."""
        return mensagem_id in self.dados["escalas_processadas"]
    
    def marcar_escala_processada(self, mensagem_id: int):
        """Marca uma escala como processada."""
        if mensagem_id not in self.dados["escalas_processadas"]:
            self.dados["escalas_processadas"].append(mensagem_id)
            # Mantem so as ultimas 100 escalas (para nao ficar muito grande)
            if len(self.dados["escalas_processadas"]) > 100:
                self.dados["escalas_processadas"] = self.dados["escalas_processadas"][-100:]
            self.salvar()
    
    def registrar_confirmacao(self, mensagem_id: str, chat_id: int, confirmou: bool):
        """Registra se o policial confirmou ciencia da escala."""
        if mensagem_id not in self.dados["confirmacoes"]:
            self.dados["confirmacoes"][mensagem_id] = {}
        
        self.dados["confirmacoes"][mensagem_id][str(chat_id)] = {
            "confirmou": confirmou,
            "data": datetime.now().isoformat()
        }
        self.salvar()


# Instancia global do banco de dados
db = BancoDeDados()

# Instancia do parser de PDF
pdf_parser = PDFParser()

# ============== COMANDOS DO BOT ==============

async def comando_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /start - Boas-vindas ao usuario.
    """
    mensagem = """
👮‍♂️ *BOT DE ESCALA MILITAR* 👮‍♂️

Bem-vindo, policial!

Este bot foi criado para enviar notificacoes automaticas sobre sua escala de servico.

*Comandos disponiveis:*
/configurar - Cadastrar seu nome para receber avisos
/ajuda - Ver instrucoes de uso
/status - Verificar se voce esta cadastrado

⚠️ *IMPORTANTE:* Para funcionar, voce precisa se cadastrar usando o comando /configurar
"""
    
    await update.message.reply_text(mensagem, parse_mode='Markdown')


async def comando_ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /ajuda - Explica como usar o bot.
    """
    mensagem = """
📋 *COMO USAR O BOT DE ESCALA* 📋

*1. CADASTRO*
Use o comando:
`/configurar SD JOAO VICTOR`

Substitua "SD JOAO VICTOR" pelo seu nome *EXATAMENTE* como aparece na escala.

*2. RECEBIMENTO*
Quando uma nova escala for postada no canal, voce recebera uma mensagem privada automaticamente.

*3. CONFIRMACAO*
Ao receber a notificacao, clique no botao *"✅ CONFIRMAR CIENCIA"* para registrar que voce viu.

*4. DICAS*
- O nome deve ser identico ao da escala (incluindo posto/graduacao)
- Se mudar de numero/telefone, cadastre novamente
- Em caso de duvida, fale com o administrador

*Comandos uteis:*
/status - Verifica seu cadastro
/recomecar - Remove seu cadastro atual
"""
    
    await update.message.reply_text(mensagem, parse_mode='Markdown')


async def comando_configurar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /configurar - Cadastra o policial no sistema.
    Uso: /configurar SD JOAO VICTOR
    """
    chat_id = update.effective_chat.id
    
    # Pega o nome que o usuario digitou apos o comando
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "❌ *Erro:* Voce precisa informar seu nome!\n\n"
            "*Uso correto:*\n"
            "`/configurar SD JOAO VICTOR`\n\n"
            "Digite seu nome *EXATAMENTE* como aparece na escala.",
            parse_mode='Markdown'
        )
        return
    
    # Junta todos os argumentos (para nomes compostos)
    nome_completo = ' '.join(args)
    
    # Tenta cadastrar
    sucesso = db.cadastrar_policial(nome_completo, chat_id)
    
    if sucesso:
        await update.message.reply_text(
            f"✅ *Cadastro realizado com sucesso!*\n\n"
            f"Nome: `{nome_completo}`\n"
            f"Chat ID: `{chat_id}`\n\n"
            f"Voce recebera notificacoes sempre que sua escala for publicada.\n\n"
            f"Teste: Envie /status para confirmar.",
            parse_mode='Markdown'
        )
        logger.info(f"Novo cadastro: {nome_completo} (Chat: {chat_id})")
    else:
        await update.message.reply_text(
            f"⚠️ *Aviso:* Este nome ja esta cadastrado!\n\n"
            f"Se precisar atualizar, use /recomecar primeiro.",
            parse_mode='Markdown'
        )


async def comando_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /status - Mostra se o usuario esta cadastrado.
    """
    chat_id = update.effective_chat.id
    
    # Busca o policial pelo chat_id
    encontrado = None
    for nome, dados in db.dados["policiais"].items():
        if dados["chat_id"] == chat_id:
            encontrado = (nome, dados)
            break
    
    if encontrado:
        nome, dados = encontrado
        await update.message.reply_text(
            f"✅ *Voce esta cadastrado!*\n\n"
            f"Nome na escala: `{nome}`\n"
            f"Cadastrado em: {dados['data_cadastro'][:10]}\n\n"
            f"Voce recebera notificacoes de escala.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ *Voce ainda nao esta cadastrado!*\n\n"
            "Use /configurar para se cadastrar.",
            parse_mode='Markdown'
        )


async def comando_recomecar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Comando /recomecar - Remove o cadastro do usuario.
    """
    chat_id = update.effective_chat.id
    
    # Busca e remove o policial
    removido = False
    for nome in list(db.dados["policiais"].keys()):
        if db.dados["policiais"][nome]["chat_id"] == chat_id:
            del db.dados["policiais"][nome]
            db.salvar()
            removido = True
            break
    
    if removido:
        await update.message.reply_text(
            "✅ Seu cadastro foi removido.\n\n"
            "Use /configurar para se cadastrar novamente.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "Você não estava cadastrado.\n\n"
            "Use /configurar para se cadastrar.",
            parse_mode='Markdown'
        )


# ============== PROCESSAMENTO DE ESCALAS ==============

async def processar_pdf_escala(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Processa PDFs enviados ao canal de escalas.
    Extrai os nomes e envia notificacoes.
    """
    mensagem = update.message
    chat_id = mensagem.chat_id
    mensagem_id = mensagem.message_id
    
    # Verifica se eh o canal correto
    if str(chat_id) != str(CANAL_ESCALA_ID):
        logger.info(f"Mensagem de outro canal ignorada: {chat_id}")
        return
    
    # Verifica se ja processou esta escala
    if db.ja_processou_escala(mensagem_id):
        logger.info(f"Escala {mensagem_id} ja foi processada. Ignorando.")
        return
    
    # Verifica se tem documento
    if not mensagem.document:
        return
    
    # Verifica se eh PDF
    if not mensagem.document.file_name.lower().endswith('.pdf'):
        return
    
    logger.info(f"Novo PDF detectado: {mensagem.document.file_name}")
    
    # Baixa o arquivo
    arquivo = await context.bot.get_file(mensagem.document.file_id)
    caminho_pdf = f"/tmp/escala_{mensagem_id}.pdf"
    await arquivo.download_to_drive(caminho_pdf)
    
    try:
        # Processa o PDF
        policiais_na_escala = pdf_parser.processar_pdf(caminho_pdf)
        
        if not policiais_na_escala:
            await mensagem.reply_text(
                "⚠️ Nenhum policial encontrado nesta escala.\n"
                "Verifique se o PDF esta correto.",
                quote=True
            )
            return
        
        # Contadores
        notificados = 0
        nao_cadastrados = []
        
        # Envia notificacao para cada policial
        for policial in policiais_na_escala:
            dados_policial = db.buscar_policial_por_nome(policial['nome_completo'])
            
            if dados_policial:
                # Cria botao de confirmacao
                keyboard = [
                    [InlineKeyboardButton(
                        "✅ CONFIRMAR CIENCIA", 
                        callback_data=f"confirmar_{mensagem_id}_{policial['nome_completo']}"
                    )]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                # Monta a mensagem
                texto_mensagem = (
                    f"🚨 *NOVA ESCALA DE SERVICO* 🚨\n\n"
                    f"Ola, *{policial['nome_completo']}*!\n\n"
                    f"Voce foi escalado para o proximo plantao.\n\n"
                    f"📄 Escala: {mensagem.document.file_name}\n"
                    f"📅 Data: {datetime.now().strftime('%d/%m/%Y')}\n\n"
                    f"Por favor, confirme o recebimento desta mensagem."
                )
                
                try:
                    await context.bot.send_message(
                        chat_id=dados_policial['chat_id'],
                        text=texto_mensagem,
                        parse_mode='Markdown',
                        reply_markup=reply_markup
                    )
                    notificados += 1
                    logger.info(f"Notificacao enviada para {policial['nome_completo']}")
                except Exception as e:
                    logger.error(f"Erro ao notificar {policial['nome_completo']}: {e}")
            else:
                nao_cadastrados.append(policial['nome_completo'])
        
        # Marca como processada
        db.marcar_escala_processada(mensagem_id)
        
        # Resumo no canal
        resumo = f"✅ *Escala processada!*\n\n"
        resumo += f"📊 Total na escala: {len(policiais_na_escala)}\n"
        resumo += f"✉️ Notificados: {notificados}\n"
        
        if nao_cadastrados:
            resumo += f"❌ Nao cadastrados: {len(nao_cadastrados)}\n"
            resumo += f"\n*Policiais nao cadastrados:*\n"
            for nome in nao_cadastrados[:10]:  # Mostra so os 10 primeiros
                resumo += f"• {nome}\n"
            if len(nao_cadastrados) > 10:
                resumo += f"... e mais {len(nao_cadastrados) - 10}\n"
            resumo += f"\nEstes precisam usar /configurar no privado do bot."
        
        await mensagem.reply_text(resumo, parse_mode='Markdown', quote=True)
        
    except Exception as e:
        logger.error(f"Erro ao processar escala: {e}")
        await mensagem.reply_text(
            f"❌ Erro ao processar escala: {str(e)}",
            quote=True
        )
    finally:
        # Limpa o arquivo temporario
        if os.path.exists(caminho_pdf):
            os.remove(caminho_pdf)


async def botao_confirmar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Processa o clique no botao "Confirmar Ciencia".
    """
    query = update.callback_query
    await query.answer()  # Remove o "carregando..."
    
    # Extrai dados do callback_data
    # Formato: confirmar_{mensagem_id}_{nome_completo}
    partes = query.data.split('_', 2)
    if len(partes) < 3:
        return
    
    mensagem_id = partes[1]
    nome_completo = partes[2]
    chat_id = query.message.chat_id
    
    # Registra a confirmacao
    db.registrar_confirmacao(mensagem_id, chat_id, True)
    
    # Atualiza a mensagem
    texto_original = query.message.text
    
    nova_mensagem = (
        f"{texto_original}\n\n"
        f"✅ *CIENCIA CONFIRMADA*\n"
        f"Confirmado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    )
    
    # Remove o botao e atualiza o texto
    await query.edit_message_text(
        nova_mensagem,
        parse_mode='Markdown'
    )
    
    logger.info(f"Ciencia confirmada por {nome_completo}")


# ============== INICIALIZACAO ==============

def main():
    """
    Funcao principal que inicia o bot.
    """
    logger.info("Iniciando Bot de Escala Militar...")
    
    # Verifica se o token foi configurado
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN nao configurado!")
        print("❌ ERRO: Configure a variavel de ambiente BOT_TOKEN")
        return
    
    if not CANAL_ESCALA_ID:
        logger.warning("CANAL_ESCALA_ID nao configurado!")
    
    # Cria a aplicacao
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Adiciona handlers de comandos
    application.add_handler(CommandHandler("start", comando_start))
    application.add_handler(CommandHandler("ajuda", comando_ajuda))
    application.add_handler(CommandHandler("help", comando_ajuda))
    application.add_handler(CommandHandler("configurar", comando_configurar))
    application.add_handler(CommandHandler("status", comando_status))
    application.add_handler(CommandHandler("recomecar", comando_recomecar))
    
    # Handler para PDFs no canal
    application.add_handler(MessageHandler(
        filters.Document.PDF & filters.Chat(chat_id=CANAL_ESCALA_ID if CANAL_ESCALA_ID else None),
        processar_pdf_escala
    ))
    
    # Handler para botao de confirmacao
    application.add_handler(CallbackQueryHandler(botao_confirmar_callback, pattern="^confirmar_"))
    
    logger.info("Bot iniciado e aguardando mensagens...")
    
    # Inicia o bot (modo polling)
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
