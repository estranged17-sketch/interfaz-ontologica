#!/usr/bin/env python3
"""
traductor.py - El Atman / Servidor Puente de la Interfaz Ontológica Unificada.
Funcion: Traduce consultas HTTP POST a la API de DeepSeek y devuelve HTML plano.
Incluye Meta-Marco, cálculo de % de contexto y gestión de sesión.
"""

from flask import Flask, request, render_template_string, session
import requests
import os
import math
from datetime import timedelta

#  ========== CONFIGURACIÓN (¡EDITA AQUÍ!) ==========
DEEPSEEK_API_KEY = "Deepseek_API"  # 🚨 OBTÉN EN: https://platform.deepseek.com/api_keys
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

# Configuración del modelo y contexto
MODELO_IA = "deepseek-chat"           # Modelo a usar
LIMITE_CONTEXTO_TOKENS = 128000       # Límite de contexto del modelo (en tokens)
# =============================================

app = Flask(__name__)
# Una clave secreta para las sesiones. En producción, usa una clave fija y segura.
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(hours=3)  # Sesión dura 3 horas

# ----- META MARCO (Instrucción de Sistema OCULTA) -----
# Se envía con CADA consulta para formatear la respuesta.
META_MARCO = f"""Eres un asistente accesible desde terminales de texto y navegadores web muy antiguos (como Lynx o el de Nintendo Wii).

**INSTRUCCIONES ESTRICTAS DE FORMATO:**
1.  Responde **ÚNICAMENTE en texto plano puro**. No uses markdown, ni negritas, ni cursivas, ni emojis, ni bloques de código con ```.
2.  Usa saltos de línea sencillos (\\n) para separar párrafos. No uses guiones o asteriscos para listas.
3.  Sé conciso por defecto. Extiende la respuesta solo si la complejidad de la pregunta lo requiere.
4.  **Al final de cada respuesta**, en una línea nueva y separada, añade **exactamente** esta línea de estado:
    [Estado del Contexto: ~{{porcentaje}}% usado | {{tokens_aprox}}K tokens aprox. | Límite: {LIMITE_CONTEXTO_TOKENS//1000}K]

**Tu objetivo:** Facilitar el acceso al conocimiento desde hardware obsoleto. La claridad y compatibilidad son primordiales.
"""

# ----- HTML de RESPUESTA -----
HTML_RESPUESTA = """
<!DOCTYPE html>
<html>
<head>
    <title>Respuesta del Logos</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: monospace; max-width: 900px; margin: auto; padding: 20px; }
        .nuevo-chat-btn {{
            position: fixed; top: 15px; right: 15px;
            padding: 8px 15px; background: #f0f0f0; border: 1px solid #ccc; cursor: pointer;
        }}
        .consulta {{ background: #f8f8f8; padding: 15px; border-left: 4px solid #ccc; }}
        .respuesta {{ white-space: pre-wrap; word-wrap: break-word; line-height: 1.5; }}
        .estado {{ font-size: 0.9em; color: #555; margin-top: 20px; padding: 10px; background: #eee; }}
        a {{ color: #0066cc; }}
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
</html>
"""

# ----- FUNCIONES AUXILIARES -----
def estimar_tokens(texto):
    """Estimación MUY aproximada: 1 token ~ 4 caracteres en español."""
    return len(texto) / 4

def calcular_estado_contexto(historial_texto):
    """Calcula el % aproximado usado y genera un texto de estado."""
    if not historial_texto:
        return 0.0, "Estado del Contexto: ~0% usado | 0K tokens aprox. | Nueva conversación."
    tokens_estimados = estimar_tokens(historial_texto)
    porcentaje = min(99.9, (tokens_estimados / LIMITE_CONTEXTO_TOKENS) * 100)
    texto_estado = f"[Estado del Contexto: ~{porcentaje:.1f}% usado | {tokens_estimados/1000:.1f}K tokens aprox. | Límite: {LIMITE_CONTEXTO_TOKENS//1000}K]"
    # Advertencia si nos acercamos al límite
    if porcentaje > 80:
        texto_estado += "\n⚠️  El contexto se está llenando. Considera usar 'Nuevo Chat' pronto."
    elif porcentaje > 95:
        texto_estado += "\n🚨 Contexto casi lleno. Las respuestas más antiguas se perderán. Usa 'Nuevo Chat'."
    return porcentaje, texto_estado

