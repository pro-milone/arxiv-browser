from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta

from .arxiv_fetch import fetch_papers_for_date
from .smart_grouping import group_papers

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/papers/week")
def papers_week():
    today = datetime.utcnow().date()
    response = {}

    for offset in range(7):
        day = today - timedelta(days=offset)
        papers = fetch_papers_for_date(day)
        groups = group_papers(papers, min_group_size=1)
        
        # Format papers to match what frontend expects
        for group in groups:
            for paper in group["papers"]:
                paper["link"] = paper.get("url", paper.get("id", ""))
                paper["abstract"] = paper.get("summary", "")

        response[day.isoformat()] = groups

    return response
