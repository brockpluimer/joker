# src/analysis.py
import pandas as pd
import numpy as np
from scipy import stats

def _get_cleaned_col_name(col_name): # Ensure this helper is here
    return col_name.replace('q', 'Q').replace('_', ' ').replace('.', ' ').title()

def calculate_summary_stats(df_to_summarize, col_name, group_col_for_stats):
    summary_data = {}
    cleaned_col_name_for_display = _get_cleaned_col_name(col_name)

    if pd.api.types.is_numeric_dtype(df_to_summarize[col_name]):
        grouped = df_to_summarize.groupby(group_col_for_stats)[col_name]
        summary = grouped.agg(
            N='count',
            Mean='mean',
            Median='median',
            StdDev='std',
            Min='min',
            Q1=lambda x: x.quantile(0.25),
            Q3=lambda x: x.quantile(0.75),
            Max='max'
        ).reset_index()
        summary.rename(columns={group_col_for_stats: 'Group'}, inplace=True)
        summary_data['type'] = 'numerical'
        summary_data['dataframe'] = summary.round(2)
        summary_data['title'] = f"Summary Statistics for '{cleaned_col_name_for_display}'"
    else: # Categorical
        counts_df = df_to_summarize.groupby(group_col_for_stats)[col_name].value_counts().rename('N').reset_index()
        percent_df = df_to_summarize.groupby(group_col_for_stats)[col_name].value_counts(normalize=True).mul(100).rename('Percentage (%)').reset_index()
        summary = pd.merge(counts_df, percent_df, on=[group_col_for_stats, col_name])
        summary.rename(columns={group_col_for_stats: 'Group', col_name: 'Category'}, inplace=True)
        summary['Percentage (%)'] = summary['Percentage (%)'].round(1).astype(str) + '%'
        summary_data['type'] = 'categorical'
        # Display N and Percentage for each category, grouped
        summary_data['dataframe'] = summary.set_index(['Group', 'Category']).sort_index()
        summary_data['title'] = f"Distribution for '{cleaned_col_name_for_display}'"
    return summary_data


def format_test_results_html(test_results_str, p_value_for_color=None):
    """Formats test results with HTML for better display, coloring p-value."""
    if p_value_for_color is not None:
        p_value_str = f"{p_value_for_color:.4g}"
        if p_value_for_color < 0.0001:
            p_value_str = "<0.0001"

        color = "red" if p_value_for_color < 0.05 else "inherit" # Or "green" for not significant
        # Replace the p-value in the string with a colored span
        # This is a bit hacky; a more robust way would be to return structured data
        test_results_str = test_results_str.replace(
            f"p-value={p_value_for_color:.4g}",
            f"p-value=<span style='color:{color}; font-weight:bold;'>{p_value_str}</span>"
        )
        test_results_str = test_results_str.replace( # Handle case where p_value was rounded to 0.0000
             f"p-value=0.0000",
             f"p-value=<span style='color:red; font-weight:bold;'><0.0001</span>" # < for <
        )
    # Use <pre> for preserving whitespace and monospace font
    return f"<pre style='font-size: 0.85em; line-height: 1.4;'>{test_results_str}</pre>"


def perform_comparison_tests(df_pair, col_name, ref_group_label, comp_group_label, group_col_for_plot):
    results_list = [] # Store lines of text
    p_value_num = None # Store the numerical p-value for coloring

    results_list.append(f"Comparison: {ref_group_label} vs {comp_group_label}")
    results_list.append(f"Variable: {_get_cleaned_col_name(col_name)}")
    results_list.append("-" * 30)

    group1_data = df_pair[df_pair[group_col_for_plot] == ref_group_label][col_name].dropna()
    group2_data = df_pair[df_pair[group_col_for_plot] == comp_group_label][col_name].dropna()

    n1, n2 = len(group1_data), len(group2_data)
    results_list.append(f"N: {ref_group_label}={n1}, {comp_group_label}={n2}")


    if n1 < 3 or n2 < 3: # Arbitrary small N threshold
        results_list.append("  Skipping test: Insufficient data in one or both groups (N < 3).")
        return "\n".join(results_list), None # Return None for p_value_num

    if pd.api.types.is_numeric_dtype(df_pair[col_name]):
        try:
            # Medians
            median1, median2 = group1_data.median(), group2_data.median()
            results_list.append(f"  Medians: {median1:.1f} vs {median2:.1f}")
            # Mann-Whitney U
            stat, p_value_num = stats.mannwhitneyu(group1_data, group2_data, alternative='two-sided')
            results_list.append(f"  Mann-Whitney U: Test Stat={stat:.2f}, p-value={p_value_num:.4g}")
            results_list.append(f"  Result: {'Significant difference (p < 0.05)' if p_value_num < 0.05 else 'No significant difference (p >= 0.05)'}")
        except ValueError as e:
            results_list.append(f"  Mann-Whitney U test error: {e}")
    else: # Categorical
        try:
            contingency_table = pd.crosstab(df_pair[group_col_for_plot], df_pair[col_name])
            if contingency_table.shape[0] > 1 and contingency_table.shape[1] > 1:
                chi2, p_value_num, dof, expected = stats.chi2_contingency(contingency_table)
                results_list.append(f"  Chi-squared: Test Stat={chi2:.2f}, df={dof}, p-value={p_value_num:.4g}")
                if (expected < 5).any().any():
                     results_list.append("  Warning: Expected cell count < 5. Chi-squared may be unreliable.")
                results_list.append(f"  Result: {'Significant association (p < 0.05)' if p_value_num < 0.05 else 'No significant association (p >= 0.05)'}")
            else:
                 results_list.append("  Chi-squared: Contingency table too small (needs >= 2x2).")
        except ValueError as e:
            results_list.append(f"  Chi-squared test error: {e}")

    return "\n".join(results_list), p_value_num