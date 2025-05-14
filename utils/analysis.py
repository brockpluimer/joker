# utils/analysis.py
import pandas as pd
from scipy import stats

def perform_comparison_tests(df_pair, col_name, group1_name, group2_name, group_col):
    """
    Performs statistical tests comparing the two specified groups on a given column.
    Returns a formatted string summarizing the test results.
    """
    # (Code is identical to the previous version - calculates test based on the two groups)
    # ... (rest of the function code from the previous version) ...
    results = []
    results.append(f"Statistical Test for '{col_name}' ({group1_name} vs {group2_name}):")

    group1_data = df_pair[df_pair[group_col] == group1_name][col_name].dropna()
    group2_data = df_pair[df_pair[group_col] == group2_name][col_name].dropna()

    if group1_data.empty or group2_data.empty:
        results.append("  Skipping test: One or both groups have no valid data for this variable.")
        return "\n".join(results)

    if pd.api.types.is_numeric_dtype(df_pair[col_name]):
        # Numerical data: Mann-Whitney U test
        try:
            stat, p_val = stats.mannwhitneyu(group1_data, group2_data, alternative='two-sided')
            results.append(f"  Mann-Whitney U test: U={stat:.2f}, p-value={p_val:.4f}")
            results.append(f"  Result: {'Statistically significant difference (p < 0.05)' if p_val < 0.05 else 'No significant difference (p >= 0.05)'}")
            results.append(f"  Medians: {group1_name}={group1_data.median():.1f}, {group2_name}={group2_data.median():.1f}")
        except ValueError as e:
            results.append(f"  Could not perform Mann-Whitney U test: {e}")

    else:
        # Categorical data: Chi-squared test
        try:
            contingency_table = pd.crosstab(df_pair[group_col], df_pair[col_name])
            if contingency_table.shape[0] > 1 and contingency_table.shape[1] > 1:
                chi2, p_val, dof, expected = stats.chi2_contingency(contingency_table)
                results.append(f"  Chi-squared test: Chi2={chi2:.2f}, p-value={p_val:.4f}, df={dof}")
                results.append(f"  Result: {'Statistically significant association (p < 0.05)' if p_val < 0.05 else 'No significant association (p >= 0.05)'}")
            else:
                 results.append("  Skipping Chi-squared test: Contingency table too small (needs >= 2x2).")

        except ValueError as e:
            results.append(f"  Could not perform Chi-squared test: {e}")

    return "\n".join(results)