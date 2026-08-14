import pandas as pd
import numpy as np
import os

def generate_classification_data():
    categories = ['Data Science', 'HR', 'Advocate', 'Arts', 'Web Designing', 
                  'Mechanical Engineer', 'Sales', 'Health and fitness', 'Civil Engineer', 'Java Developer']
    
    category_keywords = {
        'Data Science': 'python machine learning data analysis sql numpy pandas scikit-learn deep learning statistics visualization r spark',
        'HR': 'human resources recruitment talent management payroll policy employee engagement hiring screening interviews onboarding sourcing',
        'Advocate': 'legal research court law litigation drafting cases defense prosecution contracts agreements judiciary advocacy law legal',
        'Arts': 'creative design painting sketching fine arts gallery exhibition portfolio museum interior design art history visual drawing',
        'Web Designing': 'html css javascript bootstrap frontend ui ux photoshop figma responsive design jquery sass web development design',
        'Mechanical Engineer': 'cad autocad thermodynamics manufacturing solidworks design mechanical systems maintenance engines structural analysis engineer',
        'Sales': 'business development sales targets marketing leads conversion customer relationship management revenue growth cold calling negotiation',
        'Health and fitness': 'nutrition trainer workout gym personal training wellness diet plan sports yoga physiology exercise health coaching fitness',
        'Civil Engineer': 'construction structural design site supervision revit surveying bridge roads project management cad site planning civil',
        'Java Developer': 'java spring boot hibernate j2ee microservices sql backend web services maven git rest api application development developer'
    }

    data = []
    for category in categories:
        keywords = category_keywords[category]
        # 100 samples per category
        for i in range(100):
            kw_list = keywords.split()
            np.random.shuffle(kw_list)
            num_words = np.random.randint(20, 45)
            sample_text = " ".join(np.random.choice(kw_list, size=num_words))
            
            # Simple features for regression
            skill_count = len(set(sample_text.split()))
            resume_length = len(sample_text)
            
            data.append({
                "Resume_Text": sample_text,
                "Category": category,
                "Skill_Count": skill_count,
                "Resume_Length": resume_length
            })
            
    df = pd.DataFrame(data)
    os.makedirs('dataset', exist_ok=True)
    df.to_csv('dataset/resume_data.csv', index=False)
    print("Classification dataset created at dataset/resume_data.csv")

if __name__ == "__main__":
    generate_classification_data()
