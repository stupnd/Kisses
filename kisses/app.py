import os
import cv2
import numpy as np
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from sklearn.cluster import KMeans

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'your_secret_key_here'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Define skin tone categories
SKIN_TONE_LABELS = {
    "fair": (200, 170, 150),
    "medium": (150, 110, 90),
    "dark": (90, 60, 40),
}

def detect_skin_tone(image_path):
    """Extracts the dominant skin tone from an image."""
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Convert image to a smaller size for faster processing
    image = cv2.resize(image, (200, 200))
    
    # Flatten image to 2D array
    pixels = image.reshape(-1, 3)
    
    # Use KMeans clustering to find dominant colors
    kmeans = KMeans(n_clusters=3, random_state=0, n_init=10)
    kmeans.fit(pixels)
    
    # Find the most dominant color
    dominant_color = np.mean(kmeans.cluster_centers_, axis=0)

    # Find closest match in predefined skin tones
    closest_tone = min(SKIN_TONE_LABELS, key=lambda tone: np.linalg.norm(np.array(SKIN_TONE_LABELS[tone]) - dominant_color))
    
    return closest_tone

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename != '':
                filename = secure_filename(photo.filename)
                photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                photo.save(photo_path)

                # Detect skin tone
                detected_skin_tone = detect_skin_tone(photo_path)

                return f"Photo uploaded successfully! Detected Skin Tone: {detected_skin_tone.capitalize()}"

    return '''
        <h2>Upload your photo & fill out the questionnaire</h2>
        <form method="post" enctype="multipart/form-data">
            <label for="photo">Upload a photo:</label>
            <input type="file" name="photo" required>
            <br><br>
            <label for="makeup_type">What kind of makeup do you like?</label>
            <select name="makeup_type">
                <option value="dewy">Dewy</option>
                <option value="matte">Matte</option>
                <option value="minimal">Minimal</option>
            </select>
            <br><br>
            <button type="submit">Submit</button>
        </form>
    '''

if __name__ == '__main__':
    app.run(debug=True)
