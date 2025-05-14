# src/plotting.py
import altair as alt
import pandas as pd
from src import config # Use 'from src import config'

def _get_cleaned_col_name(col_name):
    """Helper to clean column names for titles and labels."""
    if not isinstance(col_name, str): # Handle cases where col_name might not be a string yet
        return str(col_name)
    return col_name.replace('q', 'Q').replace('_', ' ').replace('.', ' ').title()

def _create_color_scale(group_names_in_plot_data, selected_palette_config_value):
    """
    Creates an Altair color scale for the groups present in the current plot data.
    `selected_palette_config_value` can be an Altair scheme name (str) or a list of hex colors.
    """
    unique_groups_sorted = sorted(list(group_names_in_plot_data))

    if isinstance(selected_palette_config_value, str): # It's an Altair scheme name
        return alt.Scale(domain=unique_groups_sorted, scheme=selected_palette_config_value)
    elif isinstance(selected_palette_config_value, list): # It's a custom list of hex colors
        num_groups = len(unique_groups_sorted)
        color_range = [selected_palette_config_value[i % len(selected_palette_config_value)] for i in range(num_groups)]
        return alt.Scale(domain=unique_groups_sorted, range=color_range)
    else: # Fallback if palette config is unexpected
        # print(f"Warning: Unexpected palette configuration '{selected_palette_config_value}'. Using fallback.")
        return alt.Scale(domain=unique_groups_sorted, scheme='tableau10')


# --- CATEGORICAL PLOT FUNCTIONS ---

def plot_grouped_bar_percentage(df_pair, col_name, ref_group_label, comp_group_label, group_col_for_plot, palette_config_value):
    y_axis_title = _get_cleaned_col_name(col_name)
    chart_title = f"{ref_group_label} vs {comp_group_label}: {y_axis_title} (% within Group)"
    # For grouped bars comparing two main groups, we usually color by those groups.
    # The palette_config_value should be a list of two colors or a scheme suitable for two.
    color_scale = _create_color_scale([ref_group_label, comp_group_label], palette_config_value)


    # Calculate percentage within each group for each category
    plot_data = df_pair.groupby(group_col_for_plot)[col_name].value_counts(normalize=True).mul(100).rename('percentage').reset_index()
    # Get counts for tooltips
    counts_data = df_pair.groupby([group_col_for_plot, col_name]).size().rename('count').reset_index()
    plot_data = pd.merge(plot_data, counts_data, on=[group_col_for_plot, col_name])

    chart = alt.Chart(plot_data).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
        x=alt.X(f'{col_name}:N', title=y_axis_title, sort='-y', axis=alt.Axis(labelAngle=-45)), # Categories on X, sort by count
        y=alt.Y('percentage:Q', axis=alt.Axis(format='.0f', title='Percentage of Group Members'), scale=alt.Scale(domain=[0, 100])),
        color=alt.Color(f'{group_col_for_plot}:N', scale=color_scale, legend=alt.Legend(title="User Group", orient="top-left")),
        xOffset=f'{group_col_for_plot}:N', # Creates the grouped effect
        tooltip=[
            alt.Tooltip(f'{group_col_for_plot}:N', title='Group'),
            alt.Tooltip(f'{col_name}:N', title=y_axis_title),
            alt.Tooltip('percentage:Q', title='Percentage', format='.1f'),
            alt.Tooltip('count:Q', title='Count (N)')
        ]
    ).properties(
        title=alt.TitleParams(text=chart_title, anchor="middle")
    ).configure_axis(
        grid=False # Cleaner look by removing grid for grouped bars if preferred
    ).configure_view(
        stroke=None
    )
    return chart

