from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, url_for
import os
import cv2
import uuid  # Import the uuid module
import shutil
import numpy as np



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
face1_cascade = cv2.CascadeClassifier('haar/haarcascade_frontalface1.xml') 
profile_cascade = cv2.CascadeClassifier('haar/haarcascade_profile.xml')


app.static_folder = 'static'
# Create an empty list to hold shared image filenames
shared_images = []

# Create an empty list to hold existing gallery image filenames
existing_gallery_images = []

image_metadata = {}


    
roi_filenames = []  # List to store ROI filenames

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

# Function to adjust brightness
def adjust_brightness(image, factor):
    # Iterate through each pixel of the image
    for y in range(image.shape[0]):
        for x in range(image.shape[1]):
            # Get the pixel color (BGR values)
            pixel = image[y, x]

            # Calculate luminosity (you can use a different formula if needed)
            luminosity = (0.299 * pixel[2] + 0.587 * pixel[1] + 0.114 * pixel[0])

            # Decide whether to make it darker or lighter based on luminosity
            if luminosity > 128:
                # Make the pixel lighter (increase brightness)
                image[y, x] = np.clip(pixel + factor, 0, 255)
            else:
                # Make the pixel darker (decrease brightness)
                image[y, x] = np.clip(pixel - factor, 0, 255)

    return image



def process_cloud_image(upload_path):
    # Load the image
    img = cv2.imread(upload_path)
    if img is None:
        print("Failed to read the image")
        return {'status': 'error', 'message': 'Failed to read the image'}

    # Perform face detection on the cloud image
    faces = face_cascade.detectMultiScale(img, scaleFactor=1.03, minSize = (60,60), minNeighbors=3)
    faces1 = face1_cascade.detectMultiScale(img, scaleFactor=1.03, minSize = (60,60), minNeighbors=3)

    # Create a copy of the original image
    result_img_rectangles = img.copy()
    
    white_image = np.full((result_img_rectangles.shape[0], 20, 3), 255, dtype=np.uint8)
    

        # Apply a color map (e.g., 'BONE') to the entire image as background
    result_img_color_mapped_faces = cv2.applyColorMap(result_img_rectangles, cv2.COLORMAP_BONE)

    final_combined_image = []
        # Iterate through detected faces in 'faces'
    for (x, y, w, h) in faces:
            # Define the region of interest (ROI) for the face
        roi_faces = img[y:y + h, x:x + w]

            # Adjust brightness and contrast of the ROI
        alpha = 0.6  # Adjust brightness (increase/decrease as needed)
        beta = 110   # Adjust contrast (increase/decrease as needed)
        adjusted_roi = cv2.convertScaleAbs(roi_faces, alpha=alpha, beta=beta)

            # Apply the desired colormap (e.g., 'OCEAN') to the ROI
        colormap_roi = cv2.applyColorMap(adjusted_roi, cv2.COLORMAP_OCEAN)

            # Adjust the saturation of the ROI (increase/decrease as needed)
        saturation_factor = 0.75  # Increase or decrease saturation as needed
        hsv_roi = cv2.cvtColor(colormap_roi, cv2.COLOR_BGR2HSV)
        hsv_roi[:, :, 1] = np.clip(hsv_roi[:, :, 1] * saturation_factor, 0, 255)
        adjusted_roi_with_colormap = cv2.cvtColor(hsv_roi, cv2.COLOR_HSV2RGB)

            # Paste the modified ROI onto the background image
        result_img_color_mapped_faces[y:y + h, x:x + w] = adjusted_roi_with_colormap

            # Draw rectangles on the original image for 'faces'
        cv2.rectangle(result_img_rectangles, (x, y), (x + w, y + h), (10, 255, 194), 6)

        # Iterate through detected faces in 'faces1'
    for (x, y, w, h) in faces1:
            # Define the region of interest (ROI) for the face from 'faces1'
        roi_faces1 = img[y:y + h, x:x + w]

            # Adjust brightness and contrast of the ROI for 'faces1'
        alpha = 0.55  # Adjust brightness (increase/decrease as needed)
        beta = 110   # Adjust contrast (increase/decrease as needed)
        adjusted_roi_faces1 = cv2.convertScaleAbs(roi_faces1, alpha=alpha, beta=beta)

            # Apply the desired colormap (e.g., 'OCEAN') to the ROI for 'faces1'
        colormap_roi_faces1 = cv2.applyColorMap(adjusted_roi_faces1, cv2.COLORMAP_OCEAN)

            # Adjust the saturation of the ROI for 'faces1'
        saturation_factor = 0.90  # Increase or decrease saturation as needed
        hsv_roi_faces1 = cv2.cvtColor(colormap_roi_faces1, cv2.COLOR_BGR2HSV)
        hsv_roi_faces1[:, :, 1] = np.clip(hsv_roi_faces1[:, :, 1] * saturation_factor, 0, 255)
        adjusted_roi_with_colormap_faces1 = cv2.cvtColor(hsv_roi_faces1, cv2.COLOR_HSV2RGB)

            # Paste the modified ROI onto the background image for 'faces1'
        result_img_color_mapped_faces[y:y + h, x:x + w] = adjusted_roi_with_colormap_faces1

            # Draw rectangles on the original image for 'faces1'
        cv2.rectangle(result_img_rectangles, (x, y), (x + w, y + h), (10, 255, 194), 6)

        # Combine the original image with rectangles and the color-mapped ROIs image side by side
        
        combined_img = np.hstack(( white_image, result_img_rectangles))
    
        final_combined_image = np.hstack((result_img_color_mapped_faces, combined_img))



    # Count the number of faces detected in 'faces' and 'faces1' regions
    num_faces = len(faces)
    num_faces1 = len(faces1)

    temp_filename = 'temp.png'
    temp_destination = os.path.join(UPLOADS_FOLDER, temp_filename)

    cv2.imwrite(temp_destination, final_combined_image)

    result_cloud = {
        'status': 'success',
        'message': 'Image processed successfully',
        'num_faces': num_faces,
        'num_faces1': num_faces1,
        'temp_filename': temp_filename
    }
    return result_cloud

