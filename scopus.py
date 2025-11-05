import requests
import pandas as pd
import re
import time

def search_scopus(api_key, query, max_results=200):
    url = "https://api.elsevier.com/content/search/scopus"
    headers = {"X-ELS-APIKey": api_key, "Accept": "application/json"}

    all_records = []
    start = 0
    count = 25  # Scopus maximum per request

    while start < max_results:
        params = {
            "query": query,
            "count": count,
            "start": start,
            "view": "STANDARD"
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            return f"Error: {response.status_code} - {response.text}"

        data = response.json()
        articles = data.get("search-results", {}).get("entry", [])

        if not articles:
            break  # stop when no more results

        for article in articles:
            doi = article.get("prism:doi", "")
            link = f"https://doi.org/{doi}" if doi else "No DOI/link"

            authors = article.get("dc:creator", "")
            if authors:
                authors_list = re.split(r'[;,]', authors)
                authors_list = [a.strip() for a in authors_list if a.strip()]
            else:
                authors_list = []

            volume = article.get("prism:volume", "")
            page_range = article.get("prism:pageRange", "")
            issn = article.get("prism:issn", "")
            affiliations = article.get("affiliation", [])
            cited_by_count = article.get("citedby-count", "0")

            affiliation_list = []
            for affil in affiliations:
                affil_name = affil.get("affilname", "")
                affil_city = affil.get("affiliation-city", "")
                affil_country = affil.get("affiliation-country", "")
                affiliation_list.append(f"{affil_name} ({affil_city}, {affil_country})")

            all_records.append({
                "Title": article.get("dc:title", "").strip(),
                "First Author": ", ".join(authors_list),
                "Year": article.get("prism:coverDate", "")[:4],
                "Journal": article.get("prism:publicationName", "").strip(),
                "DOI": doi,
                "Link": link,
                "Volume": volume,
                "Page Range": page_range,
                "ISSN": issn,
                "Affiliations": "; ".join(affiliation_list) if affiliation_list else "No Affiliations",
                "Cited By Count": cited_by_count
            })

        # Check total number of results from API metadata (optional)
        total_results = int(data.get("search-results", {}).get("opensearch:totalResults", 0))
        if start + count >= total_results:
            break  # stop if we’ve reached the end

        start += count
        time.sleep(0.5)  # avoid hitting rate limits

    df = pd.DataFrame(all_records)
    return df
