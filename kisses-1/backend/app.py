from flask import Flask, request, jsonify, render_template
import os
import cv2
import numpy as np
import requests  # For making API calls

app = Flask(__name__)

# Function to fetch makeup products from the Makeup API
def fetch_makeup_products(product_type, brand=None, price_range=None):
    url = "http://makeup-api.herokuapp.com/api/v1/products.json"
    params = {
        "product_type": product_type,
        "brand": brand,
        "price_less_than": price_range,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    return []

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

    # Detect skin tone
    skin_tone = detect_skin_tone(photo_path)
    return jsonify({'skin_tone': skin_tone})

# Route to handle questionnaire and recommendations
@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    skin_tone = data.get('skin_tone')
    makeup_style = data.get('makeup_style')
    skin_type = data.get('skin_type')
    budget = data.get('budget')

    # Fetch foundation recommendations
    foundations = fetch_makeup_products("foundation", price_range=budget)
    # Filter foundations based on skin tone and skin type
    filtered_foundations = [
        product for product in foundations
        if skin_tone.lower() in product.get("name", "").lower() and
           skin_type.lower() in product.get("description", "").lower()
    ]

    # Fetch lipstick recommendations
    lipsticks = fetch_makeup_products("lipstick", price_range=budget)
    # Filter lipsticks based on makeup style
    filtered_lipsticks = [
        product for product in lipsticks
        if makeup_style.lower() in product.get("name", "").lower()
    ]

    # Fetch eyeshadow recommendations
    eyeshadows = fetch_makeup_products("eyeshadow", price_range=budget)
    # Filter eyeshadows based on makeup style
    filtered_eyeshadows = [
        product for product in eyeshadows
        if makeup_style.lower() in product.get("name", "").lower()
    ]

    recommendations = {
        "foundation": filtered_foundations[:3],  # Return top 3 results
        "lipstick": filtered_lipsticks[:3],
        "eyeshadow": filtered_eyeshadows[:3],
    }
    return jsonify(recommendations)

# Skin tone detection functions (keep your existing implementation)
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
    print(f"Average BGR Color: {average_color}")  # Debug print

    # Convert the average color from BGR to a human-readable skin tone
    skin_tone = classify_skin_tone(average_color)
    return skin_tone

def classify_skin_tone(bgr_color):
    # Convert BGR to RGB
    rgb_color = (bgr_color[2], bgr_color[1], bgr_color[0])
    print(f"Average RGB Color: {rgb_color}")  # Debug print

    # Define updated skin tone ranges
    skin_tones = {
        "Fair": ((200, 180, 150), (255, 220, 200)),
        "Light": ((150, 100, 70), (200, 180, 150)),  # Expanded range
        "Medium": ((120, 80, 50), (150, 100, 70)),  # Expanded range
        "Tan": ((80, 50, 30), (120, 80, 50)),
        "Dark": ((0, 0, 0), (80, 50, 30)),
    }

    # Classify the skin tone based on the average color
    for tone, (lower, upper) in skin_tones.items():
        if lower[0] <= rgb_color[0] <= upper[0] and \
           lower[1] <= rgb_color[1] <= upper[1] and \
           lower[2] <= rgb_color[2] <= upper[2]:
            return tone

    return "Unknown"
    # (Keep your existing implementation)
    ...

if __name__ == '__main__':
    app.run(debug=True)