# ----- RUTAS PRINCIPALES -----
@app.route('/')
def home():
    """Página principal con el formulario. Inicializa la sesión."""
    if 'historial' not in session:
        session['historial'] = ""
    # Devolvemos un HTML simple embebido, sin leer archivo.
    html_base = """
    <!DOCTYPE html>
    <html>
    <head><title>Consulta</title><meta charset="UTF-8"></head>
    <body>
        <h1>Consulta al Logos</h1>
        <p>El servidor puente (Atman) está funcionando.</p>
        <p><a href="{url_netlify}">Accede a la Interfaz Completa (Jiva)</a></p>
        <p><i>Esta es solo la API del backend. Usa el enlace de arriba para la interfaz de usuario.</i></p>
    </body>
    </html>
    """
    # Reemplaza {url_netlify} con la URL que tendrá tu frontend (una vez lo subas a Netlify)
    return html_base.format(url_netlify="https://vocal-cobbler-7a48f5.netlify.app/")

@app.route('/consulta', methods=['POST'])
def consultar():
    """El endpoint principal: procesa la consulta y devuelve la respuesta."""
    pregunta_usuario = request.form.get('pregunta', '').strip()
    if not pregunta_usuario:
        return "Error: No se recibió una pregunta.", 400

    # 1. GESTIONAR HISTORIAL Y CALCULAR ESTADO
    historial = session.get('historial', '')
    # Añadir la nueva pregunta al historial para el cálculo
    historial_para_calculo = historial + f"\nUsuario: {pregunta_usuario}"
    porcentaje, texto_estado = calcular_estado_contexto(historial_para_calculo)

    # 2. PREPARAR LA CONSULTA PARA DEEPSEEK
    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json'
    }
    # Insertamos el % calculado en el Meta Marco que se envía a la IA
    meta_marco_actualizado = META_MARCO.format(porcentaje=f"{porcentaje:.1f}", tokens_aprox=f"{(estimar_tokens(historial_para_calculo))/1000:.1f}")
    data = {
        "model": MODELO_IA,
        "messages": [
            {"role": "system", "content": meta_marco_actualizado},
            {"role": "user", "content": pregunta_usuario}
        ],
        "stream": False  # Respuesta completa de una vez
    }

    # 3. LLAMAR A LA API DE DEEPSEEK
    try:
        respuesta_api = requests.post(DEEPSEEK_API_URL, json=data, headers=headers, timeout=90)
        respuesta_api.raise_for_status()
        respuesta_json = respuesta_api.json()
        texto_respuesta = respuesta_json['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        texto_respuesta = f"❌ Error de conexión con la IA:\n{str(e)}"
    except KeyError as e:
        texto_respuesta = f"⚠️  La respuesta de la IA tuvo un formato inesperado.\nError: {e}"

    # 4. ACTUALIZAR HISTORIAL DE LA SESIÓN (con la respuesta)
    # Limitamos el historial guardado para no inflar la sesión (~10K chars)
    nuevo_bloque = f"U: {pregunta_usuario[:500]}\nA: {texto_respuesta[:2000]}"
    session['historial'] = (historial + "\n" + nuevo_bloque)[-10000:]

    # 5. RENDERIZAR Y DEVOLVER LA RESPUESTA HTML
    return render_template_string(HTML_RESPUESTA,
                                  pregunta=pregunta_usuario,
                                  respuesta=texto_respuesta,
                                  estado=texto_estado)

@app.route('/limpiar')
def limpiar_sesion():
    """Borra el historial de la sesión y redirige a la página principal (Nuevo Chat)."""
    session.pop('historial', None)
    return '<script>alert("Conversación reiniciada."); window.location.href = "/";</script>'

# ----- PUNTO DE ENTRADA -----
if __name__ == '__main__':
    # Para ejecutar localmente: `python traductor.py`
    app.run(host='0.0.0.0', port=10000, debug=True)
