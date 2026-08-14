import pandas as pd
import numpy as np
import pickle
import os
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from preprocess import clean_resume_text
from skill_analysis import get_top_skills_per_role

def train_backend():
    print("Starting Model Training Pipeline...")
    dataset_path = 'dataset/resume_data.csv'
    if not os.path.exists(dataset_path):
        print("Dataset not found at 'dataset/resume_data.csv'")
        return

    df = pd.read_csv(dataset_path)
    print(f"Dataset Loaded: {len(df)} resumes found.")
    
    # Preprocessing
    df['Cleaned_Resume'] = df['Resume_Text'].apply(clean_resume_text)

    # Feature Extraction (TF-IDF)
    print("Extracting TF-IDF Features...")
    tfidf = TfidfVectorizer(max_features=3000, stop_words='english')
    X = tfidf.fit_transform(df['Cleaned_Resume']).toarray()
    print("x is",X)
    print(X.shape)
    le = LabelEncoder()
    y = le.fit_transform(df['Category'])

    # Split for validation
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 1. Supervised Learning: Model Comparison
    models = {
        "Logistic Regression": LogisticRegression(max_iter=1000),
        "Naive Bayes": MultinomialNB(),
        "Support Vector Machine": SVC(probability=True, kernel='linear')
    }

    best_model = None
    best_accuracy = 0
    best_model_name = ""

    print("\n--- Model Evaluation (k-Fold Cross Validation) ---")
    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    for name, model in models.items():
        # k-Fold CV
        cv_scores = cross_val_score(model, X_train, y_train, cv=kf)
        mean_cv_acc = cv_scores.mean()
        
        # Fit on train set
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        print(f"Model: {name:20} | CV Mean: {mean_cv_acc:.4f} | Test Acc: {acc:.4f} | F1: {f1:.4f}")

        if acc > best_accuracy:
            best_accuracy = acc
            best_model = model
            best_model_name = name

    print(f"\nOptimization Complete: '{best_model_name}' selected for deployment.")

    # Save ROLE mapping and skill patterns
    role_ideal_skills = get_top_skills_per_role(df)

    # Save Pre-Cleaned Dataset for faster Benchmarking
    df.to_csv('dataset/resume_data_cleaned.csv', index=False)

    # 3. Persistence
    os.makedirs('models', exist_ok=True)
    with open('models/classifier.pkl', 'wb') as f:
        pickle.dump(best_model, f)
    with open('models/tfidf.pkl', 'wb') as f:
        pickle.dump(tfidf, f)
    with open('models/label_encoder.pkl', 'wb') as f:
        pickle.dump(le, f)
    with open('models/role_skills.pkl', 'wb') as f:
        pickle.dump(role_ideal_skills, f)

    print("\nAll models and pre-cleaned benchmark patterns saved successfully.")

if __name__ == "__main__":
    train_backend()

if __name__ == "__main__":
    train_backend()
