import os
import pytesseract
from PIL import Image
import pandas as pd
from PyPDF2 import PdfReader
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import pickle


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


def extract_features(file_path):
    """Extract features from a file."""
    text = extract_text(file_path)
    return {
        "text_length": len(text),
        "word_count": len(text.split()),
        "text": text
    }


def prepare_dataset(dataset_folder):
    """Prepare dataset from the given folder."""
    data = []
    labels = []

    for label in os.listdir(dataset_folder):
        label_folder = os.path.join(dataset_folder, label)
        if os.path.isdir(label_folder):
            for file_name in os.listdir(label_folder):
                file_path = os.path.join(label_folder, file_name)
                if os.path.isfile(file_path):
                    features = extract_features(file_path)
                    data.append(features)
                    labels.append(label)
    return data, labels

def main():
    dataset_folder = "dataset"  # Replace with your dataset folder path
    print("Extracting features from dataset...")
    data, labels = prepare_dataset(dataset_folder)

    # Convert data into a DataFrame
    df = pd.DataFrame(data)
    df["label"] = labels

    # Vectorize text features
    from sklearn.feature_extraction.text import TfidfVectorizer
    vectorizer = TfidfVectorizer(max_features=500)
    text_vectors = vectorizer.fit_transform(df["text"]).toarray()

    # Combine text vectors with other features
    feature_df = pd.DataFrame(text_vectors)
    feature_df["text_length"] = df["text_length"]
    feature_df["word_count"] = df["word_count"]
    feature_df["label"] = df["label"]

    # Split dataset
    X = feature_df.drop("label", axis=1)
    y = feature_df["label"]

    # Convert column names to strings
    X.columns = X.columns.astype(str)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train model
    print("Training model...")
    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    # Evaluate model
    print("Evaluating model...")
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))

    # Save model and vectorizer
    with open("certificate_classifier.pkl", "wb") as model_file:
        pickle.dump(model, model_file)
    with open("vectorizer.pkl", "wb") as vectorizer_file:
        pickle.dump(vectorizer, vectorizer_file)

    print("Model and vectorizer saved successfully!")


if __name__ == "__main__":
    main()
