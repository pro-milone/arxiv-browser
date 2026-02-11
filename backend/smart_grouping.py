import re
from collections import defaultdict

# Define research field patterns (hep-th + quant-ph focused)
FIELD_PATTERNS = {
    "String Theory & M-Theory": [
        r"string theory", r"m-theory", r"superstring", r"heterotic",
        r"type ii", r"string compactification", r"d-brane", r"brane",
        r"worldsheet", r"string amplitude"
    ],
    
    "AdS/CFT & Holography": [
        r"ads/cft", r"ads-cft", r"holograph", r"gauge/gravity",
        r"anti-de sitter", r"conformal field theory", r"cft",
        r"bulk-boundary", r"holographic dual"
    ],
    
    "Quantum Field Theory": [
        r"quantum field theory", r"qft", r"gauge theory", r"yang-mills",
        r"effective field theory", r"renormalization", r"feynman",
        r"perturbative", r"non-perturbative", r"eft\b"
    ],
    
    "Supersymmetry & SUSY": [
        r"supersymmetr", r"susy", r"superfield", r"supergravity",
        r"superspace", r"supertranslation", r"n=\d"
    ],
    
    "Black Holes & Gravity": [
        r"black hole", r"hawking", r"event horizon", r"schwarzschild",
        r"kerr", r"extremal", r"near-horizon", r"microstate",
        r"gravitational wave", r"general relativity"
    ],
    
    "Cosmology": [
        r"cosmolog", r"inflation", r"de sitter", r"cosmological constant",
        r"dark energy", r"primordial", r"cmb", r"early universe",
        r"big bang", r"flrw"
    ],
    
    "Quantum Information & Entanglement": [
        r"entanglement entropy", r"quantum information", r"quantum error correction",
        r"tensor network", r"quantum circuit", r"von neumann entropy",
        r"mutual information", r"page curve", r"quantum complexity",
        r"entanglement measure", r"quantum channel", r"quantum communication"
    ],
    
    "Quantum Computing & Algorithms": [
        r"quantum computing", r"quantum algorithm", r"quantum gate",
        r"quantum supremacy", r"quantum advantage", r"variational quantum",
        r"vqe", r"qaoa", r"quantum annealing", r"adiabatic quantum",
        r"quantum walk", r"grover", r"shor"
    ],
    
    "Quantum Error Correction & Fault Tolerance": [
        r"quantum error correction", r"fault tolerant", r"stabilizer code",
        r"surface code", r"topological code", r"ldpc", r"qec\b",
        r"logical qubit", r"error threshold", r"syndrome"
    ],
    
    "Quantum Cryptography & Security": [
        r"quantum cryptography", r"quantum key distribution", r"qkd\b",
        r"quantum random", r"bb84", r"device-independent",
        r"quantum secure"
    ],
    
    "Quantum Optics & Photonics": [
        r"quantum optics", r"photonic", r"single photon", r"squeezed state",
        r"quantum light", r"parametric down", r"boson sampling",
        r"linear optical", r"cavity qed"
    ],
    
    "Quantum Simulation": [
        r"quantum simulat", r"analog quantum", r"quantum emulat",
        r"cold atom", r"trapped ion", r"rydberg"
    ],
    
    "Quantum Many-Body Physics": [
        r"many-body", r"many body", r"condensed matter", r"quantum phase transition",
        r"quantum spin", r"hubbard", r"quantum magnet", r"frustrated system"
    ],
    
    "Conformal Field Theory": [
        r"conformal field theory", r"conformal symmetry", r"virasoro",
        r"conformal block", r"operator product expansion", r"ope\b",
        r"conformal dimension", r"central charge", r"minimal model"
    ],
    
    "Scattering Amplitudes": [
        r"scattering amplitude", r"amplituhedron", r"on-shell",
        r"bcfw", r"unitarity method", r"loop integral",
        r"feynman diagram", r"cross section"
    ],
    
    "Topological Field Theory": [
        r"topological field theory", r"tqft", r"chern-simons",
        r"topological string", r"topological twist", r"cohomolog",
        r"bv formalism", r"brst"
    ],
    
    "Topological Quantum Matter": [
        r"topological phase", r"topological order", r"anyonic",
        r"majorana", r"quantum hall", r"topological insulator",
        r"kitaev", r"toric code"
    ],
    
    "Lattice & Numerical": [
        r"lattice", r"monte carlo", r"numerical simulation",
        r"discretization", r"lattice gauge theory", r"lattice qcd"
    ],
    
    "Integrable Systems": [
        r"integrabl", r"bethe ansatz", r"yangian", r"quantum group",
        r"r-matrix", r"exactly solvable", r"spin chain"
    ],
    
    "Bootstrap & CFT Methods": [
        r"bootstrap", r"crossing symmetry", r"conformal bootstrap",
        r"numerical bootstrap", r"modular bootstrap", r"s-matrix bootstrap"
    ],
    
    "Anomalies & Symmetries": [
        r"anomaly", r"anomalies", r"chiral", r"global symmetry",
        r"symmetry breaking", r"ward identity", r"noether",
        r"spontaneous symmetry"
    ],
    
    "Open Quantum Systems": [
        r"open quantum system", r"decoherence", r"lindblad",
        r"master equation", r"quantum noise", r"dephasing",
        r"dissipative"
    ],
    
    "Quantum Foundations & Interpretations": [
        r"quantum foundation", r"bell inequality", r"nonlocal",
        r"contextuality", r"quantum measurement", r"collapse",
        r"interpretation", r"hidden variable"
    ],
}