def plot_grouped_bar_count(df_pair, col_name, ref_group_label, comp_group_label, group_col_for_plot, palette_config_value):
    y_axis_title = _get_cleaned_col_name(col_name)
    chart_title = f"{ref_group_label} vs {comp_group_label}: {y_axis_title} (Counts)"
    color_scale = _create_color_scale([ref_group_label, comp_group_label], palette_config_value)

    chart = alt.Chart(df_pair).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
        x=alt.X(f'{col_name}:N', title=y_axis_title, sort='-y', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('count():Q', title='Number of Respondents'),
        color=alt.Color(f'{group_col_for_plot}:N', scale=color_scale, legend=alt.Legend(title="User Group", orient="top-left")),
        xOffset=f'{group_col_for_plot}:N',
        tooltip=[
            alt.Tooltip(f'{group_col_for_plot}:N', title='Group'),
            alt.Tooltip(f'{col_name}:N', title=y_axis_title),
            alt.Tooltip('count():Q', title='Count (N)')
        ]
    ).properties(
        title=alt.TitleParams(text=chart_title, anchor="middle")
    ).configure_axis(
        grid=False
    ).configure_view(
        stroke=None
    )
    return chart

def plot_faceted_pie_charts(df_pair, col_name, ref_group_label, comp_group_label, group_col_for_plot, palette_config_value_ignored_for_slices):
    y_axis_title_cleaned = _get_cleaned_col_name(col_name)
    category_color_scheme = 'tableau20' # A broad scheme for categories within pies

    pie_charts_list = []
    # Increased size for better readability, especially with labels
    chart_width = 320
    chart_height = 320

    # Determine the overall sort order of categories based on total counts across both groups
    # This helps in making the pie charts visually comparable if using the same color scheme for slices
    category_order = df_pair[col_name].dropna().value_counts().index.tolist()

    for i, group_label in enumerate([ref_group_label, comp_group_label]):
        group_data = df_pair[df_pair[group_col_for_plot] == group_label].copy()
        if group_data.empty or group_data[col_name].nunique() == 0:
            empty_chart_text = f"No data for {group_label}"
            empty_chart = alt.Chart(pd.DataFrame({'text': [empty_chart_text]})).mark_text(size=14, align="center", baseline="middle").encode(
                text='text:N'
            ).properties(title=alt.TitleParams(text=f"{group_label}: {y_axis_title_cleaned}", anchor="middle", dy=-15), width=chart_width, height=chart_height)
            pie_charts_list.append(empty_chart)
            continue

        # Calculate percentage for labels within this group's data
        group_data['percentage'] = group_data.groupby(col_name)[col_name].transform('count') / len(group_data) * 100

        pie_title_text = f"{group_label}: {y_axis_title_cleaned}"

        base = alt.Chart(group_data).encode(
            theta=alt.Theta("count():Q", stack=True),
            color=alt.Color(f"{col_name}:N",
                          scale=alt.Scale(scheme=category_color_scheme, domain=category_order), # Consistent color mapping
                          legend=alt.Legend(title=None, # Remove redundant legend title
                                            orient="right" if i == 0 else "none",
                                            symbolLimit=10, labelLimit=180, titleLimit=0, padding=10,
                                            columns=1, labelFontSize=10, titleFontSize=11) if i == 0 else None
                         ),
            tooltip=[
                alt.Tooltip(f"{col_name}:N", title=y_axis_title_cleaned),
                alt.Tooltip("count():Q", title="N"),
                alt.Tooltip("percentage:Q", title="%", format=".1f")
            ]
        ).properties(title=alt.TitleParams(text=pie_title_text, anchor="middle", dy=-15), width=chart_width, height=chart_height)

        pie = base.mark_arc(innerRadius=40, outerRadius=120, stroke="#fff", strokeWidth=1.5)

        text = base.mark_text(radiusOffset=20, fontSize=9, fill="black").encode(
            text=alt.condition(
                alt.datum['percentage'] > 7, # Threshold for label visibility
                alt.Text("percentage:Q", format=".0f"),
                alt.value('')
            )
        )
        pie_charts_list.append(pie + text)

    if not pie_charts_list: return alt.Chart().mark_text(text="No data available for pie charts.").to_dict()
    
    # Concatenate. If only one valid pie, it will just show that one.
    if len(pie_charts_list) == 1:
        return pie_charts_list[0]
    elif len(pie_charts_list) > 1:
        return alt.hconcat(*pie_charts_list).resolve_legend(color="shared")
    else: # Should not happen if previous check is correct
        return alt.Chart().mark_text(text="Error generating pie charts.").to_dict()


