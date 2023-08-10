from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, url_for
import os
import cv2

app = Flask(__name__)

@app.after_request
def add_cache_control(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Set the path for the uploads and processed images folders
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOADS_FOLDER = os.path.join(APP_ROOT, 'static/images')
PROCESSED_FOLDER = os.path.join(APP_ROOT, 'static/images')

face_cascade = cv2.CascadeClassifier('haar/haarcascade_frontalface.xml') 
profile_cascade = cv2.CascadeClassifier('haar/haarcascade_profile.xml')

# default access page
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/indexcloud")
def indexcloud():
    return render_template('indexcloud.html')

@app.route("/indexfire")
def indexfire():
    return render_template('indexfire.html')

@app.route("/indexcloud.html")
def serve_indexcloud():
    return send_from_directory("templates", "indexcloud.html")

@app.route("/indexfire.html")
def serve_indexfire():
    return send_from_directory("templates", "indexfire.html")


#_______Process Routes_____________

def process_cloud_image(upload_path):
    img = cv2.imread(upload_path)
    if img is None:
        print("Failed to read the image")
        return {'status': 'error', 'message': 'Failed to read the image'}
    
# Perform face detection  --  clouds
    faces = face_cascade.detectMultiScale(img, scaleFactor=1.01, minNeighbors=3)
    prof = profile_cascade.detectMultiScale(img, scaleFactor=1.01, minNeighbors=4)

    for x, y, w, h in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (10, 255, 194), 10)
    for x, y, w, h in prof:
        cv2.rectangle(img, (x, y), (x + w, y + h), (10, 255, 194), 10)
    
    # Count the number of faces detected
    num_faces = len(faces)
    num_profiles = len(prof)

    temp_filename = 'temp.png'
    temp_destination = os.path.join(UPLOADS_FOLDER, temp_filename)

    # Save the processed image
    cv2.imwrite(temp_destination, img)

    # Remove the uploaded image
    os.remove(upload_path)

    result_cloud = {
        'status': 'success',
        'message': 'Image processed successfully',
        'num_faces': num_faces,
        'num_profiles': num_profiles,
        'temp_filename': temp_filename
    }
    return result_cloud


def process_fire_image(upload_path):
    img = cv2.imread(upload_path)
    if img is None:
        print("Failed to read the image")
        return {'status': 'error', 'message': 'Failed to read the image'}
    
# Perform face detection  --- fire
    faces = face_cascade.detectMultiScale(img, scaleFactor=1.01, minNeighbors=3)
    
    for x, y, w, h in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (181, 90, 0), 8)
    
    
    # Count the number of faces detected
    num_faces = len(faces)
    

    temp_filename = 'temp.png'
    temp_destination = os.path.join(UPLOADS_FOLDER, temp_filename)

    # Save the processed image
    cv2.imwrite(temp_destination, img)

    # Remove the uploaded image
    os.remove(upload_path)

    result_fire = {
        'status': 'success',
        'message': 'Image processed successfully',
        'num_faces': num_faces,
        'temp_filename': temp_filename
    }
    return result_fire

def process_cemetery_image(upload_path):
    img = cv2.imread(upload_path)
    if img is None:
        print("Failed to read the image")
        return {'status': 'error', 'message': 'Failed to read the image'}
    
# Perform face detection  --- Cemetery
    faces = face_cascade.detectMultiScale(img, scaleFactor=1.01, minNeighbors=7)
    prof = profile_cascade.detectMultiScale(img, scaleFactor=1.01, minNeighbors=4)

    for x, y, w, h in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (181, 90, 0), 8)
    for x, y, w, h in prof:
        cv2.rectangle(img, (x, y), (x + w, y + h), (181, 90, 0), 8)
    
    # Count the number of faces detected
    num_faces = len(faces)
    num_profiles = len(prof)

    temp_filename = 'temp.png'
    temp_destination = os.path.join(UPLOADS_FOLDER, temp_filename)

    # Save the processed image
    cv2.imwrite(temp_destination, img)

    # Remove the uploaded image
    os.remove(upload_path)

    result_cemetery = {
        'status': 'success',
        'message': 'Image processed successfully',
        'num_faces': num_faces,
        'num_profiles': num_profiles,
        'temp_filename': temp_filename
    }
    return result_cemetery
  

