from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <form method="POST" action="/consulta">
        <input type="text" name="pregunta">
        <button>Enviar</button>
    </form>
    '''

@app.route('/consulta', methods=['POST'])
def consulta():
    pregunta = request.form.get('pregunta', 'Sin pregunta')
    
    # ¡SOLO PARA TEST! Respuesta estática
    respuesta = f"✅ El sistema funciona. Recibí: '{pregunta}'"
    estado = "[TEST: Todo OK - Template renderizado]"
    
    # Template HTML SIMPLE con variables directamente
    html = f'''
    <html>
    <body>
        <h3>Pregunta:</h3>
        <p>{pregunta}</p>
        <h3>Respuesta:</h3>
        <pre>{respuesta}</pre>
        <h3>Estado:</h3>
        <p>{estado}</p>
        <a href="/">Otra pregunta</a>
    </body>
    </html>
    '''
    
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
