import re
from typing import List, Tuple, Dict
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def keyword_found(text: str, patterns: List[str]) -> List[str]:
    found = []
    for pat in patterns:
        if re.search(pat, text, flags=re.IGNORECASE):
            found.append(pat)
    return found

def is_short_deadline(text: str) -> List[str]:
    hits = []
    rush_words = [
        r"\burgent\b",r"\burgently\b",r"\bquick\b",r"\bquickly\b",r"\bfast\b", r"\bimmediately\b", r"\bright away\b", r"\bas soon as possible\b",
        r"\bpriority\b",r"\bimmidiate\b",r"\beod\b", r"\bhigh priority\b",r"\bpriority\b", r"\bcritical\b", r"\bblocker\b", r"\bescalat(e|ion)\b",
        r"\bneeds to be fixed\b", r"\bdeadline\b", r"\breminder\b", r"\bsubmit\b", r"\bfix(ed|ing)?\b"
    ]
    hits += keyword_found(text, rush_words)
    time_phrases = [
        r"\bby eod\b", r"\bbefore eod\b", r"\bend of day\b", r"\btoday\b", r"\btonight\b", r"\bthis evening\b",
        r"\btomorrow\b", r"\bwithin (?:\d+)\s*(?:min|mins|minutes|hr|hrs|hours|day|days)\b", r"\bbefore [0-9]{1,2} ?(am|pm)\b", r"\bbefore \d{1,2}(:\d{2})?\s?(am|pm)?\b"
    ]
    hits += keyword_found(text, time_phrases)
    date_like = [
        r"\b\d{1,2}/\d{1,2}(/\d{2,4})?\b",
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b\d{1,2}\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\b",
        r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\s*\d{1,2}\b",
        r"\bdeadline\b"
    ]
    for pat in date_like:
        if re.search(pat, text, flags=re.IGNORECASE):
            hits.append("time-bound")
            break
    return list(dict.fromkeys(hits))

def business_risk_signals(text: str) -> List[str]:
    patterns = [
        r"\bserver (?:down|error|failure)\b", r"\bprod(?:uction)? issue\b", r"\bcomplain(ing|ed)?\b",
        r"\binvoice\b", r"\bpayment due\b", r"\bpast due\b", r"\boverdue\b", r"\brefund\b", r"\bchargeback\b",
        r"\bcancellation\b", r"\bcancel\b", r"\bchurn\b", r"\bescalation\b", r"\bdowntime\b", r"\boutage\b",
        r"\bP\d\b", r"\bsev[1-3]\b", r"\bSLA\b", r"\bbreach\b", r"\blegal\b", r"\bcontract\b", r"\brenewal\b",
        r"\bdeadline\b", r"\bcomplaint\b", r"\bangry\b", r"\bfrustrated\b", r"\bunhappy\b"
    ]
    return keyword_found(text, patterns)

def stakeholder_signals(text: str) -> List[str]:
    patterns = [
        r"\bCEO\b", r"\bCTO\b", r"\bCFO\b", r"\bVP\b", r"\bdirector\b", r"\bmanager\b", r"\bclient\b", r"\bcustomer\b",
        r"\bpartner\b", r"\bboard\b", r"\binvestor\b", r"\bescalated\b", r"\bescalation\b"
    ]
    return keyword_found(text, patterns)

def scheduling_signals(text: str) -> List[str]:
    patterns = [
        r"\bmeeting\b", r"\bcall\b", r"\bsync\b", r"\bstandup\b", r"\breview\b", r"\bdemo\b", r"\binterview\b",
        r"\bschedule\b", r"\breschedule\b", r"\bfollow up\b", r"\bnewsletter\b"
    ]
    return keyword_found(text, patterns)

def count_question_marks(text: str) -> int:
    return text.count("?")

def compute_priority_score(
    text: str,
    sentiment_label: str,
    compound_score: float
) -> Tuple[str, int, List[str], Dict[str, List[str]]]:
    reasons = []
    debug_matches: Dict[str, List[str]] = {}
    score = 0

    rush_hits = is_short_deadline(text)
    if rush_hits:
        add = 35 + min(25, 7 * (len(rush_hits) - 1))  
        score += add
        reasons.append(f"Time pressure indicators (+{add}).")
        debug_matches["time"] = rush_hits

    risk_hits = business_risk_signals(text)
    if risk_hits:
        add = 25 + min(15, 4 * (len(risk_hits) - 1))
        score += add
        reasons.append(f"Business/production risk keywords (+{add}).")
        debug_matches["risk"] = risk_hits

    stake_hits = stakeholder_signals(text)
    if stake_hits:
        add = 10 + min(10, 2 * (len(stake_hits) - 1))
        score += add
        reasons.append(f"High-visibility stakeholders involved (+{add}).")
        debug_matches["stakeholders"] = stake_hits

    sched_hits = scheduling_signals(text)
    if sched_hits:
        add = 6
        score += add
        reasons.append(f"Scheduling/coordination requested (+{add}).")
        debug_matches["scheduling"] = sched_hits

    # Sentiment influence: negative increases, positive decreases, neutral no effect
    if sentiment_label == "Negative":
        add = 15 + int(10 * min(1.0, abs(compound_score)))
        score += add
        reasons.append(f"Negative tone detected (+{add}).")
    elif sentiment_label == "Positive":
        sub = 8
        score -= sub
        reasons.append(f"Positive tone (−{sub}).")

    qm = count_question_marks(text)
    if qm >= 2:
        add = 5
        score += add
        reasons.append(f"Multiple questions ({qm}) (+{add}).")

    words = len(text.split())
    if words <= 25 and (rush_hits or qm >= 1):
        add = 7
        score += add
        reasons.append(f"Short, action-oriented ask (+{add}).")

    # Adjust for very casual/positive emails (e.g., team outings, greetings)
    if sentiment_label == "Positive" and not (rush_hits or risk_hits or stake_hits):
        score = min(score, 20) 

    score = max(0, min(100, score))

    if score >= 60:
        priority = "High"
    elif score >= 35:
        priority = "Medium"
    else:
        priority = "Low"

    return priority, score, reasons, debug_matches

class EmailClassifier:
    def __init__(self):            
        self.sia = SentimentIntensityAnalyzer()

    def preprocess_text(self, text):
        text = text.lower()
        text = re.sub(r"(?i)^>.*$", "", text, flags=re.MULTILINE)
        text = re.sub(r"(?is)--\s*\n.*$", "", text)
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text

    def predict_sentiment(self, text):
        processed_text = self.preprocess_text(text)
        scores = self.sia.polarity_scores(processed_text)
        compound = scores['compound']
        # Tweak thresholds for more realistic neutral/positive split
        if compound >= 0.15:
            return "Positive"
        elif compound <= -0.15:
            return "Negative"
        else:
            return "Neutral"

    def determine_priority(self, text, sentiment_label=None, compound_score=None):
        processed_text = self.preprocess_text(text)
        if sentiment_label is None or compound_score is None:
            scores = self.sia.polarity_scores(processed_text)
            compound_score = scores['compound']
            if compound_score >= 0.15:
                sentiment_label = "Positive"
            elif compound_score <= -0.15:
                sentiment_label = "Negative"
            else:
                sentiment_label = "Neutral"
        priority, score, reasons, debug_matches = compute_priority_score(
            processed_text, sentiment_label, compound_score
        )
        return priority

    def classify_email(self, email_text):
        sentiment = self.predict_sentiment(email_text)
        scores = self.sia.polarity_scores(self.preprocess_text(email_text))
        priority = self.determine_priority(email_text, sentiment, scores['compound'])
        return sentiment, priority