# Technique patterns
TECHNIQUE_PATTERNS = {
    "Perturbative Methods": [
        r"perturbativ", r"feynman diagram", r"loop expansion",
        r"coupling expansion", r"weak coupling"
    ],
    
    "Non-perturbative": [
        r"non-perturbative", r"strong coupling", r"instanton",
        r"soliton", r"monopole", r"duality"
    ],
    
    "Numerical/Computational": [
        r"numerical", r"computation", r"simulation", r"monte carlo",
        r"lattice", r"algorithm"
    ],
    
    "Effective Field Theory": [
        r"effective field theory", r"eft\b", r"wilsonian",
        r"low energy", r"matching condition"
    ],
    
    "Symmetry Analysis": [
        r"symmetry analysis", r"lie algebra", r"representation theory",
        r"group theory", r"coset"
    ],
    
    "Geometric Methods": [
        r"geometric", r"differential geometry", r"kähler",
        r"calabi-yau", r"complex manifold", r"fiber bundle"
    ],
}


def _matches_pattern(text, patterns):
    """Check if text matches any pattern in the list."""
    text_lower = text.lower()
    for pattern in patterns:
        if re.search(pattern, text_lower):
            return True
    return False


def classify_paper(paper):
    """
    Classify a paper into research fields and techniques.
    Returns dict with 'fields' and 'techniques' lists.
    """
    text = f"{paper.get('title', '')} {paper.get('summary', '')}"
    
    fields = []
    for field_name, patterns in FIELD_PATTERNS.items():
        if _matches_pattern(text, patterns):
            fields.append(field_name)
    
    techniques = []
    for tech_name, patterns in TECHNIQUE_PATTERNS.items():
        if _matches_pattern(text, patterns):
            techniques.append(tech_name)
    
    return {
        'fields': fields if fields else ['General/Other'],
        'techniques': techniques
    }


def group_papers(papers, min_group_size=1):
    """
    Group papers by research field, then annotate with techniques.
    Returns groups with descriptive labels.
    """
    if not papers:
        return []
    
    # Classify all papers
    classified = []
    for paper in papers:
        classification = classify_paper(paper)
        classified.append({
            'paper': paper,
            'fields': classification['fields'],
            'techniques': classification['techniques']
        })
    
    # Group by primary field
    field_groups = defaultdict(list)
    for item in classified:
        primary_field = item['fields'][0]  # Use first matched field
        field_groups[primary_field].append(item)
    
    # Build output groups
    output = []
    for field, items in field_groups.items():
        if len(items) < min_group_size:
            continue
        
        # Collect common techniques
        technique_counts = defaultdict(int)
        for item in items:
            for tech in item['techniques']:
                technique_counts[tech] += 1
        
        # Get top techniques
        top_techniques = sorted(
            technique_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:2]
        
        # Build label
        label = field
        if top_techniques and top_techniques[0][1] >= 2:
            tech_names = [t[0] for t in top_techniques if t[1] >= 2]
            if tech_names:
                label = f"{field} ({', '.join(tech_names)})"
        
        output.append({
            'keywords': [label],  # Single descriptive label
            'papers': [item['paper'] for item in items],
            'field': field,
            'techniques': dict(top_techniques)
        })
    
    # Sort by number of papers (largest first)
    output.sort(key=lambda x: len(x['papers']), reverse=True)
    
    return output


def get_field_color(field_name):
    """
    Return a color for each field (for potential UI enhancement).
    """
    colors = {
        "String Theory & M-Theory": "#FF6B6B",
        "AdS/CFT & Holography": "#4ECDC4",
        "Quantum Field Theory": "#45B7D1",
        "Supersymmetry & SUSY": "#FFA07A",
        "Black Holes & Gravity": "#9B59B6",
        "Cosmology": "#E74C3C",
        "Quantum Information & Entanglement": "#3498DB",
        "Quantum Computing & Algorithms": "#2ECC71",
        "Quantum Error Correction & Fault Tolerance": "#1ABC9C",
        "Quantum Cryptography & Security": "#16A085",
        "Quantum Optics & Photonics": "#F39C12",
        "Quantum Simulation": "#E67E22",
        "Quantum Many-Body Physics": "#D35400",
        "Conformal Field Theory": "#27AE60",
        "Scattering Amplitudes": "#F39C12",
        "Topological Field Theory": "#1ABC9C",
        "Topological Quantum Matter": "#8E44AD",
        "Lattice & Numerical": "#95A5A6",
        "Integrable Systems": "#E67E22",
        "Bootstrap & CFT Methods": "#16A085",
        "Anomalies & Symmetries": "#D35400",
        "Open Quantum Systems": "#3498DB",
        "Quantum Foundations & Interpretations": "#9B59B6",
        "General/Other": "#7F8C8D"
    }
    return colors.get(field_name, "#95A5A6")