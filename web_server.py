"""
WEB SERVER - Servidor Web Simples
=================================
Este servidor web eh usado para manter o bot "acordado"
no plano gratuito do Render.com.

No plano gratuito, o bot "dorme" apos 15 minutos de inatividade.
Este servidor cria uma pagina que pode ser acessada para manter
o servico ativo.

Autor: Bot Escala Militar
"""

from flask import Flask, jsonify
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def home():
    """Pagina principal com informacoes do bot."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bot de Escala Militar</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background-color: #f0f0f0;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2c3e50;
            }
            .status {
                background: #27ae60;
                color: white;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }
            .info {
                background: #ecf0f1;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>👮‍♂️ Bot de Escala Militar</h1>
            <div class="status">
                ✅ Bot Online e Funcionando!
            </div>
            <div class="info">
                <p><strong>Status:</strong> Operacional</p>
                <p><strong>Ultima verificacao:</strong> """ + datetime.now().strftime('%d/%m/%Y %H:%M:%S') + """</p>
                <p><strong>Versao:</strong> 1.0</p>
            </div>
            <p>Este servidor mantem o bot de escala militar online 24 horas.</p>
        </div>
    </body>
    </html>
    """

@app.route('/status')
def status():
    """Endpoint JSON para verificar status."""
    return jsonify({
        'status': 'online',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0',
        'service': 'bot-escala-militar'
    })

@app.route('/health')
def health():
    """Endpoint de health check."""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    # Pega a porta do ambiente (Render define automaticamente)
    porta = int(os.environ.get('PORT', 5000))
    
    # Inicia o servidor
    app.run(host='0.0.0.0', port=porta)
