import os, io
import base64 
from PIL import Image
import cv2
import numpy as np
from flask import Flask, render_template, request, abort
from werkzeug.utils import secure_filename
import imghdr
from image_processing.ndvi import get_ndvi, apply_gradient

if (__name__=='__main__'):
	app = Flask(__name__)
	app.config['TEMPLATES_AUTO_RELOAD'] = True
	app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 128 # 128 мегабайт - максимальный размер загружаемых файлов
	app.config['UPLOAD_EXTENSIONS'] = ['.tif']
	app.config['UPLOAD_PATH'] = 'static/process_images'

@app.route('/')
def index():
	return render_template('index.html')

def validate_image(stream):
	header = stream.read(512)
	stream.seek(0) 
	format = imghdr.what(None, header)
	if not format:
		return None
	return format

def get_uri(img):
	rawBytes = io.BytesIO()
	img.save(rawBytes, "JPEG")
	rawBytes.seek(0)
	img_base64 = base64.b64encode(rawBytes.getvalue()).decode('ascii')
	mime = "image/jpeg"
	return "data:%s;base64,%s"%(mime, img_base64)

@app.route('/', methods=['POST'])
def upload_files():
	files = request.files.getlist('file')
	filenames = []
	if (request.files['file'].filename == ''): # Нет файлов
		return ('', 204)
	for uploaded_file in files:
		filename = secure_filename(uploaded_file.filename)
		if filename != '':
			filenames.append(filename)
			file_ext = os.path.splitext(filename)[1]
			if file_ext not in app.config['UPLOAD_EXTENSIONS'] or \
					file_ext != validate_image(uploaded_file.stream):
				abort(400)
			npimg = np.fromstring(uploaded_file.read(),np.uint8)
			img = cv2.cvtColor(cv2.imdecode(npimg,cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
			img = Image.fromarray(img.astype("uint8"))
			if "B4" in filename:
				red_img = Image.open(uploaded_file.stream)
			if "B3" in filename:
				nir_img = Image.open(uploaded_file.stream)

	if red_img == None or nir_img == None:
		 abort(400)

	ndvi = get_ndvi(nir_img, red_img)
	result_greyscale = (ndvi + 1.)/2. #greyscale
	result = apply_gradient(result_greyscale)

	return render_template('result.html', result=get_uri(Image.fromarray(result.astype("uint8"))))

if (__name__=='__main__'):
	app.run(debug=True, use_reloader=False)