##### PROCESS FIRE ------------------------------------------------------------------------------------
def process_fire_image(upload_path):
    img = cv2.imread(upload_path)
    if img is None:
        print("Failed to read the image")
        return {'status': 'error', 'message': 'Failed to read the image'}
    
    # Perform face detection
    faces = face_cascade.detectMultiScale(img, scaleFactor=1.03, minNeighbors=3)

    # Create a copy of the original image to process separately
    processed_img1 = img.copy()
    result_img_color_mapped_faces = img.copy()
    
    white_image = np.full((processed_img1.shape[0], 20, 3), 255, dtype=np.uint8)

    # Iterate through detected faces and draw rectangles on the first processed image
    for (x, y, w, h) in faces:
        cv2.rectangle(processed_img1, (x, y), (x + w, y + h), (181, 90, 0), 10)

    #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Iterate through detected faces and apply colormap to the second processed image
    for (x, y, w, h) in faces:
        # Define the region of interest (ROI) for the face
        roi_faces = img[y:y + h, x:x + w]

       

            # Apply the desired colormap (e.g., 'BONE') to the ROI
        adjusted_roi_with_colormap= cv2.applyColorMap(roi_faces, cv2.COLORMAP_BONE) 

            # Paste the modified ROI onto the background image
        result_img_color_mapped_faces[y:y + h, x:x + w] = adjusted_roi_with_colormap
    
    # Combine the two processed images side by side
    
    combined_img = np.hstack(( white_image, processed_img1))
    
    final_combined_image = np.hstack(( result_img_color_mapped_faces, combined_img,))
    # Count the number of faces detected
    num_faces = len(faces)

    temp_filename = 'temp.png'
    temp_destination = os.path.join(UPLOADS_FOLDER, temp_filename)

    # Save the combined image with rectangles and colormap
    cv2.imwrite(temp_destination, final_combined_image)

    # Remove the uploaded image
    os.remove(upload_path)

    result_fire = {
        'status': 'success',
        'message': 'Image processed successfully',
        'num_faces': num_faces,
        'temp_filename': temp_filename
    }

    return result_fire    




