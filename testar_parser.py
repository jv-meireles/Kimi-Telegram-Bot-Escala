"""
SCRIPT DE TESTE - PDF Parser
============================
Use este script para testar se o parser esta identificando
os nomes corretamente antes de colocar o bot online.

Como usar:
1. Coloque seu PDF de escala na mesma pasta
2. Execute: python testar_parser.py escala.pdf
"""

import sys
from pdf_parser import PDFParser

def main():
    # Verifica se o usuario passou o nome do arquivo
    if len(sys.argv) < 2:
        print("="*60)
        print("TESTADOR DE PARSER DE ESCALA")
        print("="*60)
        print("\nUso: python testar_parser.py <arquivo.pdf>")
        print("\nExemplo:")
        print("  python testar_parser.py escala_janeiro.pdf")
        print("\n" + "="*60)
        sys.exit(1)
    
    caminho_pdf = sys.argv[1]
    
    print("="*60)
    print("TESTANDO PARSER DE ESCALA MILITAR")
    print("="*60)
    print(f"\nArquivo: {caminho_pdf}")
    print("-"*60)
    
    try:
        # Cria o parser
        parser = PDFParser()
        
        # Processa o PDF
        policiais = parser.processar_pdf(caminho_pdf)
        
        print("\n✅ PROCESSAMENTO CONCLUIDO!")
        print("="*60)
        
        if policiais:
            print(f"\n🎯 POLICIAIS ENCONTRADOS: {len(policiais)}\n")
            print("-"*60)
            
            for i, policial in enumerate(policiais, 1):
                print(f"{i:2d}. {policial['nome_completo']}")
            
            print("-"*60)
            print(f"\nTotal: {len(policiais)} policiais identificados")
            
        else:
            print("\n⚠️  ATENCAO: Nenhum policial encontrado!")
            print("\nPossiveis causas:")
            print("  - O PDF pode estar em formato de imagem (use OCR)")
            print("  - Os nomes podem estar em formato diferente")
            print("  - O PDF pode estar vazio ou corrompido")
        
        print("\n" + "="*60)
        
    except FileNotFoundError:
        print(f"\n❌ ERRO: Arquivo nao encontrado: {caminho_pdf}")
        print("\nVerifique se o nome do arquivo esta correto.")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        print("\nDetalhes do erro:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
