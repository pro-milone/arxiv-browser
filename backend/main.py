from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import os

from arxiv_fetch import fetch_papers_for_date
from smart_grouping import group_papers

app = FastAPI()

# Update CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",  # Your Vercel domain
        "http://localhost:3000",  # Local development
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "arXiv Research Board API"}

@app.get("/papers/week")
def papers_week(category: str = Query(default="hep-th")):
    today = datetime.utcnow().date()
    response = {}

    for offset in range(7):
        day = today - timedelta(days=offset)
        papers = fetch_papers_for_date(day, category=category)
        groups = group_papers(papers, min_group_size=1)
        
        # Format papers to match what frontend expects
        for group in groups:
            for paper in group["papers"]:
                paper["link"] = paper.get("url", paper.get("id", ""))
                paper["abstract"] = paper.get("summary", "")

        response[day.isoformat()] = groups

    return response