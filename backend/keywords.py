from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

# Aggressive removal of generic words that pollute hep-th / quant-ph clouds
GENERIC_STOPWORDS = {
    "quantum", "theory", "model", "paper", "result", "approach", "analysis",
    "system", "systems", "method", "methods", "study", "using", "based",
    "general", "simple", "finite", "classical", "non", "new", "field",
    "state", "states", "dynamics", "properties", "effects"
}

# Curated technical phrases that should survive TF–IDF pruning
TECH_PHRASE_WHITELIST = {
    "ads cft", "conformal field theory", "effective field theory",
    "entanglement entropy", "tensor networks", "quantum error correction",
    "scattering amplitudes", "cosmological correlators",
    "modular bootstrap", "renormalization group",
    "black hole entropy", "de sitter", "holographic duality",
    "topological phases", "lattice gauge theory",
    "non hermitian", "quantum circuits", "quantum information"
}


def _clean_phrase(p):
    return re.sub(r"[^a-z\s]", "", p.lower()).strip()


def group_papers(papers, similarity_threshold=0.1, max_keywords=4):
    """
    Cluster papers by abstract similarity and extract *technical* phrases
    suitable for a compact keyword cloud.
    """

    if not papers:
        return []

    valid = [p for p in papers if p.get("summary", "").strip()]
    if not valid:
        return [{
            "keywords": ["misc"],
            "papers": papers
        }]

    texts = [p["summary"] for p in valid]

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(2, 3),          # force phrases
        max_df=0.85,
        min_df=1,
        max_features=1200
    )

    tfidf = vectorizer.fit_transform(texts)
    sim = cosine_similarity(tfidf)

    visited = set()
    groups = []

    for i in range(len(valid)):
        if i in visited:
            continue

        cluster = [i]
        visited.add(i)

        for j in range(len(valid)):
            if j not in visited and sim[i, j] >= similarity_threshold:
                cluster.append(j)
                visited.add(j)

        groups.append(cluster)

    features = np.array(vectorizer.get_feature_names_out())
    output = []

    for g in groups:
        centroid = tfidf[g].mean(axis=0).A1
        ranked = features[np.argsort(-centroid)]

        keywords = []
        for k in ranked:
            ck = _clean_phrase(k)
            if (
                ck not in GENERIC_STOPWORDS
                and len(ck.split()) >= 2
            ):
                keywords.append(k)
            if len(keywords) >= max_keywords:
                break

        # Fallback: whitelist rescue
        if not keywords:
            for w in TECH_PHRASE_WHITELIST:
                if any(w in v["summary"].lower() for v in [valid[i] for i in g]):
                    keywords.append(w)
                    break

        if not keywords:
            keywords = ["misc"]

        output.append({
            "keywords": keywords,
            "papers": [valid[i] for i in g]
        })

    # Largest clusters first → visual prominence
    output.sort(key=lambda x: len(x["papers"]), reverse=True)
    return output
