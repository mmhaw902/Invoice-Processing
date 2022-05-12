from flask import Flask, flash, request, redirect, url_for, render_template
import os
from werkzeug.utils import secure_filename
import cv2
from almost_final import main_function

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/'

app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']

    if file.filename == '':
        flash('No image selected for uploading')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        img = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        img_encode = cv2.imencode('.JPG', img)[1]
        encoded_img = img_encode.tolist()

        output = main_function(encoded_img)

        print(output)

        for i in os.listdir(UPLOAD_FOLDER):
            os.remove(UPLOAD_FOLDER + i)

        flash('Image successfully uploaded and result is below')
        return render_template('index.html', filename=output)
    else:
        flash('Allowed image types are - png, jpg, jpeg, gif')
        return redirect(request.url)


@app.route('/display/<filename>')
def display_image():
    return redirect(url_for(), code=301)


if __name__ == "__main__":
    app.run(debug=True)
