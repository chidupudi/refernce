import os
import pickle
import pytesseract
from flask import Flask, render_template_string, request, redirect
from werkzeug.utils import secure_filename
from PIL import Image
from PyPDF2 import PdfReader
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'png', 'jpg', 'jpeg'}
app.secret_key = 'supersecretkey'  # For CSRF protection, can be any string

# Load the model and vectorizer
with open("certificate_classifier.pkl", "rb") as model_file:
    model = pickle.load(model_file)

with open("vectorizer.pkl", "rb") as vectorizer_file:
    vectorizer = pickle.load(vectorizer_file)


def allowed_file(filename):
    """Check if the file is an allowed type."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def extract_text(file_path):
    """Extract text from a file (PDF or image)."""
    if file_path.lower().endswith(".pdf"):
        text = ""
        try:
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text()
        except Exception as e:
            print(f"Error reading PDF file {file_path}: {e}")
        return text
    elif file_path.lower().endswith((".png", ".jpg", ".jpeg")):
        try:
            text = pytesseract.image_to_string(Image.open(file_path))
        except Exception as e:
            print(f"Error reading image file {file_path}: {e}")
            text = ""
        return text
    else:
        return ""

#this is my name
def extract_features(file_path):
    """Extract features from a file."""
    text = extract_text(file_path)
    return {
        "text_length": len(text),
        "word_count": len(text.split()),
        "text": text
    }


def predict_certificate(file_path):
    """Predict if the certificate is genuine or not using the trained model."""
    features = extract_features(file_path)

    # Vectorize the text
    text_vector = vectorizer.transform([features["text"]]).toarray()

    # Combine with other features
    feature_array = np.hstack((text_vector, np.array([[features["text_length"], features["word_count"]]])))

    # Make the prediction
    prediction = model.predict(feature_array)
    return prediction[0]


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    filename = None
    if request.method == "POST":
        if "file" not in request.files:
            return redirect(request.url)
        file = request.files["file"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Predict the certificate type
            result = predict_certificate(file_path)

    return render_template_string(HTML_TEMPLATE, result=result, filename=filename)


HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Certificate Verification</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }

        .container {
            width: 50%;
            margin: auto;
            padding: 30px;
            background-color: #fff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            margin-top: 50px;
            border-radius: 10px;
        }

        h1 {
            color: #333;
            text-align: center;
        }

        form {
            display: flex;
            flex-direction: column;
        }

        label {
            margin-bottom: 10px;
        }

        input[type="file"] {
            padding: 10px;
            margin-bottom: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }

        button {
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        button:hover {
            background-color: #45a049;
        }

        a {
            display: block;
            text-align: center;
            margin-top: 20px;
            color: #333;
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Upload Your Certificate</h1>
        {% if result is not none %}
            <p>Uploaded Certificate: {{ filename }}</p>
            <p>Prediction: <strong>{{ result }}</strong></p>
            <a href="/">Upload another certificate</a>
        {% else %}
            <form action="/" method="post" enctype="multipart/form-data">
                <label for="file">Choose a certificate file (PDF, PNG, JPG, JPEG):</label>
                <input type="file" name="file" id="file" required>
                <button type="submit">Upload and Check</button>
            </form>
        {% endif %}
    </div>
</body>
</html>
'''

if __name__ == "__main__":
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
