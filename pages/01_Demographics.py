# pages/01_Demographics.py
import streamlit as st
import pandas as pd
import os

from src import config
from src.data_loader import load_processed_data
from src.plotting import (
    plot_faceted_pie_charts,    # Primary for categorical DEMOGRAPHICS
    plot_density_boxplot,       # Primary for numerical DEMOGRAPHICS
    # Keep others if you want to offer them as options via selectbox
    plot_grouped_bar_percentage,
    plot_grouped_bar_count,
    plot_overlapping_histogram_count,
    plot_side_by_side_boxplot
)
from src.analysis import perform_comparison_tests, calculate_summary_stats, format_test_results_html

@st.cache_data
def convert_df_to_csv(df_to_convert):
   return df_to_convert.to_csv(index=False).encode('utf-8')

# --- Page Config & Title ---
st.header("📊 Demographic Comparison")
st.markdown("Compare demographic profiles between selected psychedelic user groups.")
st.divider()

# --- Load Data ---
df_full = load_processed_data()
if df_full is None: st.stop()

# --- SIDEBAR CONTROLS ---
st.sidebar.header("📊 Demographic Controls")

ref_substance_name_display = st.sidebar.selectbox(
    "1. Reference Group:",
    options=config.SUBSTANCE_NAMES_SORTED,
    index=config.SUBSTANCE_NAMES_SORTED.index(config.DEFAULT_REFERENCE_SUBSTANCE) if config.DEFAULT_REFERENCE_SUBSTANCE in config.SUBSTANCE_NAMES_SORTED else 0,
    key="demographics_ref_group_select_v6"
)
ref_group_col_actual = config.FULL_SUBSTANCE_COL_NAMES.get(ref_substance_name_display)

comp_options = [config.ALL_OTHER_RESPONDENTS] + [s for s in config.SUBSTANCE_NAMES_SORTED if s != ref_substance_name_display]
default_comp_val_list = [name for name in config.DEFAULT_COMPARISON_SUBSTANCES if name in comp_options]
default_comp_val = default_comp_val_list[0] if default_comp_val_list else (comp_options[0] if comp_options else None)

selected_comp_substance_name = st.sidebar.selectbox(
    "2. Comparison Group:",
    options=comp_options,
    index=comp_options.index(default_comp_val) if default_comp_val and default_comp_val in comp_options else 0,
    key="demographics_comp_group_select_v6"
)

mutually_exclusive = st.sidebar.checkbox(
    "Mutually Exclude Reference from Comparison",
    value=True,
    key="demographics_mutual_exclude_v6"
)

demographic_variable_label = st.sidebar.selectbox(
    "3. Demographic Variable:",
    options=list(config.DEMOGRAPHIC_COLS.keys()),
    key="demographics_variable_select_sidebar_v6"
)
actual_col_name, col_type = config.DEMOGRAPHIC_COLS[demographic_variable_label]

# Plot type is now fixed based on col_type for this page, as per request
selected_plot_type = ""
plot_function_to_call = None

if col_type == 'categorical':
    selected_plot_type = "Faceted Pie Charts" # Only option for categorical demographics
    plot_function_to_call = plot_faceted_pie_charts
    # If you want other options later, add them to config.DEMOGRAPHICS_PAGE_CATEGORICAL_PLOT_TYPES
    # and use a selectbox like before.
elif col_type == 'numerical':
    selected_plot_type = "Density + Box Plot" # Only option for numerical demographics
    plot_function_to_call = plot_density_boxplot

st.sidebar.text_input("Active Plot Type:", value=selected_plot_type, disabled=True, key="demog_plot_display_v6")

selected_palette_name = st.sidebar.selectbox(
    "4. Color Palette:", # Palette for Density/Box (pies use their own internal scheme for categories)
    options=list(config.PALETTES.keys()),
    index=list(config.PALETTES.keys()).index(config.DEFAULT_PALETTE_NAME),
    key="demographics_palette_v6"
)
active_palette = config.PALETTES[selected_palette_name]

plot_opacity = 0.55
if selected_plot_type == "Density + Box Plot":
    plot_opacity = st.sidebar.slider(
        "Density Plot Opacity:", min_value=0.1, max_value=1.0, value=0.55, step=0.05,
        key=f"demographics_opacity_v6_{actual_col_name}"
    )

show_stats_tests = st.sidebar.checkbox("Show Significance Tests", value=False, key="demog_show_stats_v6")

# --- Define Reference & Comparison Group Data ---
# ... (This logic for defining df_ref_group, df_comp_group, n_ref, n_comp, labels, df_pair, df_pair_dropna remains the same
#      as the previous version of pages/01_Demographics.py. Ensure labels use the simplified names.)
if not ref_group_col_actual: st.error("Invalid reference group."); st.stop()
is_ref_group = df_full[ref_group_col_actual] == True
df_ref_group = df_full[is_ref_group].copy()
n_ref = df_ref_group.shape[0]
ref_group_display_label = f"{ref_substance_name_display} Users" # Simplified

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Reference:** <br>{ref_group_display_label}: **{n_ref}**", unsafe_allow_html=True)

if n_ref == 0: st.warning(f"No users for reference: {ref_substance_name_display}."); st.stop()
if not selected_comp_substance_name: st.info("Please select a comparison group."); st.stop()

df_comp_group = pd.DataFrame()
comp_group_display_label = ""
# is_comp_group = pd.Series([False]*len(df_full)) # Not needed, redefined below

if selected_comp_substance_name == config.ALL_OTHER_RESPONDENTS:
    is_comp_group = ~is_ref_group
    df_comp_group = df_full[is_comp_group].copy()
    comp_group_display_label = config.ALL_OTHER_RESPONDENTS
