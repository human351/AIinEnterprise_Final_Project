import os
import time
import cv2
from flask import Flask, render_template, request, redirect, send_from_directory
from ultralytics import YOLO, solutions
from dotenv import load_dotenv
#test check
# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Retrieve directory paths from environment variables
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'output')
TARGET_WIDTH = int(os.getenv('TARGET_WIDTH', 640))
TARGET_HEIGHT = int(os.getenv('TARGET_HEIGHT', 480))

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Ensure the directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)

def resize_and_pad(image, target_width, target_height):
    """Resize and pad image to maintain aspect ratio and fit target dimensions."""
    (h, w) = image.shape[:2]
    aspect = w / h
    if aspect > 1:
        new_width = target_width
        new_height = int(target_width / aspect)
    else:
        new_height = target_height
        new_width = int(target_height * aspect)

    resized_image = cv2.resize(image, (new_width, new_height))
    padded_image = cv2.copyMakeBorder(
        resized_image,
        top=(target_height - new_height) // 2,
        bottom=(target_height - new_height + 1) // 2,
        left=(target_width - new_width) // 2,
        right=(target_width - new_width + 1) // 2,
        borderType=cv2.BORDER_CONSTANT,
        value=(0, 0, 0)  # Black padding
    )
    return padded_image

@app.route("/", methods=["GET", "POST"])
def upload_image():
    if request.method == "POST":
        if "file" not in request.files:
            return redirect(request.url)
        
        file = request.files["file"]
        if file.filename == "":
            return redirect(request.url)

        if file:
            # Save the original image
            filename = file.filename
            original_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(original_path)

            # Load and process the image
            im0 = cv2.imread(original_path)
            if im0 is None:
                return "Error loading image", 400

            im0 = resize_and_pad(im0, TARGET_WIDTH, TARGET_HEIGHT)

            # Initialize YOLO model and Object Counter within the request
            model = YOLO("yolov8n.pt")
            region_points = [(20, 400), (1080, 404), (1080, 360), (20, 360), (20, 400)]
            counter = solutions.ObjectCounter(
                view_img=True,
                reg_pts=region_points,
                names=model.names,
                draw_tracks=True,
                line_thickness=2,
            )

            # Process the image
            tracks = model.track(im0, persist=True, show=False, classes=[0])

            # Perform counting and draw the results on the image
            im0 = counter.start_counting(im0, tracks)

            # Generate a unique filename for the processed image
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            processed_filename = f"processed_image_{timestamp}.jpg"
            processed_path = os.path.join(app.config['OUTPUT_FOLDER'], processed_filename)

            # Save the processed image
            success = cv2.imwrite(processed_path, im0)
            if not success:
                return "Failed to save image", 500

            # Return both the original and processed image paths to the frontend
            return render_template("display_images.html", original_image=filename, processed_image=processed_filename)

    return render_template("upload.html")

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/output/<filename>')
def output_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == "__main__":

    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