### ? Saving ROIs

@app.route("/process_roi", methods=["POST"])
def process_roi():
    target = os.path.join(APP_ROOT, 'static/images/')

    # create the image directory if not found
    if not os.path.isdir(target):
        os.mkdir(target)

    # Check if the file was uploaded
    if "image" not in request.files:
        return render_template("error.html", message="No file uploaded"), 400

    # Retrieve the file from the HTML file picker
    upload = request.files.getlist("image")[0]
    print("File name: {}".format(upload.filename))
    filename = upload.filename

    # File support verification
    ext = os.path.splitext(filename)[1]
    if ext.lower() in [".jpg", ".png", ".bmp", ".jpeg"]:
        print("File accepted")
    else:
        return render_template("error.html", message="The selected file is not supported"), 400

    # Save the file
    destination = os.path.join(target, filename)
    print("File saved to:", destination)
    upload.save(destination)

    # Continue with the image processing for fire image
    processed_result = process_fire_image(destination)

    if processed_result['status'] == 'error':
        return render_template("error.html", message="Failed to process the image"), 500

    # Modify the ROI filenames to include the correct path to the separate ROI folder
    roi_folder = 'static/roi_images'  # Adjust this folder path to match the actual path
    roi_filenames_absolute = [os.path.join(roi_folder, os.path.basename(filename)) for filename in processed_result.get('roi_filenames', [])]

    # Append the ROI filenames to the shared list
    roi_filenames.extend(roi_filenames_absolute)

    # Redirect to the display_fire route, passing the ROI filenames as a list
    return redirect(url_for('display_fire', original_image=filename, processed_image=processed_result['temp_filename'],
                    num_faces=processed_result['num_faces'], roi_filenames=roi_filenames_absolute))


