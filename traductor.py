from flask import Flask, request
import os
import requests

app = Flask(__name__)

# Almacenamiento simple en memoria (NO para múltiples usuarios en producción)
historial = []

@app.route('/')
def home():
    return '''
    <form method="POST" action="/consulta">
        <textarea name="pregunta" rows="5" cols="50" placeholder="Escribe tu pregunta..."></textarea><br>
        <button>Enviar</button>
    </form>
    '''

@app.route('/consulta', methods=['POST'])
def consulta():
    try:
        pregunta = request.form.get('pregunta', '').strip()
        
        if not pregunta:
            return "Error: Pregunta vacía"
        
        # 1. Configurar API Key (¡IMPORTANTE!)
        api_key = os.environ.get('DEEPSEEK_API_KEY')
        if not api_key:
            return '''
            <h3>⚠️ Error de Configuración</h3>
            <p>La API Key de DeepSeek no está configurada.</p>
            <p>Configura la variable de entorno <strong>DEEPSEEK_API_KEY</strong> en Render.com</p>
            <p>Obtén una API Key gratis en: <a href="https://platform.deepseek.com/api_keys">platform.deepseek.com</a></p>
            '''
        
        # 2. Preparar mensajes para DeepSeek
        mensajes = []
        
        # Añadir contexto del historial (últimas 2 preguntas/respuestas)
        for item in historial[-4:]:  # Mantenerlo pequeño
            mensajes.append(item)
        
        # Añadir la nueva pregunta
        mensajes.append({"role": "user", "content": pregunta})
        
        # 3. Llamar a DeepSeek API
        url = "https://api.deepseek.com/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": mensajes,
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        respuesta_api = requests.post(url, headers=headers, json=data, timeout=30)
        
        # 4. Manejar posibles errores
        if respuesta_api.status_code != 200:
            error_msg = f"Error de API: {respuesta_api.status_code}"
            try:
                error_detail = respuesta_api.json()
                error_msg += f" - {error_detail}"
            except:
                error_msg += f" - {respuesta_api.text[:100]}"
            
            return f'''
            <h3>⚠️ Error con DeepSeek API</h3>
            <p>{error_msg}</p>
            <p><a href="/">Intentar de nuevo</a></p>
            '''
        
        # 5. Extraer respuesta
        respuesta_json = respuesta_api.json()
        respuesta_texto = respuesta_json['choices'][0]['message']['content']
        
        # 6. Actualizar historial (mantener conversación)
        historial.append({"role": "user", "content": pregunta})
        historial.append({"role": "assistant", "content": respuesta_texto})
        
        # Limitar tamaño del historial
        if len(historial) > 10:  # Máximo 5 intercambios
            historial.pop(0)
            historial.pop(0)
        
        # 7. Calcular contexto usado (aproximado)
        total_caracteres = sum(len(str(msg.get('content', ''))) for msg in mensajes)
        contexto_usado = min(100, int((total_caracteres / 4) / 128000 * 100))  # Aprox tokens
        
        # 8. Generar respuesta HTML
        html = f'''
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Interfaz Ontológica</title>
            <style>
                body {{ font-family: monospace; max-width: 800px; margin: 20px auto; padding: 20px; }}
                .pregunta {{ background: #f0f0f0; padding: 15px; border-radius: 5px; }}
                .respuesta {{ white-space: pre-wrap; margin: 20px 0; line-height: 1.5; }}
                .estado {{ color: #666; font-size: 0.9em; margin-top: 20px; }}
                a {{ color: #0066cc; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <h1>🧠 Interfaz Ontológica</h1>
            <a href="/" style="float:right;">Nuevo Chat</a>
            
            <div class="pregunta">
                <strong>Tu consulta:</strong><br>
                {pregunta}
            </div>
            
            <div class="respuesta">
                <strong>Respuesta:</strong><br>
                {respuesta_texto}
            </div>
            
            <div class="estado">
                [Estado del Contexto: ~{contexto_usado}% usado]
            </div>
            
            <hr>
            
            <form method="POST" action="/consulta">
                <textarea name="pregunta" rows="5" cols="50" placeholder="Haz otra pregunta..."></textarea><br>
                <button>Enviar</button>
            </form>
        </body>
        </html>
        '''
        
        return html
        
    except requests.exceptions.Timeout:
        return "Error: Timeout al conectar con DeepSeek API"
    except Exception as e:
        return f"Error inesperado: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
