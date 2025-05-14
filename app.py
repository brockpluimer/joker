# app.py
import streamlit as st
from PIL import Image # Optional: To display an image/logo

# --- Page Configuration (Sets defaults for all pages) ---
# This should be the first Streamlit command in your script
st.set_page_config(
    page_title="GPS2023 Analyzer",
    page_icon="📊", # You can use emojis or paths to favicons
    layout="wide", # Use wide layout for more space
    initial_sidebar_state="expanded", # Keep sidebar open initially
    menu_items={
        'Get Help': 'https://www.example.com/help', # Replace with actual link if you have one
        'Report a bug': "https://www.example.com/bug", # Replace with actual link
        'About': """
        ## GPS2023 Survey Analyzer
        This app provides tools for Exploratory Data Analysis (EDA)
        of the Global Psychedelic Survey 2023 dataset.
        Select analysis pages from the sidebar.
        (Note: Uses processed data assuming preprocessing script has been run.)
        """
    }
)

# --- Main Landing Page Content ---

# --- Title ---
st.title("Welcome to the GPS2023 Survey Analyzer 📊")
st.markdown("---") # Visual separator

# --- Optional: Logo/Image ---
# try:
#     # Make sure you have an image file (e.g., logo.png) in your project directory
#     image_path = "logo.png" # Adjust path as needed
#     image = Image.open(image_path)
#     st.image(image, width=200) # Adjust width as needed
# except FileNotFoundError:
#     st.warning("Optional logo file not found.")

# --- Introduction and Guidance ---
st.header("Explore Psychedelic User Data from GPS 2023")

st.markdown(
    """
    This interactive application allows you to explore and compare different user groups
    based on the responses from the Global Psychedelic Survey 2023.

    Navigate through different analysis sections using the sidebar on the left.

    ### How to Use:
    1.  **👈 Select an Analysis Page:** Choose a category like "Demographics", "Use Patterns", etc., from the sidebar navigation.
    2.  **⚙️ Configure Options:** Within each page, use the sidebar or main panel options to select user groups, variables, and plot types.
    3.  **📈 View Results:** Interactive plots and summary statistics will be displayed in the main area.
    4.  **💾 Download Data:** Use the download buttons (where available) to get the data subset used for specific plots.

    ---
    *Please ensure the preprocessing script (`src/preprocessing.py`) has been run at least once to generate the necessary `processed_data.parquet` file in the `data/` directory before using the analysis pages.*
    """
)

# --- Optional: Link to Source/More Info ---
st.markdown(
    """
    For more information about the survey or data, please refer to:
    [Link to Survey Source or Paper - Replace Me]
    """
)

# --- Sidebar Customization (Optional Global Items) ---
# Items placed here in app.py will appear *above* the page navigation in the sidebar
st.sidebar.header("Global Options")
st.sidebar.info("Options here might apply across pages (if implemented). Page-specific options appear when you navigate to a page.")
# Example: Could add a global theme selector here later

# --- End of app.py ---
# Streamlit automatically handles the rest based on the 'pages/' directory