#### PROCESS CEM *
def process_cemetery_image(upload_path):   ### BONE GOOD FOR FIRE####
    img = cv2.imread(upload_path)
    if img is None:
        print("Failed to read the image")
        return {'status': 'error', 'message': 'Failed to read the image'}
    
    # Perform face detection
    faces = face_cascade.detectMultiScale(img, scaleFactor=1.03, minSize = (60,60), minNeighbors=6)
    prof =  face_cascade.detectMultiScale(img, scaleFactor=1.03, minSize = (60,60), minNeighbors=6)

    # Create a copy of the original image to process separately
    processed_img1 = img.copy()
    processed_img2 = img.copy()
    
    white_image = np.full((processed_img1.shape[0], 20, 3), 255, dtype=np.uint8)

    # Iterate through detected faces and draw rectangles on the first processed image
    for (x, y, w, h) in faces:
        cv2.rectangle(processed_img1, (x, y), (x + w, y + h), (181, 90, 0), 10)
    for (x, y, w, h) in prof:
        cv2.rectangle(processed_img1, (x, y), (x + w, y + h), (181, 90, 0), 10)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Iterate through detected faces and apply colormap to the second processed image
    
    
    for (x, y, w, h) in faces:
        # Define the region of interest (ROI) for the face
        roi_gray = gray[y:y + h, x:x + w]

        # Apply color mapping to the grayscale ROI
        color_mapped_roi = cv2.applyColorMap(roi_gray, cv2.COLORMAP_OCEAN)

        # Replace the grayscale ROI with the color-mapped ROI in the second processed image
        processed_img2[y:y + h, x:x + w] = color_mapped_roi
    
    for (x, y, w, h) in prof:
        # Define the region of interest (ROI) for the face
        roi_gray = gray[y:y + h, x:x + w]

        # Apply color mapping to the grayscale ROI
        color_mapped_roi = cv2.applyColorMap(roi_gray, cv2.COLORMAP_OCEAN)

        # Replace the grayscale ROI with the color-mapped ROI in the second processed image
        processed_img2[y:y + h, x:x + w] = color_mapped_roi
    
    # Combine the two processed images side by side
    combined_img = np.hstack(( white_image, processed_img1))
    
    final_combined_image = np.hstack(( processed_img2, combined_img))

    # Count the number of faces detected
    num_faces = len(faces)
    num_profiles = len(prof)

    temp_filename = 'temp.png'
    temp_destination = os.path.join(UPLOADS_FOLDER, temp_filename)

    # Save the combined image with rectangles and colormap
    cv2.imwrite(temp_destination, final_combined_image)

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

    destination = os.path.join(target, filename)
    print("File saved to:", destination)
    upload.save(destination)

    processed_result = process_cloud_image(destination)
    print("Processed temp filename:", processed_result['temp_filename'])  # Add this line to check the value

    if processed_result['status'] == 'error':
        return render_template("error.html", message="Failed to process the image"), 500
    
    # Store the processed image filename as a relative path within the static directory
    #processed_image_path = 'images/' + processed_result['temp_filename']
    
    # Get the number of faces detected from the processed_result dictionary
    num_faces = processed_result['num_faces']
    num_faces1 = processed_result['num_faces1']
    
    

    # Append the processed image data to the shared_images list
    shared_images.append({
        'temp_filename': processed_result['temp_filename'],
        'num_faces': num_faces,
        'num_faces1': num_faces1
        
    })
    
    # Store the metadata in the image_metadata dictionary using the filename as the key
    image_metadata[processed_result['temp_filename']] = {
        'num_faces': num_faces,
        'num_faces1': num_faces1
    }
    
    #return redirect(url_for('displaycloud', original_image=filename, processed_image=processed_image_path,
                            #num_faces=num_faces,  num_profiles=num_profiles))

    return redirect(url_for('displaycloud', original_image=filename, processed_image=processed_result['temp_filename'], num_faces=processed_result['num_faces'], num_faces1=processed_result['num_faces1']))


@app.route("/uploadfire", methods=["POST"])
def uploadfire():
    target = os.path.join(APP_ROOT, 'static/images/')

    # create the image directory if not found
    if not os.path.isdir(target):
        os.mkdir(target)

    # Check if the file was uploaded
    if "image" not in request.files:
        return render_template("error.html", message="No file uploaded"), 400

    # Retrieve the file from the HTML file picker
    upload = request.files.getlist("image")[0]
    print("File name: {}".format(upload.filename))

    # File support verification
    ext = os.path.splitext(upload.filename)[1]
    if ext.lower() in [".jpg", ".png", ".bmp", ".jpeg"]:
        print("File accepted")
    else:
        return render_template("error.html", message="The selected file is not supported"), 400

    filename = upload.filename

    # Save the file
    destination = os.path.join(target, filename)
    print("File saved to:", destination)
    upload.save(destination)

    # Continue with the image processing for the fire image
    processed_result = process_fire_image(destination)

    if processed_result['status'] == 'error':
        return render_template("error.html", message="Failed to process the image"), 500

    # Extract the list of ROI filenames and convert paths to forward slashes
    roi_filenames = processed_result.get('roi_filenames', [])
    roi_filenames_absolute = [roi_filename.replace("\\", "/") for roi_filename in roi_filenames]

    # Redirect to the display_fire route, passing the ROI filenames as a list
    return redirect(url_for('display_fire', original_image=filename, processed_image=processed_result['temp_filename'],
                        num_faces=processed_result['num_faces'], roi_filenames=roi_filenames))





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
    num_faces1 = int(request.args.get('num_faces1', 0))  
    temp_filename = processed_image          
    
        
    return render_template("displaycloud.html", original_image=original_image, processed_image=processed_image, num_faces=num_faces,   num_faces1=num_faces1,  temp_filename=temp_filename)
    

