from bs4 import BeautifulSoup
from collections import defaultdict


def merge_tables(saved_tables):
    grouped = defaultdict(list)

    # Group only by title
    for item in saved_tables:
        grouped[item["title"]].append(item["html"])

    merged = []
    for title, html_list in grouped.items():
        all_rows = []
        header_html = None

        # Collect rows from all tables with same title
        for html in html_list:
            soup = BeautifulSoup(html, "html.parser")

            # Save header from first table only
            if header_html is None:
                thead = soup.find("thead")
                header_html = str(thead) if thead else "<thead></thead>"

            tbody = soup.find("tbody")
            if tbody:
                all_rows.extend(tbody.find_all("tr"))

        # Build merged table
        merged_html = f"""
        <table border="1" class="dataframe">
          {header_html}
          <tbody>
            {''.join(str(row) for row in all_rows)}
          </tbody>
        </table>
        """

        merged.append({"title": title, "html": merged_html})

    return merged

