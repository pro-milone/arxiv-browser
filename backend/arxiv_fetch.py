import arxiv
from datetime import datetime, timedelta, date


def fetch_papers_for_date(day: date, max_results=400):
    """
    Fetch all arXiv papers submitted on a specific UTC date.
    Includes both hep-th and quant-ph categories, including cross-submissions.
    """

    start = datetime.combine(day, datetime.min.time())
    end = start + timedelta(days=1)

    # Query for both hep-th and quant-ph
    # Using OR operator to get papers from either category
    query = arxiv.Search(
        query="cat:hep-th OR cat:quant-ph",
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )

    results = []
    seen_ids = set()  # Deduplicate cross-submissions
    
    for result in query.results():
        published = result.published.replace(tzinfo=None)

        if start <= published < end:
            # Deduplicate by ID (in case a paper appears in both searches)
            if result.entry_id not in seen_ids:
                seen_ids.add(result.entry_id)
                
                # Extract all categories for the paper
                # result.categories is already a list of strings
                categories = result.categories
                
                results.append({
                    "id": result.entry_id,
                    "title": result.title,
                    "summary": result.summary,
                    "authors": [a.name for a in result.authors],
                    "published": published.isoformat(),
                    "url": result.pdf_url,
                    "categories": categories,  # Include all categories
                    "primary_category": result.primary_category,
                })

        # arXiv returns newest first → stop once we pass the day
        if published < start:
            break

    return results