import re

# Comprehensive list of skills for extraction
SKILL_LIST = [
    # Data Science & ML
    'python', 'r', 'sql', 'machine learning', 'deep learning', 'statistics', 'pandas', 'scikit-learn', 
    'tableau', 'power bi', 'keras', 'pytorch', 'tensorflow', 'nlp', 'data mining', 'matplotlib', 'seaborn',
    # Development
    'java', 'spring boot', 'hibernate', 'microservices', 'maven', 'junit', 'docker', 'golang', 'c++',
    'html', 'css', 'javascript', 'figma', 'photoshop', 'ui', 'ux', 'bootstrap', 'react', 'node.js', 'angular',
    # HR & Management
    'recruitment', 'payroll', 'onboarding', 'talent acquisition', 'employee engagement', 'training', 'sourcing',
    'performance management', 'labor law', 'grievance handling', 'hrms', 'compensation',
    # Cloud & DevOps
    'aws', 'kubernetes', 'jenkins', 'linux', 'terraform', 'ansible', 'monitoring', 'azure', 'gcp', 'ci/cd',
    # Business & Project Management
    'jira', 'agile', 'scrum', 'business requirements', 'stakeholder management', 'ms project', 'pmp', 'kanban',
    # Marketing
    'seo', 'content strategy', 'social media', 'google analytics', 'email marketing', 'copywriting', 'ads', 'crm',
    # Testing
    'selenium', 'manual testing', 'automation', 'test cases', 'bug tracking', 'regression testing', 'postman',
    # Finance & Others
    'sap', 'oracle', 'financial analysis', 'auditing', 'banking', 'tally', 'excel', 'public relations'
]

# Pre-compile a single regex for performance
SKILL_REGEX = r'\b(' + '|'.join(re.escape(skill) for skill in SKILL_LIST) + r')\b'

def extract_skills(text):
    """Extracts predefined skills from text using regex."""
    if not text:
        return []
    # Find all matches in one pass
    return list(set(re.findall(SKILL_REGEX, text.lower())))

def get_top_skills_per_role(df):
    """Identifies the most common skills for each job role in the dataset."""
    skills_per_role = {}
    roles = df['Category'].unique()
    for role in roles:
        role_texts = df[df['Category'] == role]['Resume_Text']
        all_found = []
        for text in role_texts:
            all_found.extend(extract_skills(text))
        
        # Count frequencies
        skill_counts = pd.Series(all_found).value_counts().head(8) # Top 8 skills
        skills_per_role[role] = list(skill_counts.index)
    return skills_per_role

import pandas as pd # Needed for get_top_skills_per_role
