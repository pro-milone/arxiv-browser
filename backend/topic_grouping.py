from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import math


def group_papers_by_topic(papers, max_topics=6):
    """
    Groups papers into broad topical clusters.
    Always returns at least one group.
    Never raises due to empty input.
    """

    if not papers:
        return []

    # Build documents safely
    documents = []
    valid_papers = []

    for p in papers:
        text = f"{p.get('title', '')} {p.get('summary', '')}".strip()
        if text:
            documents.append(text)
            valid_papers.append(p)

    # If everything was empty → single fallback group
    if not documents:
        return [{
            "topic": "Uncategorized",
            "count": len(papers),
            "papers": papers
        }]

    # Decide cluster count (broad, non-fragmented)
    k = min(max_topics, max(1, math.ceil(len(documents) / 8)))

    # If too small for clustering → no TF-IDF
    if len(documents) < 3:
        return [{
            "topic": "General Research",
            "count": len(valid_papers),
            "papers": valid_papers
        }]

    # TF-IDF with safe settings
    vectorizer = TfidfVectorizer(
        stop_words="english",
        min_df=1,
        max_df=0.9
    )

    try:
        tfidf = vectorizer.fit_transform(documents)
    except ValueError:
        # Absolute safety net
        return [{
            "topic": "General Research",
            "count": len(valid_papers),
            "papers": valid_papers
        }]

    # KMeans clustering
    model = KMeans(n_clusters=k, n_init=10, random_state=42)
    labels = model.fit_predict(tfidf)

    terms = vectorizer.get_feature_names_out()

    clusters = {}
    for idx, label in enumerate(labels):
        clusters.setdefault(label, []).append(valid_papers[idx])

    grouped = []
    for label, group in clusters.items():
        centroid = model.cluster_centers_[label]
        top_idx = centroid.argsort()[-3:][::-1]
        topic = " / ".join(terms[i] for i in top_idx)

        grouped.append({
            "topic": topic or "General Research",
            "count": len(group),
            "papers": group
        })

    return grouped
