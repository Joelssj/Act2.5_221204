from flask import Flask, request, render_template_string
import os
import re

app = Flask(__name__)
DIRECTORIO_ARCHIVOS = 'archivos/'
if not os.path.exists(DIRECTORIO_ARCHIVOS):
    os.makedirs(DIRECTORIO_ARCHIVOS)
app.config['DIRECTORIO_ARCHIVOS'] = DIRECTORIO_ARCHIVOS

codigo_correcto = '''<html>

<head></head>

<body>
   <?php
   echo "Hola mundo";
   ?>
</body>

</html>'''

def normalizar_codigo(codigo):
    return re.sub(r'\s+', '', codigo)

def analisis_lexico(codigo):
    resultado = []
    palabras_clave = {'echo', 'if', 'else', 'while', 'for', 'function', 'return'}
    simbolos = {';', '{', '}', '(', ')', '=', '>', '<', '+', '-', '*', '/'}
    lineas = codigo.split('\n')
    for numero_linea, linea in enumerate(lineas, start=1):
        tokens = re.findall(r'\b\w+\b|[{}();=><+\-*/]', linea)
        for token in tokens:
            if token in palabras_clave:
                resultado.append((numero_linea, 'Palabra clave', token))
            elif token in simbolos:
                resultado.append((numero_linea, 'Símbolo', token))
            elif token.isdigit():
                resultado.append((numero_linea, 'Número', token))
            else:
                resultado.append((numero_linea, 'Identificador', token))
    return resultado

def analisis_sintactico(codigo):
    errores = []
    lineas_correctas = codigo_correcto.split('\n')
    lineas_codigo = codigo.split('\n')
    
    dentro_php = False
    lineas_correctas_filtradas = []
    lineas_codigo_filtradas = []

    for linea_correcta, linea_codigo in zip(lineas_correctas, lineas_codigo):
        if '<?php' in linea_correcta or '?>' in linea_correcta:
            dentro_php = not dentro_php
            continue
        if not dentro_php:
            lineas_correctas_filtradas.append(linea_correcta)
            lineas_codigo_filtradas.append(linea_codigo)
    
    for numero_linea, (linea_correcta, linea_codigo) in enumerate(zip(lineas_correctas_filtradas, lineas_codigo_filtradas), start=1):
        if normalizar_codigo(linea_correcta) != normalizar_codigo(linea_codigo):
            errores.append((numero_linea, f"Código incorrecto en la línea {numero_linea}: se esperaba '{linea_correcta.strip()}', pero se encontró '{linea_codigo.strip()}'."))
    
    if len(lineas_correctas_filtradas) != len(lineas_codigo_filtradas):
        errores.append((len(lineas_codigo), f"Error de longitud: se esperaban {len(lineas_correctas_filtradas)} líneas, pero se encontraron {len(lineas_codigo_filtradas)} líneas."))
    
    if errores:
        return [(error[0], error[1], False) for error in errores]
    else:
        return [(0, "Código correcto", True)]

def analisis_semantico(codigo):
    errores = []
    lineas = codigo.split('\n')
    if "<?php" not in codigo:
        errores.append((0, "Error semántico, la abertura de php está mal implementada."))
    if "?>" not in codigo:
        errores.append((0, "Error semántico. El cierre de PHP está mal implementado."))
    for numero_linea, linea in enumerate(lineas, start=1):
        if 'echo' in linea and 'echo "Hola mundo";' not in linea:
            errores.append((numero_linea, "Error semántico, ha de faltar un punto y coma, le falta comillas o la palabra echo está mal escrita."))
    if errores:
        return [(error[0], error[1], False) for error in errores]
    else:
        return [(0, "No hay errores semánticos", True)]