else:
    comp_group_col_actual_for_comp = config.FULL_SUBSTANCE_COL_NAMES.get(selected_comp_substance_name)
    if not comp_group_col_actual_for_comp: st.warning(f"Col for '{selected_comp_substance_name}' not found."); st.stop()
    is_comp_group_raw = df_full[comp_group_col_actual_for_comp] == True
    is_comp_group = is_comp_group_raw & (~is_ref_group) if mutually_exclusive else is_comp_group_raw
    df_comp_group = df_full[is_comp_group].copy()
    comp_group_display_label = f"{selected_comp_substance_name} Users" # Simplified
    if mutually_exclusive and ref_substance_name_display != selected_comp_substance_name:
        comp_group_display_label += f" (Non-{ref_substance_name_display})"

n_comp = df_comp_group.shape[0]
st.sidebar.markdown(f"**Comparison:** <br>{comp_group_display_label}: **{n_comp}**", unsafe_allow_html=True)
st.sidebar.markdown("---")

if n_comp == 0: st.warning(f"No users for comparison: {comp_group_display_label}."); st.stop()

df_ref_group_temp = df_ref_group.copy(); df_ref_group_temp['group_for_plot'] = ref_group_display_label
df_comp_group_temp = df_comp_group.copy(); df_comp_group_temp['group_for_plot'] = comp_group_display_label
df_pair = pd.concat([df_ref_group_temp, df_comp_group_temp], ignore_index=True)
df_pair_dropna = df_pair[[actual_col_name, 'group_for_plot']].dropna(subset=[actual_col_name])

if df_pair_dropna.empty or len(df_pair_dropna['group_for_plot'].unique()) < 2 or \
   df_pair_dropna[df_pair_dropna['group_for_plot'] == ref_group_display_label].empty or \
   df_pair_dropna[df_pair_dropna['group_for_plot'] == comp_group_display_label].empty:
    st.warning(f"Insufficient data for '{demographic_variable_label}' to compare groups after NA removal.")
else:
    # --- Main Content Area ---
    st.subheader(f"Comparison: {ref_substance_name_display} vs. {selected_comp_substance_name}")
    st.caption(f"Comparing {n_ref} {ref_group_display_label} with {n_comp} {comp_group_display_label} on **'{demographic_variable_label}'**.")

    # For Pie Charts, we might want a different layout than for density plots
    if selected_plot_type == "Faceted Pie Charts":
        # Pie charts are generated by plot_faceted_pie_charts and hconcat-ed there.
        # We just display the resulting combined chart.
        try:
            chart = plot_faceted_pie_charts(df_pair_dropna, actual_col_name, ref_group_display_label, comp_group_display_label, 'group_for_plot', active_palette)
            if chart:
                st.altair_chart(chart, use_container_width=True) # Let Streamlit handle width
            else:
                st.warning(f"Could not generate Pie Charts for '{demographic_variable_label}'.")
        except Exception as e:
            st.error(f"Pie Chart Plotting Error for '{demographic_variable_label}':"); st.exception(e)

        # Stats below pie charts
        st.markdown("##### Summary Statistics")
        stats_dict = calculate_summary_stats(df_pair_dropna, actual_col_name, 'group_for_plot')
        st.dataframe(stats_dict['dataframe'], height=(min(12, len(stats_dict['dataframe'])) + 1) * 35 + 3, use_container_width=True)

    else: # For Density+Box plot or other single-chart numerical plots
        plot_col, stats_col = st.columns([0.7, 0.3], gap="large") # 70% for plot, 30% for stats

        with plot_col:
            chart = None
            try:
                if col_type == 'numerical' and selected_plot_type == "Density + Box Plot":
                    chart = plot_density_boxplot(df_pair_dropna, actual_col_name, ref_group_display_label, comp_group_display_label, 'group_for_plot', active_palette, plot_opacity)
                # Add elif for other numerical plot types if re-enabled later
                # elif col_type == 'numerical' and selected_plot_type == "Overlapping Histogram (Count)":
                #     chart = plot_overlapping_histogram_count(...)

                if chart:
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.warning(f"Plot type '{selected_plot_type}' for '{demographic_variable_label}' not configured or no data.")
            except Exception as e:
                st.error(f"Plotting Error for '{demographic_variable_label}':"); st.exception(e)

        with stats_col:
            st.markdown("##### Summary Statistics")
            stats_dict = calculate_summary_stats(df_pair_dropna, actual_col_name, 'group_for_plot')
            st.dataframe(stats_dict['dataframe'], height=(min(12, len(stats_dict['dataframe'])) + 1) * 35 + 3, use_container_width=True)

    # Common elements for both plot types below the plot/stats area
    st.divider()
    if show_stats_tests:
        st.markdown("##### Statistical Test")
        test_results_str, p_val = perform_comparison_tests(df_pair_dropna, actual_col_name, ref_group_display_label, comp_group_display_label, 'group_for_plot')
        st.markdown(format_test_results_html(test_results_str, p_val), unsafe_allow_html=True)
    else:
        st.caption("Enable 'Show Significance Tests' in sidebar.")

    if not df_pair_dropna.empty:
        csv_data = convert_df_to_csv(df_pair_dropna[[actual_col_name, 'group_for_plot']])
        st.download_button(
            label=f"Download Filtered Data", data=csv_data,
            file_name=f"demog_data_{ref_substance_name_display}_vs_{selected_comp_substance_name}_{actual_col_name}.csv",
            mime='text/csv', key=f"download_{selected_comp_substance_name}_{actual_col_name}_v6"
        )
st.divider()
st.caption("Note: If 'Mutually Exclude' is checked, comparison groups exclude users who also used the reference substance.")