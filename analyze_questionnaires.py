import pandas as pd
import numpy as np
from typing import Dict, List, Any

def analyze_demographics(df: pd.DataFrame, demographic_cols: List[str]) -> Dict[str, Any]:
    """
    Analyzes demographic columns of a DataFrame.
    """
    demographic_stats: Dict[str, Any] = {}
    for col in demographic_cols:
        if col in df.columns:
            if pd.api.types.is_string_dtype(df[col]) or isinstance(df[col].dtype, pd.CategoricalDtype):
                counts = df[col].value_counts()
                percentages = df[col].value_counts(normalize=True) * 100
                demographic_stats[col] = {
                    'counts': counts.to_dict(),
                    'percentages': percentages.to_dict()
                }
            elif pd.api.types.is_numeric_dtype(df[col]):
                demographic_stats[col] = df[col].describe().to_dict()
    return demographic_stats

def analyze_variable_questions(df: pd.DataFrame, question_mapping: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
    """
    Analyzes variable questions, handling single and multiple-choice answers.
    """
    indicator_scores: Dict[str, List[float]] = {}
    df_copy = df.copy()

    for question, mapping in question_mapping.items():
        if question in df_copy.columns:
            indicator = mapping['indicator']
            scale = mapping['scale']
            score_col = f"{question}_score"

            def calculate_score(cell_value):
                if pd.isna(cell_value):
                    return np.nan
                
                # Handle comma-separated multiple answers
                if isinstance(cell_value, str) and ',' in cell_value:
                    selected_options = [opt.strip() for opt in cell_value.split(',')]
                    scores = [scale.get(option) for option in selected_options if option in scale]
                    return sum(scores) / len(scores) if scores else np.nan
                else:
                    # Handle single answer, stripping whitespace
                    return scale.get(cell_value.strip() if isinstance(cell_value, str) else cell_value)

            df_copy[score_col] = df_copy[question].apply(calculate_score)
            
            if indicator not in indicator_scores:
                indicator_scores[indicator] = []
            
            indicator_scores[indicator].extend(df_copy[score_col].dropna().tolist())

    mean_indicator_scores = {
        indicator: (sum(scores) / len(scores)) if scores else 0.0
        for indicator, scores in indicator_scores.items()
    }
    
    return mean_indicator_scores

def analyze_cross_analysis(df: pd.DataFrame, demographic_cols: List[str], question_mapping: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Performs cross-analysis between demographics and variable question indicators.
    """
    cross_analysis_results: Dict[str, Any] = {}
    df_copy = df.copy()

    # Ensure score columns exist for all questions
    for question, mapping in question_mapping.items():
        if question in df_copy.columns:
            score_col = f"{question}_score"
            if score_col not in df_copy.columns:
                scale = mapping['scale']
                def calculate_score(cell_value):
                    if pd.isna(cell_value):
                        return np.nan
                    if isinstance(cell_value, str) and ',' in cell_value:
                        selected_options = [opt.strip() for opt in cell_value.split(',')]
                        scores = [scale.get(option) for option in selected_options if option in scale]
                        return sum(scores) / len(scores) if scores else np.nan
                    else:
                        return scale.get(cell_value.strip() if isinstance(cell_value, str) else cell_value)
                df_copy[score_col] = df_copy[question].apply(calculate_score)

    indicators = sorted(list(set(m['indicator'] for m in question_mapping.values())))
    indicator_cols: Dict[str, List[str]] = {indicator: [] for indicator in indicators}

    for question, mapping in question_mapping.items():
        if f"{question}_score" in df_copy.columns:
            indicator_cols[mapping['indicator']].append(f"{question}_score")

    for indicator, score_cols in indicator_cols.items():
        if score_cols:
            df_copy[f"{indicator}_mean_score"] = df_copy[score_cols].mean(axis=1, skipna=True)

    for demo_col in demographic_cols:
        if demo_col in df_copy.columns:
            cross_analysis_results[demo_col] = {}
            for indicator in indicators:
                if f"{indicator}_mean_score" in df_copy.columns:
                    grouped_analysis = df_copy.groupby(demo_col)[f"{indicator}_mean_score"].mean().to_dict()
                    cross_analysis_results[demo_col][indicator] = grouped_analysis
                
    return cross_analysis_results

def analyze_survey(file_path: str, demographic_cols: List[str], question_mapping: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Main function to run the full questionnaire analysis pipeline.
    """
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except FileNotFoundError:
        return {"error": f"File not found at {file_path}"}
    except Exception as e:
        return {"error": f"An error occurred while reading the file: {e}"}

    df_analysis = df.copy()

    demographic_results = analyze_demographics(df_analysis, demographic_cols)
    indicator_results = analyze_variable_questions(df_analysis, question_mapping)
    cross_analysis_results = analyze_cross_analysis(df_analysis, demographic_cols, question_mapping)
    
    full_analysis = {
        "demographic_analysis": demographic_results,
        "indicator_analysis": indicator_results,
        "cross_analysis": cross_analysis_results
    }
    
    return full_analysis

if __name__ == '__main__':
    data = {
        'gender': ['Female', 'Male', 'Female', 'Male', 'Female', 'Male'],
        'age': [25, 34, 45, 22, 51, 30],
        'satisfaction_q1': ['Happy', 'Neutral', 'Happy', 'Sad', 'Happy', 'Neutral'],
        'feedback_q1': ['Good', 'Good Bad', 'Excellent', 'Bad', 'Good Excellent', 'Good']
    }
    sample_df = pd.DataFrame(data)
    sample_csv_path = 'sample_survey_data.csv'
    sample_df.to_csv(sample_csv_path, index=False, encoding='utf-8-sig')

    demographic_columns = ['gender', 'age']
    
    variable_question_mapping = {
        'satisfaction_q1': {
            'indicator': 'satisfaction',
            'scale': {'Sad': 1, 'Neutral': 3, 'Happy': 5}
        },
        'feedback_q1': {
            'indicator': 'feedback',
            'scale': {'Bad': 1, 'Good': 3, 'Excellent': 5}
        }
    }

    analysis_results = analyze_survey(
        file_path=sample_csv_path,
        demographic_cols=demographic_columns,
        question_mapping=variable_question_mapping
    )

    import json
    print(json.dumps(analysis_results, indent=4, ensure_ascii=False))

    import os
    os.remove(sample_csv_path)
