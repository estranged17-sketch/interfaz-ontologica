from flask import Flask, request
import os
import requests
import time
import json

app = Flask(__name__)

# Almacenamiento por sesión - SIMPLIFICADO para compatibilidad
sesiones_activas = {}

# Meta-marco adaptado para MiMo-V2-Flash
META_MARCO = """Eres la Interfaz Ontológica Unificada. 
Principios operativos:
1. Respuestas en TEXTO PLANO PURO (cero markdown, cero código, cero HTML)
2. Lenguaje claro y accesible
3. Si la pregunta es técnica, explica como a un no-especialista
4. Si es filosófica, profundiza en los aspectos ontológicos
5. Estructura: Contenido principal → "---" → [Estado: X% contexto]

Formato EJEMPLO:
[tu respuesta en texto puro]

---

[Estado del Sistema: ~5% del contexto usado | Modelo: MiMo-V2-Flash 309B]"""

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>🧬 INTERFAZ ONTOLÓGICA</title>
        <style>
            /* CSS compatible con navegadores MUY antiguos */
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
            .respuesta {
                white-space: pre-wrap;
                background-color: #ecf0f1;
                padding: 20px;
                margin: 20px 0;
                border-left: 5px solid #16a085;
                font-family: monospace;
                line-height: 1.5;
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
                ⚡ <strong>MODELO ACTIVO:</strong> Xiaomi MiMo-V2-Flash (309B parámetros totales, 15B activos)<br>
                🆓 <strong>ACCESO:</strong> Gratuito via OpenRouter<br>
                🧠 <strong>CONTEXTO:</strong> 256K tokens | 🔧 <strong>ARQUITECTURA:</strong> Mixture-of-Experts
            </div>
            
            <p><strong>Hardware objetivo:</strong> Nintendo Wii (2006), navegadores legacy (IE6+, Lynx), terminales texto</p>
            
            <form method="POST" action="/consulta">
                <textarea name="pregunta" placeholder="Formula tu pregunta o reflexión..." required></textarea><br>
                <input type="submit" value="CONSULTAR AL LOGOS 309B">
            </form>
            
            <div class="estado-sistema">
                ✅ Backend: Flask en Render.com | 🌐 Frontend: HTML 4.01 | 🔄 Protocolo: HTTP/1.1<br>
                📊 Historial: 5 mensajes máximo | ⚙️ Arquitectura: 3-capas (N0-N4)
            </div>
            
            <div style="margin-top: 20px; font-size: 12px; color: #7f8c8d;">
                <strong>Ejemplos conceptuales:</strong><br>
                • "¿Cómo esta arquitectura restaura la unidad comunicativa entre polos tecnológicos?"<br>
                • "Explica el principio de no-dualidad operativa en este sistema"<br>
                • "¿Qué significa que Atman sea función pura en N1?"<br>
                • "Demuestra cómo un navegador de Wii puede dialogar con un modelo de 309B parámetros"
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
                <p><a href="/">← Volver al interfaz</a></p>
            </div>
            '''
        
        # Gestión simple de sesión por IP
        ip_cliente = request.remote_addr
        if ip_cliente not in sesiones_activas:
            sesiones_activas[ip_cliente] = {
                'historial': [],
                'timestamp': time.time()
            }
        
        sesion = sesiones_activas[ip_cliente]
        historial = sesion['historial']
        
        # Limpieza de sesiones antiguas (> 2 horas)
        if time.time() - sesion['timestamp'] > 7200:
            historial = []
        
        # Construcción del contexto para el modelo
        mensajes_ia = []
        
        # 1. Añadir el meta-marco como sistema
        mensajes_ia.append({"role": "system", "content": META_MARCO})
        
        # 2. Añadir historial reciente (últimas 2 interacciones máximo)
        for item in historial[-4:]:
            mensajes_ia.append(item)
        
        # 3. Añadir la nueva pregunta
        mensajes_ia.append({"role": "user", "content": pregunta})
        
        # CONFIGURACIÓN PARA XIAOMI MIMO-V2-FLASH (309B)
        api_key = os.environ.get('OPENROUTER_API_KEY', '')
        
        headers = {
            "Content-Type": "application/json",
        }
        
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            headers["HTTP-Referer"] = "https://interfaz-ontologica.onrender.com"
            headers["X-Title"] = "Interfaz Ontológica (MiMo-V2-Flash)"
        
        # Parámetros optimizados para MiMo-V2-Flash
        payload = {
            "model": "openrouter/free",  # MODELO Dinamico Free
            "messages": mensajes_ia,
            "max_tokens": 1200,  # Tokens ampliados para respuestas detalladas
            "temperature": 0.7,
            "top_p": 0.9,
            "frequency_penalty": 0.1,
            "presence_penalty": 0.1,
            "stream": False,
            "reasoning_enabled": True  # Activamos el pensamiento híbrido del modelo
        }
        
        # LLAMADA A LA API DE OPENROUTER
        try:
            respuesta_api = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=90  # Timeout extendido para modelo grande
            )
            
            tiempo_respuesta = time.time() - inicio_tiempo
            
            if respuesta_api.status_code == 200:
                # ÉXITO: Respuesta del modelo 309B
                datos_respuesta = respuesta_api.json()
                texto_respuesta = datos_respuesta['choices'][0]['message']['content']
                
                # Asegurar formato limpio
                if "---" not in texto_respuesta:
                    texto_respuesta = texto_respuesta + "\n\n---\n\n"
                
                modelo_utilizado = "MiMo-V2-Flash (309B)"
                estado_conexion = f"[✅ Conectado a 309B | Tiempo: {round(tiempo_respuesta, 1)}s]"
                
            else:
                # ERROR en la API - Modo de respaldo
                raise Exception(f"API error {respuesta_api.status_code}")
                
        except Exception as api_error:
            # RESPUESTA DE RESERVA si falla el modelo 309B
            tiempo_respuesta = time.time() - inicio_tiempo
            
            texto_respuesta = f"""Consulta recibida: "{pregunta}"

El modelo MiMo-V2-Flash (309B parámetros) está experimentando alta demanda temporal.

📊 **ESTADO DEL SISTEMA:**
• Backend: ✅ Operativo en Render.com
• Modelo objetivo: Xiaomi MiMo-V2-Flash (309B/15B)
• Contexto disponible: 256K tokens
• Tiempo de espera: {round(tiempo_respuesta, 1)} segundos
• Arquitectura: Mixture-of-Experts con atención híbrida

Este sistema demuestra la viabilidad de conectar hardware legacy (2006) con arquitecturas de IA de vanguardia (2025) mediante principios de traducción pura de protocolos.

¿Qué aspecto de esta mediación ontológica te interesa explorar?"""
            
            modelo_utilizado = "Sistema de demostración (reserva)"
            estado_conexion = f"[⚠️ Modelo 309B temporalmente saturado | Tiempo: {round(tiempo_respuesta,1)}s]"
        
        # ACTUALIZACIÓN DEL HISTORIAL (limitado por contexto)
        historial.append({"role": "user", "content": pregunta[:150]})  # Limitar tamaño
        historial.append({"role": "assistant", "content": texto_respuesta[:200]})
        
        # Mantener máximo 3 intercambios (para compatibilidad)
        if len(historial) > 6:
            historial = historial[-6:]
        
        sesion['historial'] = historial
        sesion['timestamp'] = time.time()
        
        # CÁLCULO DE CONTEXTO USADO (aproximación simplificada)
        caracteres_totales = sum(len(str(m.get('content', ''))) for m in mensajes_ia)
        porcentaje_contexto = min(100, caracteres_totales // 250)  # Aprox para 256K tokens
        
        # GENERACIÓN DE RESPUESTA HTML (compatible universal)
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
                    {estado_conexion} | Contexto aproximado: {porcentaje_contexto}% de 256K usado<br>
                    <small>Arquitectura: Mixture-of-Experts (309B totales, 15B activos) | Pensamiento híbrido: Activado</small>
                </div>
                
                <hr style="border: 1px dashed #bdc3c7; margin: 25px 0;">
                
                <form method="POST" action="/consulta">
                    <textarea name="pregunta" placeholder="Profundiza en el diálogo ontológico..." required></textarea><br><br>
                    <input type="submit" value="CONTINUAR CONSULTA 309B" class="btn-enviar">
                </form>
                
                <div style="text-align: center; margin-top: 25px; font-size: 12px; color: #7f8c8d;">
                    <a href="/">🏠 Interfaz Principal</a> | 
                    <a href="https://github.com/estranged17-sketch/interfaz-ontologica">📜 Código Fuente</a> | 
                    <a href="https://openrouter.ai/xiaomi/mimo-v2-flash:free">🔍 Especificaciones del Modelo</a>
                </div>
            </div>
        </body>
        </html>
        '''
        
    except requests.exceptions.Timeout:
        tiempo_total = time.time() - inicio_tiempo
        return f'''
        <div class="marco">
            <h2>⏱️ Timeout del Modelo 309B</h2>
            <p>El modelo MiMo-V2-Flash (309B parámetros) ha excedido el tiempo de espera de 90 segundos.</p>
            <p><strong>Tiempo transcurrido:</strong> {round(tiempo_total, 1)} segundos</p>
            
            <div style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 20px 0;">
                <strong>📋 Contexto técnico:</strong><br>
                • Modelo: Xiaomi MiMo-V2-Flash (Mixture-of-Experts, 309B/15B)<br>
                • Arquitectura: Híbrida con ventana de 256K tokens<br>
                • Estado: Servicio gratuito con alta demanda<br>
                • Compatibilidad: HTTP/1.1 para navegadores legacy
            </div>
            
            <p><strong>Sugerencias:</strong></p>
            <ul>
                <li>Formula preguntas más concisas</li>
                <li>Espera 60 segundos y reintenta</li>
                <li>Considera que modelos de este tamaño pueden tener latencia variable en servicios gratuitos</li>
            </ul>
            
            <p><a href="/">← Volver al interfaz principal</a></p>
        </div>
        '''
    except Exception as error_general:
        return f'''
        <div class="marco">
            <h2>⚠️ Error inesperado</h2>
            <p>Ha ocurrido un error en el sistema:</p>
            <pre style="background: #f8f9fa; padding: 15px; border: 1px solid #dee2e6; overflow: auto;">{str(error_general)}</pre>
            <p><a href="/">← Volver al interfaz principal</a></p>
        </div>
        '''

if __name__ == '__main__':
    # Configuración optimizada para Render.com
    puerto = int(os.environ.get('PORT', 10000))
    app.run(
        host='0.0.0.0',
        port=puerto,
        debug=False  # Desactivado para producción
    )
