import streamlit as st
import pandas as pd
from datetime import datetime
from scopus import search_scopus


def main():
    # Title
    st.title("Scopus Article Search")

    # API key input
    api_key = st.text_input("Enter your Scopus API Key", type="password")

    # Search query input
    query = st.text_input(
        "Enter your search query (keywords)",
        placeholder='Example: "Knowledge graphs" AND "large language models"'
    )

    # Get current year for slider upper limit
    current_year = datetime.now().year

    # Year range slider
    year_range = st.slider(
        "Select publication year range",
        min_value=1990,
        max_value=current_year,
        value=(current_year - 5, current_year),
        step=1
    )

    # Max results slider
    max_results = st.slider(
        "Maximum number of results to fetch",
        min_value=25,
        max_value=500,
        value=100,
        step=25,
        help="Scopus API returns 25 results per request. This option allows multiple paginated requests."
    )

    # Search button
    if st.button("Search"):
        if api_key and query:
            start_year, end_year = year_range

            # Build Scopus query with year range
            if start_year == end_year:
                full_query = f"{query} AND PUBYEAR IS {start_year}"
            else:
                full_query = f"{query} AND PUBYEAR > {start_year - 1} AND PUBYEAR < {end_year + 1}"

            # Display spinner while searching
            with st.spinner("Searching Scopus... Please wait."):
                # Perform the search with pagination
                result = search_scopus(api_key, full_query, max_results=max_results)

            # Display results
            if isinstance(result, pd.DataFrame):
                st.success(f"Showing up to {max_results} results for {start_year}–{end_year}")
                st.dataframe(result)

                # Download as CSV
                st.download_button(
                    label="Download CSV",
                    data=result.to_csv(index=False),
                    file_name=f"scopus_articles_{start_year}_{end_year}.csv",
                    mime="text/csv"
                )
            else:
                st.error(result)
        else:
            st.warning("Please enter your API Key and a search query.")


if __name__ == "__main__":
    main()
