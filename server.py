from flask import Flask, render_template, send_from_directory, abort, request
import os

app = Flask(__name__)
app.config['SUSPECTS_FOLDER'] = os.path.join(app.root_path, 'suspeitos')
app.config['IMAGE_FOLDER'] = os.path.join(app.root_path, 'images')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/contato')
def contato():
    return render_template('contato.html')

@app.route('/casos')
def casos():
    return render_template('casos.html')

@app.route('/casos/hack_x')
def caso_hack():
    return render_template('ocaso.html')

@app.route('/casos/hack_x/<susp>')
def suspeito_caso_hack(susp):
    suspect_id = susp
    suspect_name = ''
    suspect_path = os.path.join(app.config['SUSPECTS_FOLDER'], susp)
    if not os.path.exists(suspect_path): abort(404)
    suspect_files = os.listdir(suspect_path)
    return render_template('suspect.html', id=suspect_id, name=suspect_name, files=suspect_files)

@app.route('/casos/hack_x/<susp>/<filename>')
def file_suspeito_caso_hack(susp, filename):
    suspect_path = os.path.join(app.config['SUSPECTS_FOLDER'], susp)
    if not os.path.exists(suspect_path): abort(404)
    return send_from_directory(suspect_path, filename)


# @app.route('/images/<filename>')
# def serve_image(filename):
#     return send_from_directory(app.config['IMAGE_FOLDER'], filename)

# # Rota para listar e exibir todas as imagens
# @app.route('/images')
# def list_images():
#     # Lista todos os arquivos na pasta de imagens
#     image_names = os.listdir(app.config['IMAGE_FOLDER'])
#     return render_template('images.html', images=image_names)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', requested_url=request.path), 404

if __name__ == '__main__':
    app.run(debug=True)