@app.route('/display_fire', methods=['GET'])
def display_fire():
    original_image = request.args.get('original_image')
    processed_image = request.args.get('processed_image')
    num_faces = int(request.args.get('num_faces'))
    temp_filename = request.args.get('temp_filename')
    
   # Retrieve ROI filenames from the URL parameter
    roi_filenames = request.args.getlist('roi_filenames')

    print("Received ROI Filenames:", roi_filenames)

    return render_template("displayfire.html", original_image=original_image, processed_image=processed_image,
                           num_faces=num_faces, temp_filename=temp_filename, roi_filenames=roi_filenames)

    


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


@app.route('/about')
def about():
    return render_template('about.html')

@app.route("/download/<filename>")
def download_image(filename):
    target = os.path.join(APP_ROOT, 'static/images')
    return send_from_directory(target, filename, as_attachment=True)



@app.route("/gallery")
def gallery():
    target_gallery = os.path.join(APP_ROOT, 'static/gallery')
    existing_gallery_images = [filename for filename in os.listdir(target_gallery) if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.JPG'))]

    # Group images into sections using dictionaries
    sections = {
        "Cloud Gallery": [filename for filename in existing_gallery_images if "section1" in filename],
        "Campfire Gallery": [filename for filename in existing_gallery_images if "section2" in filename],
        "Nature Gallery": [filename for filename in existing_gallery_images if "section3" in filename],
    }

    # Reverse the shared_images list to display the most recent image at the top
    reversed_shared_images = shared_images[::-1]

    image_saved = False
    if request.method == "POST":
        filename = request.form.get("filename")
        if filename:
            image_saved = True

    return render_template(
        'gallery.html',
        shared_images=reversed_shared_images,
        sections=sections,
        image_saved=image_saved
    )




@app.route("/save_to_gallery", methods=["POST"])
def save_to_gallery():
    print("save_to_gallery route accessed")
    target_gallery = os.path.join(APP_ROOT, 'static/gallery')
    new_filename = str(uuid.uuid4())  # Generate a unique filename without extension

    # Determine the file extension based on the image format
    processed_image_extension = 'png'  # Default extension
    if os.path.exists(os.path.join(APP_ROOT, 'static/images/temp.jpg')):
        processed_image_extension = 'jpg'

    # Move the processed image from the static/images folder to the static/gallery folder with the correct extension
    processed_image_path = os.path.join(APP_ROOT, 'static/images/temp.' + processed_image_extension)
    new_processed_image_path = os.path.join(APP_ROOT, 'static', 'gallery', new_filename + '.' + processed_image_extension)
    shutil.move(processed_image_path, new_processed_image_path)

    num_faces = int(request.form.get('num_faces', 0))
    num_profiles = int(request.form.get('num_profiles', 0))
    num_faces1 = int(request.form.get('num_faces1', 0))
   

    shared_images.append({
        'temp_filename': new_filename + '.' + processed_image_extension,
        'num_faces': num_faces,
        'num_profiles': num_profiles,
        'num_faces1': num_faces1
    })
    # Store the metadata in the image_metadata dictionary using the UUID-based filename as the key
    image_metadata[new_filename] = {
        'num_faces': num_faces,
        'num_profiles': num_profiles,
        'num_faces1': num_faces1
    }

    return redirect(url_for("gallery"))



@app.route("/clear_shared_images", methods=["GET"])
def clear_shared_images():
    global shared_images
    shared_images = []  # Clear the shared_images list
    return redirect(url_for("gallery"))



@app.route('/challenge')
def challenge():
    return render_template('challenge.html')

if __name__ == "__main__":
    app.run()
