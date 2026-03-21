"""Fetch recent publications from Google Scholar and update README.md."""

import re
import sys
from scholarly import scholarly

SCHOLAR_ID = "zFqBbIkAAAAJ"
MAX_PUBS = 5

START_MARKER = "<!-- PUBLICATIONS:START -->"
END_MARKER = "<!-- PUBLICATIONS:END -->"


def fetch_publications():
    author = scholarly.search_author_id(SCHOLAR_ID)
    author = scholarly.fill(author, sections=["publications"])

    pubs = sorted(
        author["publications"],
        key=lambda p: p["bib"].get("pub_year", "0"),
        reverse=True,
    )[:MAX_PUBS]

    lines = []
    for pub in pubs:
        title = pub["bib"].get("title", "Untitled")
        year = pub["bib"].get("pub_year", "")
        venue = pub["bib"].get("citation", "")
        # Clean up venue — take first part before comma if long
        if len(venue) > 60:
            venue = venue.split(",")[0]
        url = f"https://scholar.google.com/citations?view_op=view_citation&hl=en&user={SCHOLAR_ID}&citation_for_view={SCHOLAR_ID}:{pub['author_pub_id'].split(':')[-1]}"
        lines.append(f"- [{title}]({url}) — *{venue}, {year}*")

    return "\n".join(lines)


def update_readme(publications_md):
    with open("README.md", "r") as f:
        content = f.read()

    pattern = re.compile(
        rf"{re.escape(START_MARKER)}.*?{re.escape(END_MARKER)}",
        re.DOTALL,
    )
    replacement = f"{START_MARKER}\n{publications_md}\n{END_MARKER}"
    new_content = pattern.sub(replacement, content)

    if new_content == content:
        print("No changes to README.md")
        return False

    with open("README.md", "w") as f:
        f.write(new_content)
    print("README.md updated with latest publications")
    return True


if __name__ == "__main__":
    try:
        pubs = fetch_publications()
        update_readme(pubs)
    except Exception as e:
        print(f"Failed to fetch publications: {e}", file=sys.stderr)
        sys.exit(1)
