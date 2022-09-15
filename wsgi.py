""" Iniput: List of Urls for the measurement """


from flask import Flask, render_template, request, redirect, url_for
application = Flask(__name__)

import os
from pathlib import Path

from runLighthouse import *


# Upload folder
UPLOAD_FOLDER = 'static/files'
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Small web app (based on Flask) for 
# (1) uploading a csv file with URLs
# (2) running the measurement for all URLs in the csv file
# (3) displaying the KPI
@application.route("/result")
def outputKpi():
    for f in Path(application.config['UPLOAD_FOLDER']).rglob('*.csv'):
        runl = runLighthouse(f.as_posix())
        # At the moment only one csv file is relevant
        return runl.calcKpi()
    return "Please, upload a csv file."

@application.route("/")
def index():
    return render_template("index.html")

@application.route("/upload")
def upload():
     # Set The upload HTML template 'templates/upload.html'
    return render_template("upload.html")

@application.route("/upload", methods=['POST'])
def uploadUrls():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        if not Path(application.config['UPLOAD_FOLDER']).exists(): 
            Path(application.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
        for csvFn in Path(application.config['UPLOAD_FOLDER']).rglob("*.csv"): csvFn.unlink()
        file_path = os.path.join(application.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(file_path)
    return redirect(url_for('outputKpi'))

if __name__ == "__main__":
    application.run(port = 5000)