@app.route('/', methods=['GET', 'POST'])
def index():
    codigo = ""
    resultado_lexico = []
    resultado_sintactico = []
    resultado_semantico = []
    if request.method == 'POST':
        if 'archivo' in request.files and request.files['archivo'].filename != '':
            archivo = request.files['archivo']
            ruta_archivo = os.path.join(app.config['DIRECTORIO_ARCHIVOS'], archivo.filename)
            archivo.save(ruta_archivo)
            with open(ruta_archivo, 'r') as f:
                codigo = f.read()
        elif 'codigo' in request.form and request.form['codigo'].strip() != '':
            codigo = request.form['codigo']

        resultado_lexico = analisis_lexico(codigo)
        resultado_sintactico = analisis_sintactico(codigo)
        resultado_semantico = analisis_semantico(codigo)

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background-color: #f0f0f5;
                color: #333;
                display: flex;
                flex-direction: row;
                align-items: flex-start;
                justify-content: center;
                min-height: 100vh;
                margin: 0;
                padding: 20px;
            }
            header {
                width: 100%;
                background-color: #4CAF50;
                color: white;
                padding: 15px;
                text-align: center;
                box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
            }
            .container {
                display: flex;
                flex-direction: row;
                width: 100%;
                margin-top: 70px;
            }
            .input-area {
                flex: 1;
                padding-right: 20px;
            }
            .results {
                flex: 1;
                padding-left: 20px;
            }
            form {
                background-color: #ffffff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
            }
            .input-group {
                margin-bottom: 15px;
            }
            .input-group label {
                display: block;
                margin-bottom: 5px;
            }
            .input-group input[type="file"],
            .input-group textarea,
            .input-group input[type="submit"] {
                width: 100%;
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 5px;
                box-sizing: border-box;
            }
            .input-group input[type="submit"] {
                background-color: #4CAF50;
                color: white;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            .input-group input[type="submit"]:hover {
                background-color: #45a049;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 20px;
            }
            table, th, td {
                border: 1px solid #ddd;
            }
            th, td {
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
            td {
                background-color: #fff;
            }
        </style>
        <title>Análisis Léxico, Sintáctico y Semántico</title>
    </head>
    <body>
        <header>
            <h1>Análisis Léxico, Sintáctico y Semántico</h1>
        </header>
        <div class="container">
            <div class="input-area">
                <form method="POST" enctype="multipart/form-data">
                    <div class="input-group">
                        <label for="archivo">Subir archivo:</label>
                        <input type="file" name="archivo">
                    </div>
                    <div class="input-group">
                        <label for="codigo">O ingrese el código aquí:</label>
                        <textarea name="codigo" rows="10" placeholder="Ingrese su código aquí...">{{ codigo }}</textarea>
                    </div>
                    <div class="input-group">
                        <input type="submit" value="Analizar">
                    </div>
                    {% if resultado_sintactico %}
                    <h2>Resultados del Análisis Sintáctico</h2>
                    <table>
                        <tr>
                            <th>Línea</th>
                            <th>Resultado</th>
                            <th>Correcto/Incorrecto</th>
                        </tr>
                        {% for linea in resultado_sintactico %}
                        <tr>
                            <td>{{ linea[0] }}</td>
                            <td>{{ linea[1] }}</td>
                            <td>{{ "✓" if linea[2] else "✗" }}</td>
                        </tr>
                        {% endfor %}
                    </table>
                    {% endif %}
                    {% if resultado_semantico %}
                    <h2>Resultados del Análisis Semántico</h2>
                    <table>
                        <tr>
                            <th>Línea</th>
                            <th>Error</th>
                            <th>Correcto/Incorrecto</th>
                        </tr>
                        {% for linea in resultado_semantico %}
                        <tr>
                            <td>{{ linea[0] }}</td>
                            <td>{{ linea[1] }}</td>
                            <td>{{ "✓" if linea[2] else "✗" }}</td>
                        </tr>
                        {% endfor %}
                    </table>
                    {% endif %}
                </form>
            </div>
            <div class="results">
                {% if resultado_lexico %}
                <h2>Resultados del Análisis Léxico</h2>
                <table>
                    <tr>
                        <th>Línea</th>
                        <th>Tipo de Token</th>
                        <th>Token</th>
                    </tr>
                    {% for linea in resultado_lexico %}
                    <tr>
                        <td>{{ linea[0] }}</td>
                        <td>{{ linea[1] }}</td>
                        <td>{{ linea[2] }}</td>
                    </tr>
                    {% endfor %}
                </table>
                {% endif %}
            </div>
        </div>
    </body>
    </html>
    """, codigo=codigo, resultado_lexico=resultado_lexico, resultado_sintactico=resultado_sintactico, resultado_semantico=resultado_semantico)

if __name__ == '__main__':
    app.run(debug=True)