#________ UPLOADS______________________
@app.route("/uploadcloud", methods=["POST"])
def uploadcloud():
    target = os.path.join(APP_ROOT, 'static/images/')

    # create the image directory if not found
    if not os.path.isdir(target):
        os.mkdir(target)

    # check if the file was uploaded
    if "image" not in request.files:
        return render_template("error.html", message="No file uploaded"), 400

    # retrieve the file from the HTML file picker
    upload = request.files.getlist("image")[0]
    print("File name: {}".format(upload.filename))
    filename = upload.filename

    # file support verification
    ext = os.path.splitext(filename)[1]
    if ext.lower() in [".jpg", ".png", ".bmp", ".jpeg"]:
        print("File accepted")
    else:
        return render_template("error.html", message="The selected file is not supported"), 400

    # save the file
    destination = os.path.join(target, filename)
    print("File saved to:", destination)
    upload.save(destination)

    processed_result = process_cloud_image(destination)
    if processed_result['status'] == 'error':
        return render_template("error.html", message="Failed to process the image"), 500

    return redirect(url_for('displaycloud', original_image=filename, processed_image=processed_result['temp_filename'],
                            num_faces=processed_result['num_faces'], num_profiles=processed_result['num_profiles']))

    


@app.route("/uploadfire", methods=["POST"])
def uploadfire():
    target = os.path.join(APP_ROOT, 'static/images/')

    # create the image directory if not found
    if not os.path.isdir(target):
        os.mkdir(target)

    # check if the file was uploaded
    if "image" not in request.files:
        return render_template("error.html", message="No file uploaded"), 400

    # retrieve the file from the HTML file picker
    upload = request.files.getlist("image")[0]
    print("File name: {}".format(upload.filename))
    filename = upload.filename

    # file support verification
    ext = os.path.splitext(filename)[1]
    if ext.lower() in [".jpg", ".png", ".bmp", ".jpeg"]:
        print("File accepted")
    else:
        return render_template("error.html", message="The selected file is not supported"), 400

    # save the file
    destination = os.path.join(target, filename)
    print("File saved to:", destination)
    upload.save(destination)

    # Continue with the image processing for fire image
    processed_result = process_fire_image(destination)
    if processed_result['status'] == 'error':
        return render_template("error.html", message="Failed to process the image"), 500

    return redirect(url_for('displayfire', original_image=filename, processed_image=processed_result['temp_filename'],
                            num_faces=processed_result['num_faces']))


#________ UPLOADS______________________
@app.route("/uploadcemetery", methods=["POST"])
def uploadcemetery():
    target = os.path.join(APP_ROOT, 'static/images/')

    # create the image directory if not found
    if not os.path.isdir(target):
        os.mkdir(target)

    # check if the file was uploaded
    if "image" not in request.files:
        return render_template("error.html", message="No file uploaded"), 400

    # retrieve the file from the HTML file picker
    upload = request.files.getlist("image")[0]
    print("File name: {}".format(upload.filename))
    filename = upload.filename

    # file support verification
    ext = os.path.splitext(filename)[1]
    if ext.lower() in [".jpg", ".png", ".bmp", ".jpeg"]:
        print("File accepted")
    else:
        return render_template("error.html", message="The selected file is not supported"), 400

    # save the file
    destination = os.path.join(target, filename)
    print("File saved to:", destination)
    upload.save(destination)

    processed_result = process_cemetery_image(destination)
    if processed_result['status'] == 'error':
        return render_template("error.html", message="Failed to process the image"), 500

    return redirect(url_for('displaycemetery', original_image=filename, processed_image=processed_result['temp_filename'],
                            num_faces=processed_result['num_faces'], num_profiles=processed_result['num_profiles']))

    
#______Processing...________

# default access page
@app.route("/")
def processing():
    return render_template('processing.html')


#________Display _______

@app.route("/displaycloud")
def displaycloud():
    original_image = request.args.get('original_image')
    processed_image = request.args.get('processed_image')
    num_faces = int(request.args.get('num_faces', 0))       
    num_profiles = int(request.args.get('num_profiles', 0))
    temp_filename = 'temp.png'

    return render_template("displaycloud.html", original_image=original_image, processed_image=processed_image, num_faces=num_faces, num_profiles=num_profiles, temp_filename=temp_filename)

@app.route("/displayfire")
def displayfire():
    original_image = request.args.get('original_image')
    processed_image = request.args.get('processed_image')
    num_faces = int(request.args.get('num_faces', 0))      
    temp_filename = 'temp.png'

    return render_template("displayfire.html", original_image=original_image, processed_image=processed_image, num_faces=num_faces,  temp_filename=temp_filename)

@app.route("/displaycemetery")
def displaycemetery():
    original_image = request.args.get('original_image')
    processed_image = request.args.get('processed_image')
    num_faces = int(request.args.get('num_faces', 0))
    num_profiles = int(request.args.get('num_profiles', 0))
    temp_filename = 'temp.png'

    return render_template("displaycemetery.html", original_image=original_image, processed_image=processed_image, num_faces=num_faces, num_profiles=num_profiles, temp_filename=temp_filename)

@app.route('/temp.png')
def send_image():
    target = os.path.join(APP_ROOT, 'static/images')
    return send_from_directory(target, 'temp.png')
    

@app.route("/download/<filename>")
def download_image(filename):
    target = os.path.join(APP_ROOT, 'static/images')
    return send_from_directory(target, filename, as_attachment=True)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == "__main__":
    app.run()
