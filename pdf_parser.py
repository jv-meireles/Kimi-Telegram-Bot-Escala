"""
PDF PARSER - Leitor de Escalas Militares
=====================================
Este modulo eh responsavel por extrair os nomes dos policiais
de arquivos PDF, sejam eles digitais ou escaneados (OCR).

Autor: Bot Escala Militar
Versao: 1.0
"""

import re
import logging
from typing import List, Optional

# Tentativa de importar bibliotecas de OCR (para PDFs escaneados)
try:
    import pytesseract
    from pdf2image import convert_from_path
    from PIL import Image
    OCR_DISPONIVEL = True
except ImportError:
    OCR_DISPONIVEL = False
    logging.warning("OCR nao disponivel. PDFs escaneados nao serao processados.")

# Importar leitor de PDF digital
try:
    import PyPDF2
    PDF_READER_DISPONIVEL = True
except ImportError:
    PDF_READER_DISPONIVEL = False

# Configuracao de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class PDFParser:
    """
    Classe responsavel por extrair texto de PDFs e identificar nomes de policiais.
    Suporta tanto PDFs digitais quanto escaneados (via OCR).
    """
    
    # Padroes de postos/graduacoes militares comuns na PM/Policia Civil
    POSTOS_GRADUACOES = [
        r'CEL\b', r'TC\b', r'MAJ\b', r'CAP\b', r'1[º°]\s*TEN\b', r'2[º°]\s*TEN\b',
        r'ASP\b', r'SUB\s*TEN\b', r'1[º°]\s*SGT\b', r'2[º°]\s*SGT\b', r'3[º°]\s*SGT\b',
        r'CB\b', r'SD\b', r'SD\s*EV\b', r'SD\s*EP\b'
    ]
    
    def __init__(self):
        """Inicializa o parser com os padroes de postos."""
        # Cria uma regex unica combinando todos os postos
        self.regex_postos = r'(?:' + '|'.join(self.POSTOS_GRADUACOES) + r')'
        logger.info("PDF Parser inicializado com sucesso!")
    
    def extrair_texto_pdf_digital(self, caminho_pdf: str) -> str:
        """
        Extrai texto de um PDF digital (onde o texto eh selecionavel).
        
        Args:
            caminho_pdf: Caminho para o arquivo PDF
            
        Returns:
            String com todo o texto extraido do PDF
        """
        if not PDF_READER_DISPONIVEL:
            raise ImportError("PyPDF2 nao instalado!")
        
        texto_completo = ""
        
        try:
            with open(caminho_pdf, 'rb') as arquivo:
                leitor = PyPDF2.PdfReader(arquivo)
                
                logger.info(f"PDF tem {len(leitor.pages)} pagina(s)")
                
                # Extrai texto de cada pagina
                for numero_pagina, pagina in enumerate(leitor.pages, 1):
                    texto_pagina = pagina.extract_text()
                    if texto_pagina:
                        texto_completo += texto_pagina + "\n"
                        logger.debug(f"Pagina {numero_pagina}: {len(texto_pagina)} caracteres extraidos")
                    else:
                        logger.warning(f"Pagina {numero_pagina}: Nenhum texto encontrado")
                        
        except Exception as erro:
            logger.error(f"Erro ao ler PDF digital: {erro}")
            raise
        
        return texto_completo
    
    def extrair_texto_ocr(self, caminho_pdf: str) -> str:
        """
        Extrai texto de um PDF escaneado usando OCR (Tesseract).
        Converte cada pagina em imagem e faz a leitura.
        
        Args:
            caminho_pdf: Caminho para o arquivo PDF
            
        Returns:
            String com todo o texto reconhecido pelo OCR
        """
        if not OCR_DISPONIVEL:
            raise ImportError("Bibliotecas de OCR nao instaladas!")
        
        texto_completo = ""
        
        try:
            logger.info("Convertendo PDF para imagens para OCR...")
            # Converte PDF em lista de imagens (uma por pagina)
            imagens = convert_from_path(caminho_pdf, dpi=300)
            
            logger.info(f"Processando {len(imagens)} pagina(s) com OCR...")
            
            for numero_pagina, imagem in enumerate(imagens, 1):
                # Configuracao do Tesseract para portugues
                texto_pagina = pytesseract.image_to_string(imagem, lang='por')
                texto_completo += texto_pagina + "\n"
                logger.debug(f"OCR - Pagina {numero_pagina}: {len(texto_pagina)} caracteres reconhecidos")
                
        except Exception as erro:
            logger.error(f"Erro no OCR: {erro}")
            raise
        
        return texto_completo
    
    def extrair_texto(self, caminho_pdf: str, usar_ocr: bool = False) -> str:
        """
        Metodo principal para extrair texto de um PDF.
        Tenta primeiro como digital, se falhar ou se usar_ocr=True, usa OCR.
        
        Args:
            caminho_pdf: Caminho para o arquivo PDF
            usar_ocr: Forca o uso de OCR mesmo se for PDF digital
            
        Returns:
            String com todo o texto do PDF
        """
        if usar_ocr:
            logger.info("Modo OCR forcado pelo usuario")
            return self.extrair_texto_ocr(caminho_pdf)
        
        # Tenta primeiro como PDF digital
        try:
            texto = self.extrair_texto_pdf_digital(caminho_pdf)
            
            # Se extraiu pouco texto (menos de 50 caracteres), provavelmente eh imagem
            if len(texto.strip()) < 50:
                logger.warning("PDF digital retornou pouco texto. Tentando OCR...")
                if OCR_DISPONIVEL:
                    texto = self.extrair_texto_ocr(caminho_pdf)
                else:
                    logger.error("OCR nao disponivel para PDF escaneado!")
                    
            return texto
            
        except Exception as erro:
            logger.error(f"Falha na leitura digital: {erro}")
            # Se falhou e OCR esta disponivel, tenta OCR
            if OCR_DISPONIVEL:
                logger.info("Tentando OCR como fallback...")
                return self.extrair_texto_ocr(caminho_pdf)
            raise
    
    def identificar_nomes(self, texto: str) -> List[dict]:
        """
        Identifica nomes de policiais no texto extraido do PDF.
        Procura por padroes como: "SD JOAO VICTOR", "SGT FIALHO", etc.
        
        Args:
            texto: Texto extraido do PDF
            
        Returns:
            Lista de dicionarios com 'posto' e 'nome' de cada policial
        """
        policiais_encontrados = []
        
        # Normaliza o texto: remove acentos, converte para maiusculas
        texto = texto.upper()
        
        # Substitui quebras de linha por espacos para facilitar
        texto = texto.replace('\n', ' ')
        
        # Remove espacos multiplos
        texto = re.sub(r'\s+', ' ', texto)
        
        # Padrao para encontrar: POSTO + NOME (ate o proximo ponto, virgula, ponto-e-virgula ou fim)
        # Exemplo: "SD JOAO VICTOR; SGT FIALHO; SUB TEN SILVA"
        padrao = r'(' + self.regex_postos + r')\s+([A-Z\s]+?)(?:;|,|\.|\n|$)'
        
        # Busca todas as ocorrencias
        matches = re.findall(padrao, texto)
        
        for match in matches:
            posto = match[0].strip()
            nome = match[1].strip()
            
            # Limpa o nome (remove espacos extras)
            nome = ' '.join(nome.split())
            
            # Ignora nomes muito curtos (provavelmente falso positivo)
            if len(nome) < 2:
                continue
                
            # Ignora se parece ser parte de outro texto (contem palavras comuns)
            palavras_invalidas = ['ESCALA', 'PLANTAO', 'DATA', 'HORA', 'LOCAL', 'SERVICO']
            if any(palavra in nome for palavra in palavras_invalidas):
                continue
            
            policiais_encontrados.append({
                'posto': posto,
                'nome': nome,
                'nome_completo': f"{posto} {nome}"
            })
            
            logger.info(f"Policial identificado: {posto} {nome}")
        
        # Remove duplicatas mantendo a ordem
        vistos = set()
        policiais_unicos = []
        for policial in policiais_encontrados:
            chave = policial['nome_completo']
            if chave not in vistos:
                vistos.add(chave)
                policiais_unicos.append(policial)
        
        logger.info(f"Total de policiais identificados: {len(policiais_unicos)}")
        return policiais_unicos
    
    def processar_pdf(self, caminho_pdf: str, usar_ocr: bool = False) -> List[dict]:
        """
        Metodo principal que processa um PDF completo.
        Extrai o texto e identifica os policiais.
        
        Args:
            caminho_pdf: Caminho para o arquivo PDF
            usar_ocr: Forca o uso de OCR
            
        Returns:
            Lista de dicionarios com informacoes dos policiais
        """
        logger.info(f"Iniciando processamento do PDF: {caminho_pdf}")
        
        # Extrai o texto do PDF
        texto = self.extrair_texto(caminho_pdf, usar_ocr)
        
        logger.debug(f"Texto extraido ({len(texto)} caracteres):")
        logger.debug(texto[:500] + "..." if len(texto) > 500 else texto)
        
        # Identifica os nomes dos policiais
        policiais = self.identificar_nomes(texto)
        
        return policiais


# Teste rapido (executar apenas se rodar este arquivo diretamente)
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python pdf_parser.py <caminho_do_pdf>")
        print("\nExemplo:")
        print("  python pdf_parser.py escala.pdf")
        sys.exit(1)
    
    caminho = sys.argv[1]
    parser = PDFParser()
    
    try:
        resultado = parser.processar_pdf(caminho)
        print("\n" + "="*50)
        print("POLICIAIS ENCONTRADOS:")
        print("="*50)
        for i, policial in enumerate(resultado, 1):
            print(f"{i}. {policial['nome_completo']}")
        print("="*50)
    except Exception as e:
        print(f"Erro: {e}")
