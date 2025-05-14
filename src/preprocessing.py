# src/preprocessing.py
import pandas as pd
import numpy as np
import sys
import config

def clean_value(value):
    """Attempt to convert value to numeric, handling common non-numeric entries."""
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        value = value.strip().lower()
        if value in ['n/a', 'na', 'unknown', '', 'none', 'not applicable']:
            return np.nan
        if value == 'prefer not to say': # Or specific survey refusal codes
             return np.nan # Or a specific code like -99 if preferred
        try:
            # Handle ranges like '5-10' by taking the average or first number
            if '-' in value and value.replace('-', '').isdigit():
                parts = value.split('-')
                return (float(parts[0]) + float(parts[1])) / 2
            # Handle '>' like '>100'
            if '>' in value and value.replace('>', '').isdigit():
                return float(value.replace('>', '')) + 1 # Or just the number
            # Handle '<' like '<5'
            if '<' in value and value.replace('<', '').isdigit():
                 return float(value.replace('<', '')) -1 # Or just the number
            return float(value)
        except ValueError:
            # If it's not convertible after cleaning, return NaN
            return np.nan
    return value # Return original if not str/int/float


def preprocess_data(raw_path, processed_path):
    """Loads raw CSV, performs cleaning and type conversions, saves as Parquet."""
    print(f"Starting preprocessing of {raw_path}...")
    try:
        # Load with latin1, skip bad lines
        df = pd.read_csv(raw_path, sep=',', encoding='latin1', on_bad_lines='skip', low_memory=False)
        print(f"Loaded raw data: {df.shape}")

        # --- Basic Cleaning ---
        # Drop potentially empty/unneeded rows/columns if identified
        # df = df.dropna(how='all') # Example: drop rows where ALL columns are NA

        # Standardize Yes/No/Maybe answers (example - adjust based on actual values)
        yes_no_cols = [col for col in df.columns if col.startswith(('q11_', 'q12_', 'q18_', 'q19_', 'q57_', 'q73_', 'q75_', 'q98_'))] # Add other prefixes
        for col in yes_no_cols:
            if df[col].dtype == 'object':
                 df[col] = df[col].str.strip().replace({'Yes': True, 'No': False, 'Maybe': np.nan, '': np.nan, 'Unknown':np.nan, 'Prefer not to say': np.nan}).astype('boolean')


        # --- Type Conversions & Specific Cleaning ---

        # Demographics
        if 'q2_age' in df.columns:
            df['q2_age'] = pd.to_numeric(df['q2_age'], errors='coerce')
        categorical_demographics = ['q1_gender', 'q3_relationship_status', 'q7_current_living_arrangement',
                                    'q8_education_level', 'q9_employment_status', 'q10_household_income_category']
        for col in categorical_demographics:
            if col in df.columns:
                 df[col] = df[col].astype('category')

        # Handle q4_racial_or_ethnic_background (Checkbox example - assumes platform didn't split it)
        # This might need significant adjustment depending on how the CSV stores checkbox results
        if 'q4_racial_or_ethnic_background' in df.columns and df['q4_racial_or_ethnic_background'].dtype == 'object':
            print("Processing Race/Ethnicity checkbox column...")
            # Example: Split comma-separated values into boolean columns
            # Define possible options based on the survey PDF
            race_options = [
                'African', 'Black / African diaspora', 'Caucasian / European', 'East Asian',
                'Indigenous', 'Latin, Hispanic, Central and South American', 'Oceanian',
                'South Asian', 'South East Asian', 'West Central Asian, Middle Eastern and North African',
                'Prefer not to say'
            ]
            # Create boolean columns - this is a basic example, needs refinement based on data format
            for option in race_options:
                col_name = f"q4_race_{option.split(' ')[0].lower()}" # Create a shorter name
                # Check if the option string exists in the comma-separated value (case-insensitive)
                df[col_name] = df['q4_racial_or_ethnic_background'].str.contains(option.split('/')[0].strip(), case=False, na=False).astype('boolean')
            # You might drop the original complex column afterwards
            # df = df.drop(columns=['q4_racial_or_ethnic_background'])

        # Numerical Ratings (e.g., 0-100)
        rating_cols = ['q14_knowledge_ranking', 'q15_experience_ranking', 'q46_positive_experience_rating',
                       'q93_tbi_rate_relief', 'q96_adhd_rate_relief'] # Add others if needed
        for col in rating_cols:
             if col in df.columns:
                  df[col] = pd.to_numeric(df[col], errors='coerce')
                  # Optional: Clamp values to expected range (0-100)
                  # df[col] = df[col].clip(0, 100)

        # Likert Scales (GAD, PHQ, Experience agreement, etc.) - Recode to numeric
        # Example: GAD/PHQ (0, 1, 2, 3) - Check actual values in CSV!
        likert_map_gad_phq = {'Not at all': 0, 'Several days': 1, 'More than half the days': 2, 'Nearly every day': 3}
        gad_phq_cols = [col for col in df.columns if col.startswith(('q79','q80'))]
        for col in gad_phq_cols:
             if col in df.columns and df[col].dtype == 'object':
                  df[col] = df[col].map(likert_map_gad_phq).astype('Int64') # Use nullable Int

        # Example: Agreement scales (Strongly disagree -> Strongly agree as 1-5 or 0-4)
        likert_map_agreement = {'Strongly disagree': 1, 'Moderately disagree': 2, 'Somewhat disagree': 2, # Combine moderate/somewhat if needed
                                'Neither agree nor disagree': 3, 'Neutral': 3,
                                'Somewhat agree': 4, 'Moderately agree': 4, 'Strongly agree': 5}
        agreement_cols = [col for col in df.columns if col.startswith(('q25','q36','q37','q41','q54'))] # Add others
        for col in agreement_cols:
            if col in df.columns and df[col].dtype == 'object':
                 df[col] = df[col].map(likert_map_agreement).astype('Int64')

        # Clean specific problematic columns if identified (like q18a_ times used)
        times_used_cols = [col for col in df.columns if col.startswith('q18a_psychedelic_times_used.')]
        for col in times_used_cols:
            if col in df.columns:
                print(f"Cleaning times used: {col}")
                df[col] = df[col].apply(clean_value)
                # Optionally coerce errors again after custom cleaning
                df[col] = pd.to_numeric(df[col], errors='coerce')


        # --- Final Check & Save ---
        print(f"Preprocessing finished. Final shape: {df.shape}")
        print("\nSample of processed data types:")
        print(df.info()) # Print info to check types

        df.to_parquet(processed_path, index=False)
        print(f"Processed data saved to {processed_path}")

    except Exception as e:
        print(f"Error during preprocessing: {e}", file=sys.stderr)
        raise # Reraise the exception to stop if preprocessing fails

if __name__ == "__main__":
    # Ensure paths are correct relative to where you run this script, or use absolute paths
    # Assumes config.py is in the same directory (src/)
    preprocess_data(config.RAW_DATA_PATH, config.PROCESSED_DATA_PATH)