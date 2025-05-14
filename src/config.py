# src/config.py
import os
import altair as alt

# --- File Paths ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "gps_2023.csv")
PROCESSED_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "processed_data.parquet")

# --- Substance Columns & Names (User-friendly key -> actual column name suffix in raw data) ---
SUBSTANCE_NAME_MAP = {
    '2C-B': '2C-B',
    'Ayahuasca': 'Ayahuasca',
    'DMT/5-MeO-DMT': 'DMT_5-MeO-DMT', # Simplified key
    'Ibogaine': 'Iboga_Ibogaine',     # Simplified key
    'Ketamine': 'Ketamine',
    'LSD': 'LSD_Acid',                # Simplified key
    'MDMA/MDA': 'MDMA_MDA',           # Simplified key
    'Mescaline': 'Mescaline',
    'Nitrous Oxide': 'Nitrous__Oxide',
    'Psilocybin': 'Psilocybin',
    'Salvia Divinorum': 'Salvia__Divinorum',
    'Other Psychedelic': 'Other__psychedelic__drug'
}
FULL_SUBSTANCE_COL_NAMES = {
    key: f"q18_lifetime_psychedelic_use.{SUBSTANCE_NAME_MAP[key]}"
    for key in SUBSTANCE_NAME_MAP.keys()
}
SUBSTANCE_NAMES_SORTED = sorted(list(SUBSTANCE_NAME_MAP.keys()))

ALL_OTHER_RESPONDENTS = "All Other Respondents (Non-Reference)"

# --- Default Selections ---
DEFAULT_REFERENCE_SUBSTANCE = 'Ibogaine'
DEFAULT_COMPARISON_SUBSTANCES = ['Psilocybin']

# --- Column Mappings ---
DEMOGRAPHIC_COLS = {
    'Age': ('q2_age', 'numerical'),
    'Gender': ('q1_gender', 'categorical'),
    'Education Level': ('q8_education_level', 'categorical'),
    'Household Income': ('q10_household_income_category', 'categorical'),
    'Relationship Status': ('q3_relationship_status', 'categorical'),
    'Living Arrangement': ('q7_current_living_arrangement', 'categorical'),
}

# --- Color Palettes ---
OKABE_ITO_COLORS = ['#E69F00', '#56B4E9', '#009E73', '#F0E442', '#0072B2', '#D55E00', '#CC79A7']
PALETTES = {
    "Classic Blue/Orange": ['#0072B2', '#D55E00'], # Default for 2 groups
    "Okabe-Ito (Custom)": OKABE_ITO_COLORS,
    "Tableau10 (Scheme)": 'tableau10',
    "Dark2 (Scheme)": 'dark2',
    "Set1 (Scheme)": 'set1',
}
DEMOGRAPHICS_PAGE_CATEGORICAL_PLOT_TYPES = ["Faceted Pie Charts"] # Only Pie Charts
DEMOGRAPHICS_PAGE_NUMERICAL_PLOT_TYPES = ["Density + Box Plot"]   # Only Density + Box

DEFAULT_PALETTE_NAME = "Classic Blue/Orange" 

# --- Plot Types (Per-page definition is better) ---
DEMOGRAPHICS_CATEGORICAL_PLOT_TYPES = ["Grouped Bar (Percentage)", "Grouped Bar (Count)", "Faceted Pie Charts"]
DEMOGRAPHICS_NUMERICAL_PLOT_TYPES = ["Density + Box Plot", "Overlapping Histogram (Count)", "Side-by-Side Box Plots"]
# For Demographics specific request:
DEMOGRAPHICS_PAGE_NUMERICAL_DEFAULT = "Density + Box Plot"

# In standalone_age_dist_plot.py, or could be moved to config.py
# This list defines the color for rank #1 peak, rank #2 peak, etc.
# Tallest peak gets first color, second tallest gets second color, etc.
PEAK_RANK_COLOR_PALETTE = [
    '#000000',  # 1. Black (for highest peak)
    '#8B0000',  # 2. Dark Red
    '#FFA500',  # 3. Orange
    '#FFD700',  # 4. Gold
    '#90EE90',  # 5. Light Green
    '#006400',  # 6. Dark Green
    '#40E0D0',  # 7. Turquoise
    '#0000FF',  # 8. Blue (standard blue)
    '#4B0082',  # 9. Indigo
    '#800080',  # 10. Purple
    '#FF69B4',  # 11. Bright Pink (HotPink)
    '#808080',  # 12. Grey
    # Add more if you have more than 12 groups, or it will cycle.
]

SUBSTANCE_COLOR_MAP = {
    'Ibogaine': '#000000',           # 1. Black
    '2C-B': '#8B0000',               # 2. Dark Red (using your updated Dark Red)
    'Salvia Divinorum': '#ff4e00',   # 3. 
    'Other Psychedelic': '#FFA500',  # 4. 
    'DMT/5-MeO-DMT': '#ffD700',      # 5. 
    'Ketamine': '#90EE90',           # 6.
    'Ayahuasca': '#40E0D0',          # 7. 
    'Nitrous Oxide': '#006400',      # 8. 
    'MDMA/MDA': '#0000FF',           # 9. 
    'Psilocybin': '#800080',         # 10. 
    'LSD': '#FF69B4',                # 11. 
    'Mescaline': '#808080',          # 12. grey
    # Fallback color for any substance not explicitly in this map
    'FallbackColor': '#808080'       # Grey
}

alt.themes.enable('latimes')