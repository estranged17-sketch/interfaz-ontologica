from flask import Flask, request
import os
import requests
import time

app = Flask(__name__)

# Almacenamiento por sesión en memoria (basado en IP del cliente)
sesiones_activas = {}

META_MARCO = """Eres la Interfaz Ontológica Unificada. 
Principios operativos:
1. Respuestas en TEXTO PLANO PURO (cero markdown, cero HTML, cero código)
2. Lenguaje claro y accesible
3. Si la pregunta es técnica, explica como a un no-especialista
4. Si es filosófica, profundiza en los aspectos ontológicos
5. Estructura: Contenido principal → "---" → [Estado: X% contexto]

Formato EJEMPLO:
[tu respuesta en texto puro]

---

[Estado del Sistema: ~5% del contexto usado | Modelo: OpenRouter Free]"""

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>🧬 INTERFAZ ONTOLÓGICA</title>
        <style>
            body {
                font-family: "Courier New", Courier, monospace;
                font-size: 14px;
                margin: 15px;
                background-color: #f0f0f0;
                color: #000000;
            }
            .marco {
                border: 2px solid #333333;
                padding: 20px;
                background-color: #ffffff;
                max-width: 780px;
                margin: 0 auto;
            }
            h1 {
                color: #2c3e50;
                border-bottom: 1px solid #7f8c8d;
                padding-bottom: 10px;
            }
            textarea {
                width: 98%;
                height: 100px;
                font-family: monospace;
                font-size: 14px;
                padding: 10px;
                border: 1px solid #bdc3c7;
                background: #fafafa;
            }
            input[type="submit"] {
                background-color: #2980b9;
                color: white;
                padding: 12px 25px;
                border: none;
                font-family: monospace;
                font-size: 16px;
                cursor: pointer;
                margin-top: 10px;
            }
            input[type="submit"]:hover {
                background-color: #3498db;
            }
            .info-modelo {
                background: linear-gradient(to right, #2c3e50, #4a6491);
                color: white;
                padding: 10px;
                margin: 15px 0;
                font-size: 12px;
                border-radius: 3px;
            }
            .estado-sistema {
                background-color: #34495e;
                color: #ecf0f1;
                padding: 10px;
                font-size: 11px;
                margin-top: 15px;
            }
            a {
                color: #2980b9;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
            @media (max-width: 600px) {
                .marco { padding: 10px; }
                textarea { height: 80px; }
            }
        </style>
    </head>
    <body>
        <div class="marco">
            <h1>🧬 INTERFAZ ONTOLÓGICA UNIFICADA</h1>
            
            <div class="info-modelo">
                ⚡ <strong>MODELO ACTIVO:</strong> OpenRouter Free Router (Dinámico)<br>
                🆓 <strong>ACCESO:</strong> Gratuito vía OpenRouter API<br>
                🧠 <strong>CONTEXTO:</strong> Variable según el modelo asignado por el router
            </div>
            
            <p><strong>Hardware objetivo:</strong> Nintendo Wii (2006), navegadores legacy (IE6+, Lynx), terminales texto</p>
            
            <form method="POST" action="/consulta">
                <textarea name="pregunta" placeholder="Formula tu pregunta o reflexión..." required></textarea><br>
                <input type="submit" value="CONSULTAR AL LOGOS">
            </form>
            
            <div class="estado-sistema">
                ✅ Backend: Flask en Render.com | 🌐 Frontend: HTML 4.01 | 🔄 Protocolo: HTTP/1.1<br>
                📊 Historial: 3 intercambios máximo | ⚙️ Arquitectura AEIOU: Capas N0-N4
            </div>
            
            <div style="margin-top: 20px; font-size: 12px; color: #7f8c8d;">
                <strong>Ejemplos conceptuales:</strong><br>
                • "¿Cómo esta arquitectura restaura la unidad comunicativa entre polos tecnológicos?"<br>
                • "Explica el principio de no-dualidad operativa en este sistema"<br>
                • "¿Qué significa que Atman sea función pura en N1?"<br>
                • "Demuestra cómo un navegador de Wii puede dialogar con la IA mediante OpenRouter"
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/consulta', methods=['POST'])
def consulta():
    inicio_tiempo = time.time()
    
    try:
        pregunta = request.form.get('pregunta', '').strip()
        
        if not pregunta or len(pregunta) < 2:
            return '''
            <div class="marco">
                <h2>⚠️ Consulta inválida</h2>
                <p>La pregunta está vacía o es demasiado corta.</p>
                <p><a href="/">← Volver a la interfaz</a></p>
            </div>
            '''
        
        # Gestión de sesión por IP
        ip_cliente = request.remote_addr or "127.0.0.1"
        if ip_cliente not in sesiones_activas:
            sesiones_activas[ip_cliente] = {
                'historial': [],
                'timestamp': time.time()
            }
        
        sesion = sesiones_activas[ip_cliente]
        
        if time.time() - sesion['timestamp'] > 7200:
            sesion['historial'] = []
            
        historial = sesion['historial']
        
        # Construcción de la lista de mensajes
        mensajes_ia = []
        mensajes_ia.append({"role": "system", "content": META_MARCO})
        
        for item in historial:
            mensajes_ia.append(item)
            
        mensajes_ia.append({"role": "user", "content": pregunta})
        
        api_key = os.environ.get('OPENROUTER_API_KEY', '')
        
        headers = {
            "Content-Type": "application/json",
        }
        
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            headers["HTTP-Referer"] = "https://interfaz-ontologica.onrender.com"
            headers["X-Title"] = "Interfaz Ontologica"
        
        # Cambio clave al endpoint dinámico openrouter/free
        payload = {
            "model": "openrouter/free",
            "messages": mensajes_ia,
            "max_tokens": 1200,
            "temperature": 0.7,
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1,
            "stream": False
        }
        
        try:
            respuesta_api = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=90
            )
            
            tiempo_respuesta = time.time() - inicio_tiempo
            
            if respuesta_api.status_code == 200:
                datos_respuesta = respuesta_api.json()
                texto_respuesta = datos_respuesta['choices'][0]['message']['content']
                
                # Detectar qué modelo real asignó OpenRouter dinámicamente
                modelo_real = datos_respuesta.get('model', 'openrouter/free')
                
                if "---" not in texto_respuesta:
                    texto_respuesta += f"\n\n---\n\n[Estado del Sistema: Normal | Modelo Asignado: {modelo_real}]"
                
                modelo_utilizado = f"OpenRouter Free ({modelo_real})"
                estado_conexion = f"[✅ Conectado vía OpenRouter Free | Tiempo: {round(tiempo_respuesta, 1)}s]"
            else:
                raise Exception(f"API error {respuesta_api.status_code}: {respuesta_api.text}")
                
        except Exception as api_error:
            tiempo_respuesta = time.time() - inicio_tiempo
            
            texto_respuesta = f"""Consulta recibida: "{pregunta}"

El servicio dinámico OpenRouter Free experimentó un problema de conexión temporal.

Detalle: {str(api_error)}

ESTADO DE RESPALDO:
• Backend: Operativo en Render.com
• Canal: Interfaz Ontológica
• Tiempo de respuesta: {round(tiempo_respuesta, 1)}s

---

[Estado del Sistema: Modo Reserva Activo]"""
            
            modelo_utilizado = "Sistema de demostración (Reserva)"
            estado_conexion = f"[⚠️ Error en OpenRouter Free | Tiempo: {round(tiempo_respuesta, 1)}s]"

        # Actualización de historial
        historial.append({"role": "user", "content": pregunta[:200]})
        historial.append({"role": "assistant", "content": texto_respuesta[:300]})
        
        if len(historial) > 6:
            historial = historial[-6:]
            
        sesion['historial'] = historial
        sesion['timestamp'] = time.time()
        
        caracteres_totales = sum(len(str(m.get('content', ''))) for m in mensajes_ia)
        porcentaje_contexto = max(1, min(100, caracteres_totales // 2500))
        
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Respuesta - Interfaz Ontológica</title>
            <style>
                body {{
                    font-family: "Courier New", Courier, monospace;
                    font-size: 14px;
                    margin: 15px;
                    background-color: #f0f0f0;
                    color: #000000;
                }}
                .marco {{
                    border: 2px solid #333333;
                    padding: 20px;
                    background-color: #ffffff;
                    max-width: 780px;
                    margin: 0 auto;
                }}
                .info-respuesta {{
                    background: linear-gradient(to right, #2c3e50, #27ae60);
                    color: white;
                    padding: 12px;
                    margin: 15px 0;
                    border-radius: 3px;
                }}
                .pregunta-usuario {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-left: 4px solid #3498db;
                    margin: 15px 0;
                }}
                .respuesta-modelo {{
                    white-space: pre-wrap;
                    background-color: #fef9e7;
                    padding: 20px;
                    border: 1px solid #f1c40f;
                    margin: 20px 0;
                    line-height: 1.5;
                    font-family: monospace;
                }}
                .estado-sistema {{
                    background-color: #2c3e50;
                    color: #ecf0f1;
                    padding: 12px;
                    font-size: 12px;
                    margin: 15px 0;
                }}
                textarea {{
                    width: 98%;
                    height: 100px;
                    font-family: monospace;
                    padding: 10px;
                }}
                .btn-enviar {{
                    background-color: #9b59b6;
                    color: white;
                    padding: 12px 25px;
                    border: none;
                    cursor: pointer;
                    font-family: monospace;
                }}
                .btn-nuevo {{
                    background-color: #e74c3c;
                    color: white;
                    padding: 8px 15px;
                    text-decoration: none;
                    display: inline-block;
                }}
            </style>
        </head>
        <body>
            <div class="marco">
                <div style="text-align: right; margin-bottom: 15px;">
                    <a href="/" class="btn-nuevo">🧹 NUEVO DIÁLOGO</a>
                </div>
                
                <h2>⚡ RESPUESTA GENERADA</h2>
                
                <div class="info-respuesta">
                    🧠 <strong>Modelo:</strong> {modelo_utilizado} | ⏱️ <strong>Tiempo:</strong> {round(tiempo_respuesta, 1)}s
                </div>
                
                <div class="pregunta-usuario">
                    <strong>TU CONSULTA ONTOLÓGICA:</strong><br>
                    {pregunta}
                </div>
                
                <div class="respuesta-modelo">
                    <strong>RESPUESTA DEL LOGOS:</strong><br>
                    {texto_respuesta}
                </div>
                
                <div class="estado-sistema">
                    {estado_conexion} | Contexto estimado: ~{porcentaje_contexto}% utilizado<br>
                    <small>Router Dinámico: openrouter/free | Formato: Texto Plano Puro</small>
                </div>
                
                <hr style="border: 1px dashed #bdc3c7; margin: 25px 0;">
                
                <form method="POST" action="/consulta">
                    <textarea name="pregunta" placeholder="Profundiza en el diálogo ontológico..." required></textarea><br><br>
                    <input type="submit" value="CONTINUAR CONSULTA" class="btn-enviar">
                </form>
                
                <div style="text-align: center; margin-top: 25px; font-size: 12px; color: #7f8c8d;">
                    <a href="/">🏠 Interfaz Principal</a>
                </div>
            </div>
        </body>
        </html>
        '''

    except requests.exceptions.Timeout:
        tiempo_total = time.time() - inicio_tiempo
        return f'''
        <div class="marco">
            <h2>⏱️ Timeout del Modelo</h2>
            <p>El router gratuito de OpenRouter excedió el tiempo límite (90s).</p>
            <p><strong>Tiempo transcurrido:</strong> {round(tiempo_total, 1)} segundos</p>
            <p><a href="/">← Volver a la interfaz principal</a></p>
        </div>
        '''
    except Exception as error_general:
        return f'''
        <div class="marco">
            <h2>⚠️ Error del Sistema</h2>
            <p>Excepción capturada:</p>
            <pre style="background: #f8f9fa; padding: 15px; border: 1px solid #dee2e6;">{str(error_general)}</pre>
            <p><a href="/">← Volver a la interfaz principal</a></p>
        </div>
        '''

if __name__ == '__main__':
    puerto = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=puerto, debug=False)