# --- NUMERICAL PLOT FUNCTIONS ---
def plot_density_boxplot(df_pair, col_name, ref_group_label, comp_group_label, group_col_for_plot, palette_config_value, opacity=0.55):
    x_axis_title = _get_cleaned_col_name(col_name)
    chart_title = f"{ref_group_label} vs {comp_group_label}: {x_axis_title} Distribution"
    current_groups_in_df = df_pair[group_col_for_plot].unique()
    color_scale = _create_color_scale(current_groups_in_df, palette_config_value)

    density_plot = alt.Chart(df_pair).transform_density(
        density=col_name,
        groupby=[group_col_for_plot],
        steps=200,
        extent=[df_pair[col_name].min(), df_pair[col_name].max()]
    ).mark_area(opacity=opacity, line={'color': 'grey', 'width': 0.7}).encode(
        alt.X('value:Q', title=x_axis_title, scale=alt.Scale(zero=False)),
        alt.Y('density:Q', title='Density', axis=alt.Axis(format='.1%')),
        alt.Color(f'{group_col_for_plot}:N', scale=color_scale, legend=alt.Legend(title="User Group", orient="top-right")), # Legend top-right
        tooltip=[
            alt.Tooltip(f'{group_col_for_plot}:N', title='Group'),
            alt.Tooltip(f'mean({col_name})', title=f'Overall Mean', format='.1f'),
            alt.Tooltip(f'median({col_name})', title=f'Overall Median', format='.1f'),
            alt.Tooltip(f'count({col_name})', title=f'N (in group)')
        ]
    ).properties(height=300)

    boxplot_summary_df = _calculate_boxplot_stats(df_pair, group_col_for_plot, col_name)
    base_box = alt.Chart(boxplot_summary_df).encode(
        y=alt.Y(f'{group_col_for_plot}:N', title=None, axis=alt.Axis(labels=False, ticks=False, domain=False)),
        color=alt.Color(f'{group_col_for_plot}:N', scale=color_scale, legend=None),
        tooltip=[
            alt.Tooltip(f'{group_col_for_plot}:N', title='Group'),
            alt.Tooltip('min_val:Q', title='Min', format='.1f'),
            alt.Tooltip('q1:Q', title='Q1 (25th)', format='.1f'),
            alt.Tooltip('median:Q', title='Median (50th)', format='.1f'),
            alt.Tooltip('q3:Q', title='Q3 (75th)', format='.1f'),
            alt.Tooltip('max_val:Q', title='Max', format='.1f'),
            alt.Tooltip('count:Q', title='N (for var)')
        ]
    )
    box = base_box.mark_bar(size=25, stroke='black', strokeWidth=0.7, cornerRadius=2).encode(
        x=alt.X('q1:Q', title=None, axis=alt.Axis(labels=False, ticks=False, grid=False)),
        x2='q3:Q'
    )
    median_tick = base_box.mark_tick(color='white', size=23, thickness=3, opacity=1).encode(x='median:Q') # Ensure median visible
    lower_whisker = base_box.mark_rule(stroke='black', strokeWidth=1).encode(x='min_val:Q', x2='q1:Q')
    upper_whisker = base_box.mark_rule(stroke='black', strokeWidth=1).encode(x='q3:Q', x2='max_val:Q')
    constructed_box_plot = alt.layer(lower_whisker, upper_whisker, box, median_tick).properties(height=70)

    return alt.vconcat(density_plot, constructed_box_plot, spacing=-5).properties( # Reduced spacing
        title=alt.TitleParams(text=chart_title, anchor="middle")
    ).resolve_scale(x='shared')

