"""Conservative English retrieval cues, not clinical negation/NER or diagnosis."""
import re

RETRIEVAL_VERSION = 'positive-source-anchor-gate-v2-audit'
CLAUSES = re.compile(r'[.;!?\n]+|\b(?:but|however|except|yet)\b', re.I)
NEGATION = re.compile(r"\b(?:no|denies|denied|without|negative for|does not have|doesn't have|not experiencing|not reporting)\b", re.I)
UNKNOWN = re.compile(r'\b(?:unknown|uncertain|not known|not assessed|not reported|not provided)\b', re.I)


def positive_text(value):
    """Drop explicit absent/unknown clauses only from retrieval text.

    Negative lists extend to punctuation or but/however/except/yet. Raw patient
    data are never edited. Ambiguous language, mixed languages, temporality and
    double negation are not comprehensively resolved by this limited heuristic.
    """
    kept = []
    for clause in CLAUSES.split(value):
        if UNKNOWN.search(clause):
            continue
        marker = NEGATION.search(clause)
        clause = clause[:marker.start()] if marker else clause
        if clause.strip():
            kept.append(clause.strip())
    return ' '.join(kept)


def normalized_words(value):
    value = value.lower().replace('_', ' ').replace('-', ' ')
    value = re.sub(r'\bdiarrhea\b', 'diarrhoea', value)
    value = re.sub(r'\bfebrile\b', 'fever', value)
    value = re.sub(r'\bhypertension\b', 'elevated blood pressure', value)
    value = re.sub(r'\bwatery (?:stools?|loose stools?)\b', 'watery diarrhoea', value)
    value = re.sub(r'\b(?:high|raised)\s+(?:bp|blood pressure)\b', 'elevated blood pressure', value)
    value = re.sub(r'\bjoint (?:pain|pains)\b', 'arthralgia', value)
    return ' '.join(re.findall(r'[a-z]+', value))


def source_anchor_matches(card, query):
    """Require a positive source-authored symptom phrase, not age/day/token noise.

    Severity/onset adjectives can be omitted for *retrieval consideration* only.
    This never marks a source prerequisite met or a diagnosis confirmed.
    """
    text = ' ' + normalized_words(query) + ' '
    matched = []
    for phrase in card['relevant_symptoms']:
        anchor = normalized_words(phrase)
        anchor = re.sub(r'^(?:(?:acute|severe|persistently)\s+)+', '', anchor)
        if not anchor or anchor in ('pain', 'asymptomatic'):
            continue
        if ' ' + anchor + ' ' in text:
            matched.append(phrase)
    return matched
