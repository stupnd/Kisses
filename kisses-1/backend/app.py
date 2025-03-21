from flask import Flask, request, jsonify, render_template
import os
import cv2
import numpy as np

app = Flask(__name__)

# Route for the homepage
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle photo upload
@app.route('/upload', methods=['POST'])
def upload_photo():
    if 'photo' not in request.files:
        return jsonify({'error': 'No photo uploaded'}), 400

    photo = request.files['photo']
    if photo.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save the photo temporarily
    uploads_dir = os.path.join(os.path.dirname(__file__), 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    photo_path = os.path.join(uploads_dir, photo.filename)
    photo.save(photo_path)

    # TODO: Add skin tone detection logic here
    skin_tone = detect_skin_tone(photo_path)

    return jsonify({'skin_tone': skin_tone})

def detect_skin_tone(image_path):
    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        return "Error: Could not read image"

    # Convert the image to grayscale for face detection
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Load the pre-trained Haar Cascade model for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) == 0:
        return "Error: No face detected"

    # Assume the first detected face is the user's face
    (x, y, w, h) = faces[0]

    # Extract the face region
    face_region = image[y:y+h, x:x+w]

    # Convert the face region to HSV color space for better skin tone analysis
    hsv_face = cv2.cvtColor(face_region, cv2.COLOR_BGR2HSV)

    # Define a mask for skin color range in HSV
    lower_skin = np.array([0, 48, 80], dtype=np.uint8)
    upper_skin = np.array([20, 255, 255], dtype=np.uint8)
    skin_mask = cv2.inRange(hsv_face, lower_skin, upper_skin)

    # Apply the mask to the face region
    skin_region = cv2.bitwise_and(face_region, face_region, mask=skin_mask)

    # Calculate the average color of the skin region
    average_color = cv2.mean(skin_region, mask=skin_mask)[:3]

    # Convert the average color from BGR to a human-readable skin tone
    skin_tone = classify_skin_tone(average_color)
    return skin_tone

def classify_skin_tone(bgr_color):
    # Convert BGR to RGB
    rgb_color = (bgr_color[2], bgr_color[1], bgr_color[0])

    # Define skin tone ranges (you can adjust these based on your needs)
    skin_tones = {
        "Fair": ((200, 180, 150), (255, 220, 200)),
        "Light": ((180, 140, 120), (200, 180, 150)),
        "Medium": ((150, 110, 90), (180, 140, 120)),
        "Tan": ((120, 80, 60), (150, 110, 90)),
        "Dark": ((60, 40, 30), (120, 80, 60)),
    }

    # Classify the skin tone based on the average color
    for tone, (lower, upper) in skin_tones.items():
        if lower[0] <= rgb_color[0] <= upper[0] and \
           lower[1] <= rgb_color[1] <= upper[1] and \
           lower[2] <= rgb_color[2] <= upper[2]:
            return tone

    return "Unknown"

if __name__ == '__main__':
    app.run(debug=True)