def _calculate_boxplot_stats(df, group_col, value_col):
    return df.groupby(group_col)[value_col].agg(
        min_val='min', q1=lambda x: x.quantile(0.25), median='median',
        q3=lambda x: x.quantile(0.75), max_val='max', count='count'
    ).reset_index()

def plot_overlapping_histogram_count(df_pair, col_name, ref_group_label, comp_group_label, group_col_for_plot, palette_config_value, opacity=0.6):
    x_axis_title = _get_cleaned_col_name(col_name)
    chart_title = f"{ref_group_label} vs {comp_group_label}: {x_axis_title} (Counts)"
    color_scale = _create_color_scale([ref_group_label, comp_group_label], palette_config_value)
    chart = alt.Chart(df_pair).mark_bar(binSpacing=0.5, opacity=opacity, cornerRadiusTopLeft=2, cornerRadiusTopRight=2).encode(
        alt.X(f"{col_name}:Q", bin=alt.Bin(maxbins=25), title=x_axis_title),
        alt.Y('count()', stack=None, title='Number of Respondents'),
        alt.Color(f'{group_col_for_plot}:N', scale=color_scale, legend=alt.Legend(title="User Group", orient="top-left")),
        order=alt.Order('count()', sort='descending'), # Attempt to draw larger group first
        tooltip=[alt.Tooltip(f"{col_name}:Q", bin=True, title=x_axis_title), alt.Tooltip('count()', title='Count in Bin'), f'{group_col_for_plot}:N']
    ).properties(title=alt.TitleParams(text=chart_title, anchor="middle"))
    return chart

def plot_side_by_side_boxplot(df_pair, col_name, ref_group_label, comp_group_label, group_col_for_plot, palette_config_value):
    x_axis_title = _get_cleaned_col_name(col_name)
    chart_title = f"{ref_group_label} vs {comp_group_label}: {x_axis_title} (Box Plots)"
    color_scale = _create_color_scale([ref_group_label, comp_group_label], palette_config_value)
    boxplot_summary_df = _calculate_boxplot_stats(df_pair, group_col_for_plot, col_name)
    base_box = alt.Chart(boxplot_summary_df).encode(
        y=alt.Y(f'{group_col_for_plot}:N', title=None, axis=alt.Axis(labels=True, domain=False, ticks=False, title=None, labelPadding=5)),
        color=alt.Color(f'{group_col_for_plot}:N', scale=color_scale, legend=None),
        tooltip=[ alt.Tooltip(f'{group_col_for_plot}:N', title='Group'), alt.Tooltip('min_val:Q', title='Min', format='.1f'), alt.Tooltip('q1:Q', title='Q1 (25th)', format='.1f'), alt.Tooltip('median:Q', title='Median (50th)', format='.1f'), alt.Tooltip('q3:Q', title='Q3 (75th)', format='.1f'), alt.Tooltip('max_val:Q', title='Max', format='.1f'), alt.Tooltip('count:Q', title='N (for var)')]
    )
    box = base_box.mark_bar(size=20, stroke='black', strokeWidth=0.7, cornerRadius=2).encode(x=alt.X('q1:Q', title=x_axis_title), x2='q3:Q')
    median_tick = base_box.mark_tick(color='white', size=18, thickness=2.5, opacity=1).encode(x='median:Q') # Prominent median
    lower_whisker = base_box.mark_rule(stroke='black', strokeWidth=1).encode(x='min_val:Q', x2='q1:Q')
    upper_whisker = base_box.mark_rule(stroke='black', strokeWidth=1).encode(x='q3:Q', x2='max_val:Q')
    chart = alt.layer(lower_whisker, upper_whisker, box, median_tick).properties(title=alt.TitleParams(text=chart_title, anchor="middle"))
    return chart