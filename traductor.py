#!/usr/bin/env python3
"""
traductor.py - El Atman / Servidor Puente de la Interfaz Ontológica Unificada.
Funcion: Traduce consultas HTTP POST a la API de DeepSeek y devuelve HTML plano.
Incluye Meta-Marco, cálculo de % de contexto y gestión de sesión.
VERSION CORREGIDA - Template Jinja2 funcional.
"""

from flask import Flask, request, render_template_string, session
import requests
import os
from datetime import timedelta

#  ========== CONFIGURACIÓN ==========
# La API Key se configura en Render como variable de entorno: DEEPSEEK_API_KEY
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
MODELO_IA = "deepseek-chat"
LIMITE_CONTEXTO_TOKENS = 128000
# =============================================

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(hours=3)

# ----- META MARCO (Instrucción de Sistema OCULTA) -----
META_MARCO = f"""Eres un asistente accesible desde terminales de texto y navegadores web muy antiguos (como Lynx o el de Nintendo Wii).

**INSTRUCCIONES ESTRICTAS DE FORMATO:**
1.  Responde **ÚNICAMENTE en texto plano puro**. No uses markdown, ni negritas, ni cursivas, ni emojis, ni bloques de código con ```.
2.  Usa saltos de línea sencillos (\\n) para separar párrafos. No uses guiones o asteriscos para listas.
3.  Sé conciso por defecto. Extiende la respuesta solo si la complejidad de la pregunta lo requiere.
4.  **Al final de cada respuesta**, en una línea nueva y separada, añade **exactamente** esta línea de estado:
    [Estado del Contexto: ~{{porcentaje}}% usado | {{tokens_aprox}}K tokens aprox. | Límite: {LIMITE_CONTEXTO_TOKENS//1000}K]

**Tu objetivo:** Facilitar el acceso al conocimiento desde hardware obsoleto. La claridad y compatibilidad son primordiales.
"""

# ----- HTML de RESPUESTA (CORREGIDO) -----
HTML_RESPUESTA = """<!DOCTYPE html>
<html>
<head>
    <title>Respuesta del Logos</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: monospace; max-width: 900px; margin: auto; padding: 20px; }
        .nuevo-chat-btn {
            position: fixed; top: 15px; right: 15px;
            padding: 8px 15px; background: #f0f0f0; border: 1px solid #ccc; cursor: pointer;
        }
        .consulta { background: #f8f8f8; padding: 15px; border-left: 4px solid #ccc; }
        .respuesta { white-space: pre-wrap; word-wrap: break-word; line-height: 1.5; }
        .estado { font-size: 0.9em; color: #555; margin-top: 20px; padding: 10px; background: #eee; }
        a { color: #0066cc; }
    </style>
</head>
<body>
    <input type="button" class="nuevo-chat-btn" value="🧹 Nuevo Chat" onclick="location.href='/limpiar'" title="Reinicia la conversación">
    <h2>⚡ Respuesta Generada</h2>
    <div class="consulta">
        <strong>Tu consulta:</strong><br>
        {pregunta}
    </div>
    <div class="respuesta">
        <strong>Respuesta:</strong><br>
        {respuesta}
    </div>
    <div class="estado">
        {estado}
    </div>
    <hr>
    <p><a href="/">← Hacer otra consulta en este mismo hilo</a></p>
</body>
</html>"""

# ----- FUNCIONES AUXILIARES -----
def estimar_tokens(texto):
    return len(texto) / 4

def calcular_estado_contexto(historial_texto):
    if not historial_texto:
        return 0.0, "Estado del Contexto: ~0% usado | 0K tokens aprox. | Nueva conversación."
    tokens_estimados = estimar_tokens(historial_texto)
    porcentaje = min(99.9, (tokens_estimados / LIMITE_CONTEXTO_TOKENS) * 100)
    texto_estado = f"[Estado del Contexto: ~{porcentaje:.1f}% usado | {tokens_estimados/1000:.1f}K tokens aprox. | Límite: {LIMITE_CONTEXTO_TOKENS//1000}K]"
    if porcentaje > 80:
        texto_estado += "\n⚠️  El contexto se está llenando. Considera usar 'Nuevo Chat' pronto."
    elif porcentaje > 95:
        texto_estado += "\n🚨 Contexto casi lleno. Las respuestas más antiguas se perderán. Usa 'Nuevo Chat'."
    return porcentaje, texto_estado

# ----- RUTAS PRINCIPALES -----
@app.route('/')
def home():
    if 'historial' not in session:
        session['historial'] = ""
    # Página simple para confirmar que el backend funciona
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Atman - Servidor Puente</title><meta charset="UTF-8"></head>
    <body>
        <h1>✅ Atman (Servidor Puente) funcionando</h1>
        <p>Este es el backend de la Interfaz Ontológica Unificada.</p>
        <p>Para usar la interfaz, visita el frontend en Netlify.</p>
        <p><a href="https://vocal-cobbler-7a48f5.netlify.app">Acceder al Frontend (Jiva)</a></p>
    </body>
    </html>
    """

@app.route('/consulta', methods=['POST'])
def consultar():
    pregunta_usuario = request.form.get('pregunta', '').strip()
    if not pregunta_usuario:
        return "Error: No se recibió una pregunta.", 400

    historial = session.get('historial', '')
    historial_para_calculo = historial + f"\nUsuario: {pregunta_usuario}"
    porcentaje, texto_estado = calcular_estado_contexto(historial_para_calculo)

    # Obtener API Key de variable de entorno (Render)
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if not api_key:
        texto_respuesta = "Error: API Key no configurada en el servidor."
    else:
        headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
        meta_marco_actualizado = META_MARCO.format(porcentaje=f"{porcentaje:.1f}", tokens_aprox=f"{(estimar_tokens(historial_para_calculo))/1000:.1f}")
        data = {
            "model": MODELO_IA,
            "messages": [
                {"role": "system", "content": meta_marco_actualizado},
                {"role": "user", "content": pregunta_usuario}
            ],
            "stream": False
        }
        try:
            respuesta_api = requests.post(DEEPSEEK_API_URL, json=data, headers=headers, timeout=90)
            respuesta_api.raise_for_status()
            texto_respuesta = respuesta_api.json()['choices'][0]['message']['content']
        except requests.exceptions.RequestException as e:
            texto_respuesta = f"❌ Error de conexión con la IA:\n{str(e)}"
        except KeyError as e:
            texto_respuesta = f"⚠️  La respuesta de la IA tuvo un formato inesperado.\nError: {e}"

    nuevo_bloque = f"U: {pregunta_usuario[:500]}\nA: {texto_respuesta[:2000]}"
    session['historial'] = (historial + "\n" + nuevo_bloque)[-10000:]

    return render_template_string(HTML_RESPUESTA,
                                  pregunta=pregunta_usuario,
                                  respuesta=texto_respuesta,
                                  estado=texto_estado)

@app.route('/limpiar')
def limpiar_sesion():
    session.pop('historial', None)
    return '<script>alert("Conversación reiniciada."); window.location.href = "/";</script>'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
