#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Wrapper web app (based on Flask) for runLighthouse.py
    (1) uploading a csv file with URLs
    (2) running the measurement for all URLs in the csv file
    (3) displaying the KPI
    Input: csv file of a list of URLs for the measurement (name; url; ...) """


from flask import Flask, render_template, request, redirect, url_for, Markup
application = Flask(__name__)

import os
from pathlib import Path
import concurrent.futures

from runLighthouse import *


# Upload folder
UPLOAD_FOLDER = 'static/files'
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@application.route("/")
def index():
    return render_template("index.html")

@application.route("/result")
def outputKpi():
    with open('kpi.txt', 'r') as fnHandle:
        outStr = fnHandle.read()
        if not outStr: outStr = 'Please, <a href="/upload">upload</a> a csv file.'
    return render_template("result.html", outStr = Markup(outStr))

@application.route("/upload")
def upload():
     # Set The upload HTML template 'templates/upload.html'
    return render_template("upload.html")

@application.route("/upload", methods=['POST'])
def uploadUrls():
    with open('status.txt', 'w') as fnHandle:
        print("Starting", file=fnHandle)
    #
    uploaded_file = request.files['file']
    if uploaded_file.filename != '':
        if not Path(application.config['UPLOAD_FOLDER']).exists(): 
            Path(application.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)
        for csvFn in Path(application.config['UPLOAD_FOLDER']).rglob("*.csv"): csvFn.unlink()
        file_path = os.path.join(application.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(file_path)
    for f in Path(application.config['UPLOAD_FOLDER']).rglob('*.csv'):
        urlFile = f.as_posix()
        runl = runLighthouse(urlFile)
        # At the moment only one csv file is relevant
        future_csvFilename = {concurrent.futures.ThreadPoolExecutor(max_workers=1).submit(runl.calcKpi): urlFile}
    return render_template("working.html")

@application.route("/getStatus")
def getStatus():
    with open('status.txt', 'r') as fnHandle:
        return fnHandle.read()
    # return session["status"]

if __name__ == "__main__":
    application.run(host = '0.0.0.0')
