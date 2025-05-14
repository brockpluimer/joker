# src/data_loader.py
import streamlit as st
import pandas as pd
from src import config # Use 'from src import config'

@st.cache_data
def load_processed_data():
    """Loads the processed Parquet data file."""
    try:
        df = pd.read_parquet(config.PROCESSED_DATA_PATH)
        print(f"Loaded processed data from: {config.PROCESSED_DATA_PATH}")

        # Ensure categorical columns loaded correctly
        for _friendly_name, (col_name, col_type) in config.DEMOGRAPHIC_COLS.items():
            if col_type == 'categorical' and col_name in df.columns:
                if df[col_name].dtype != 'category':
                     df[col_name] = df[col_name].astype('category')
        # Add similar checks for other known categorical columns if needed

        return df
    except FileNotFoundError:
        st.error(f"❌ Processed data file not found: {config.PROCESSED_DATA_PATH}")
        st.error("Please run the preprocessing script first: `python src/preprocessing.py`")
        return None
    except Exception as e:
        st.error(f"Error loading processed data: {e}")
        return None