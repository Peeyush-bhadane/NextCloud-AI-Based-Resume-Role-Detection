import re
import pandas as pd
import numpy as np
from collections import Counter
from sklearn.metrics.pairwise import cosine_similarity

def calculate_benchmark_metrics(user_text, predicted_role, df_data, tfidf, role_skills, confidence_score):
    """
    Computes genuine data-driven metrics using pre-cleaned benchmarks.
    """
    user_vec = tfidf.transform([user_text])
    
    # 1. Filter Role Data (Dynamic)
    role_df = df_data[df_data["Category"] == predicted_role].copy()
    if role_df.empty:
        return 0, 0, 0, 0, [], [], 0, 0, 0, []
    
    # 2. Similarity Benchmarking (Uses Pre-cleaned data)
    # Check if 'Cleaned_Resume' exists (saved during training)
    column = "Cleaned_Resume" if "Cleaned_Resume" in role_df.columns else "Resume_Text"
    role_vecs = tfidf.transform(role_df[column])
    similarities = cosine_similarity(user_vec, role_vecs).flatten()
    
    benchmark_indices = np.where(similarities > 0.35)[0] 
    if len(benchmark_indices) < 5:
        benchmark_indices = similarities.argsort()[-5:]
        
    benchmark_df = role_df.iloc[benchmark_indices]
    benchmark_profiles_count = len(benchmark_indices)
    
    # 3. Skill Match (60%)
    from skill_analysis import extract_skills
    user_extracted_skills = set(extract_skills(user_text))
    benchmark_skill_set = set(role_skills.get(predicted_role, []))
    
    matching_skills = sorted(list(user_extracted_skills.intersection(benchmark_skill_set)))
    missing_skills = sorted(list(benchmark_skill_set - user_extracted_skills))
    skill_match_score = (len(matching_skills) / len(benchmark_skill_set)) * 100 if benchmark_skill_set else 100
    
    # 4. Content Quality Score (25%)
    avg_benchmark_len = benchmark_df["Resume_Text"].apply(lambda x: len(x.split())).mean()
    user_len = len(user_text.split())
    len_ratio = user_len / avg_benchmark_len if avg_benchmark_len > 0 else 1
    quality_score = max(0, 100 - abs(1 - len_ratio) * 100)
    
    # 5. Keyword Density (15%)
    # Use only benchmark group for keywords
    benchmark_text = " ".join(benchmark_df["Resume_Text"].str.lower())
    benchmark_words = set([w for w in re.findall(r'\w+', benchmark_text) if len(w) > 3])
    user_words = set([w for w in re.findall(r'\w+', user_text.lower()) if len(w) > 3])
    overlap = len(user_words.intersection(benchmark_words)) / len(benchmark_words) if benchmark_words else 0
    keyword_score = min(overlap * 400, 100) 
    
    # 6. Neural Insight: Deep Similarity Matching
    # Only count very high quality matches (> 0.6) for realism
    high_match_count = int(np.sum(similarities > 0.60))
    
    # 7. Real Industry Benchmarks (Top 3 actual resumes)
    top_indices = similarities.argsort()[-3:][::-1]
    top_benchmarks = []
    for idx in top_indices:
        snippet = role_df.iloc[idx][column]
        # Get first 150 chars for the snippet
        top_benchmarks.append({
            "score": float(similarities[idx] * 100),
            "snippet": snippet[:150].strip() + "..."
        })

    # 8. Final Job Readiness
    job_readiness = (0.60 * skill_match_score) + (0.25 * quality_score) + (0.15 * keyword_score)
    
    return min(job_readiness, 100), skill_match_score, quality_score, keyword_score, matching_skills, missing_skills, len(role_df), benchmark_profiles_count, high_match_count, top_benchmarks

def generate_suggestions(missing_skills, predicted_role):
    """Generates professional development path for futuristic UI cards."""
    tips = []
    if missing_skills:
        for skill in missing_skills[:4]:
            tips.append(f"Deploy your learning focus on **{skill.title()}** integration to reach peak industry readiness.")
    
    tips.append(f"Architect high-impact portfolio projects centered on **{predicted_role}** core frameworks.")
    tips.append(f"Synchronize resume keywords with high-density technical benchmarks discovered in our dataset.")
    return list(dict.fromkeys(tips))[:5]
