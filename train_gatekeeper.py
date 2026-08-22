import os
import cv2
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import joblib

def extract_text_structural_features(img_gray):
    """
    Extracts layout-independent features based on text stroke contours,
    ignoring absolute pixel positions, logos, or background lines.
    """
    # Apply Otsu thresholding to separate text from background
    _, thresh = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Find contours of text/blobs
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return [0, 0, 0, 0, 0] # Empty fallback
        
    areas = []
    aspect_ratios = []
    solidity_vals = []
    
    for c in contours:
        area = cv2.contourArea(c)
        if area < 5: # Filter out tiny pixel noise
            continue
        areas.append(area)
        
        # Bounding box aspect ratio
        x, y, w, h = cv2.boundingRect(c)
        if h > 0:
            aspect_ratios.append(w / float(h))
            
        # Solidity (contour area / hull area)
        hull = cv2.convexHull(c)
        hull_area = cv2.contourArea(hull)
        if hull_area > 0:
            solidity_vals.append(area / float(hull_area))
            
    if not areas:
        return [0, 0, 0, 0, 0]
        
    # Aggregate structural metrics (position-independent)
    features = [
        len(areas),                         # Total distinct text components
        np.mean(areas),                     # Average size of text elements
        np.std(areas) if len(areas) > 1 else 0, # Variation in text sizes
        np.mean(aspect_ratios) if aspect_ratios else 0, # Average character/word aspect ratio
        np.mean(solidity_vals) if solidity_vals else 0   # Text compactness
    ]
    return features

def load_dataset_from_folders():
    data = []
    labels = []
    
    classes = {"typed": "TYPED", "handwritten": "HANDWRITTEN"}
    
    for folder_name, label_name in classes.items():
        folder_path = os.path.join("dataset", folder_name)
        if not os.path.exists(folder_path):
            print(f"Warning: Directory {folder_path} not found.")
            continue
            
        print(f"Loading images from {folder_path}...")
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(folder_path, filename)
                # Read image as grayscale
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    # Extract structural text features instead of flattening pixels
                    features = extract_text_structural_features(img)
                    data.append(features)
                    labels.append(label_name)
                
    return np.array(data), np.array(labels)

def train_model():
    X, y = load_dataset_from_folders()
    
    if len(X) == 0:
        print("Error: No training data found! Run 'build_dataset.py' first.")
        return

    print(f"Loaded {len(X)} total images successfully.")
    
    # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train Random Forest Classifier
    print("Training Random Forest structural gatekeeper model...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    # Evaluate performance
    preds = clf.predict(X_test)
    print("\nModel Evaluation Report:")
    print(classification_report(y_test, preds))
    
    # Export model artifact
    model_filename = "receipt_gatekeeper_model.pkl"
    joblib.dump(clf, model_filename)
    print(f"Gatekeeper model saved successfully as '{model_filename}'!")

if __name__ == "__main__":
    train_model()