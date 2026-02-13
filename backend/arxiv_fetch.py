import arxiv
from datetime import datetime, timedelta, date


def fetch_papers_for_date(day: date, category: str = "hep-th", max_results=400):
    """
    Fetch all arXiv papers submitted on a specific UTC date for a given category.
    """

    start = datetime.combine(day, datetime.min.time())
    end = start + timedelta(days=1)

    # Query for the specified category
    query = arxiv.Search(
        query=f"cat:{category}",
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )

    results = []
    seen_ids = set()
    
    for result in query.results():
        published = result.published.replace(tzinfo=None)

        if start <= published < end:
            if result.entry_id not in seen_ids:
                seen_ids.add(result.entry_id)
                
                # result.categories is already a list of strings
                categories = result.categories
                
                results.append({
                    "id": result.entry_id,
                    "title": result.title,
                    "summary": result.summary,
                    "authors": [a.name for a in result.authors],
                    "published": published.isoformat(),
                    "url": result.pdf_url,
                    "categories": categories,
                    "primary_category": result.primary_category,
                })

        # arXiv returns newest first → stop once we pass the day
        if published < start:
            break

    return results