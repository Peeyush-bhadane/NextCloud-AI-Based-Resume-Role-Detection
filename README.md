# AI-Based Resume Role Detection and Job Readiness Analyzer

This project is a comprehensive Machine Learning pipeline that classifies professional resumes into predefined job categories and provides a detailed "Job Readiness" analysis. It features a sleek, interactive web dashboard built with Streamlit for a rich user experience.

## 🚀 Features
- **AI-Powered Role Classification**: Automatically predicts a resume's job category (e.g., Data Science, Java Developer) using a trained Support Vector Machine (SVM) model.
- **Job Readiness Scoring**: Uses a custom weighted formula (Skill Match, Resume Quality, Keyword Density).
- **Interactive Dashboard**: A futuristic, dark-themed UI built with Streamlit allows for easy resume uploading and visualization of results.
- **Deep Skill Analysis**: Extracts skills from the resume and benchmarks them against industry standards, highlighting identified strengths and critical skill gaps.
- **Actionable Roadmap**: Generates personalized suggestions to help users enhance their profile and improve their job readiness score.

## 📁 Project Structure
- `app.py`: Streamlit frontend with futuristic UI.
- `train_model.py`: Model training, comparison, and evaluation script.
- `preprocess.py`: Text cleaning and PDF extraction utilities.
- `scoring.py`: Logic for readiness and quality scores.
- `skill_analysis.py`: Skill extraction and benchmarking logic.
- `models/`: Saved pkl files for classifier, vectorizer, etc.
- `dataset/`: Contains `resume_data.csv`.
- `utils/`: Utility scripts, including the data generator.

## ⚙️ How It Works
The project follows a standard machine learning pipeline:
1.  **Data Generation**: A synthetic dataset of resumes is created using keyword lists for various job roles.
2.  **Preprocessing**: The text is cleaned by removing punctuation, URLs, and stopwords.
3.  **Feature Engineering**: The cleaned text is converted into numerical features using TF-IDF (Term Frequency-Inverse Document Frequency).
4.  **Model Training**: Several classifiers (Logistic Regression, Naive Bayes, SVM) are trained and evaluated using k-Fold Cross-Validation. The best-performing model is saved.
5.  **Inference & Analysis**: The Streamlit app loads the saved model and vectorizer to classify new resumes and run the complete job readiness analysis.

## 🛠️ Setup and Execution
Follow these steps to get the project running locally.

### 1. Generate the Dataset
First, create the synthetic resume data that the model will be trained on.
   ```bash
   python utils/generate_data.py
   ```

### 2. Install Dependencies
Install all the required Python libraries from the `requirements.txt` file.
   ```bash
   pip install -r requirements.txt
   ```

### 3. Train the Machine Learning Models
This script will preprocess the data, train and evaluate the classifiers, and save the best model and vectorizer to the `models/` directory.
   ```bash
   python train_model.py
   ```

### 4. Run the Streamlit Application
Finally, launch the interactive web dashboard.
   ```bash
   streamlit run app.py
   ```
   
## 🧠 ML Concepts Used
- **Feature Engineering**: TF-IDF Vectorization.
- **Classification**: Support Vector Machine (SVM), Logistic Regression, Multinomial Naive Bayes.
- **Model Evaluation**: Accuracy, Precision, Recall, F1 Score, k-Fold Cross Validation.
- **Evaluation**: Accuracy, Precision, Recall, F1 Score, k-Fold Cross Validation.

## 🎨 UI/UX Highlights
- Dark Futuristic Theme with Neon Accents.
- Glassmorphism Effect for containers.
- Animated gradients and custom skill matrices for a polished look.

---

