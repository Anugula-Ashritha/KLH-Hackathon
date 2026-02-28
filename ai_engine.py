# ============================================================
# ai_engine.py — MindBridge AI Engine (Gemini Version)
#
# PRETRAINED MODEL : NRCLex (emotion detection, offline)
# LLM              : Google Gemini 1.5 Flash (free, fast)
#
# PIPELINE:
#   Layer 1 → Crisis keywords  (instant, rule-based)
#   Layer 2 → NRCLex model     (pretrained, local, offline)
#   Layer 3 → Gemini LLM       (smart severity detection)
#   Layer 4 → Keyword fallback (if everything fails)
# ============================================================

import os

# ─── Gemini Setup ─────────────────────────────────────────────
try:
    import google.generativeai as genai
    GEMINI_API_KEY = "AIzaSyAi869jnfbTL-AeYicfaPRb04cYFoS0HqE"   # ← paste AIza... key here
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-2.0-flash")
    llm_client   = True   # keeps sidebar showing green
    print("[ai_engine] ✅ Gemini configured successfully")
except Exception as e:
    gemini_model = None
    llm_client   = None
    print(f"[ai_engine] ⚠️ Gemini error: {e}")

# ─── NRCLex pretrained model ──────────────────────────────────
try:
    from nrclex import NRCLex
    NRCLEX_AVAILABLE = True
    print("[ai_engine] ✅ NRCLex pretrained model loaded")
except Exception as e:
    NRCLEX_AVAILABLE = False
    print(f"[ai_engine] ⚠️ NRCLex not available: {e}")

# ─── NRCLex → Our emotion mapping ────────────────────────────
NRC_LABEL_MAP = {
    "fear":         "anxious",
    "sadness":      "sad",
    "anger":        "angry",
    "disgust":      "angry",
    "anticipation": "stressed",
    "trust":        "positive",
    "joy":          "positive",
    "surprise":     "neutral",
}

# ─── Crisis keywords — always rule-based ─────────────────────
CRISIS_KEYWORDS = [
    "suicide", "kill myself", "end my life", "want to die",
    "don't want to live", "self harm", "hurt myself",
    "no reason to live", "better off dead", "end it all",
    "take my own life", "not worth living", "wish i was dead",
    "cant live anymore", "can't live anymore", "no point living",
]

# ─── Fallback keywords ────────────────────────────────────────
SEVERE_KEYWORDS = [
    "hopeless", "worthless", "can't go on", "give up",
    "nothing matters", "hate myself", "breakdown",
    "falling apart", "trapped", "unbearable",
    "can't take it", "desperate", "numb",
    "empty inside", "completely lost",
]

MODERATE_KEYWORDS = [
    "anxious", "stressed", "overwhelmed", "sad", "depressed",
    "lonely", "scared", "worried", "panic", "angry",
    "frustrated", "nervous", "upset", "struggling",
    "can't sleep", "not okay", "miserable",
]

# ─── Gemini prompts ───────────────────────────────────────────
SEVERITY_PROMPT = """You are a mental health severity classifier.

Classify this message as ONE of: mild, moderate, severe, crisis

- mild     = slightly off, venting, general sadness
- moderate = noticeable anxiety, stress, loneliness, panic
- severe   = hopelessness, worthlessness, breakdown, deep despair
- crisis   = suicidal ideation, self-harm, wanting to die

Rules:
- ONE word only: mild / moderate / severe / crisis
- No punctuation, no explanation
- Err on the side of caution — go higher if unsure
- Indirect phrases like "dark thoughts", "I can't anymore" = severe

Message: "{text}"
Severity:"""

EMOTION_PROMPT = """You are an emotion classifier for a mental health app.

Classify the PRIMARY emotion as ONE of:
anxious / sad / angry / stressed / lonely / positive / neutral

Rules:
- ONE word only
- No punctuation, no explanation
- Pick the strongest emotion

Message: "{text}"
Emotion:"""

# ─── Gemini classify helper ───────────────────────────────────
def _gemini_classify(prompt: str, valid: list, fallback: str) -> str:
    if not gemini_model:
        return fallback
    try:
        response = gemini_model.generate_content(prompt)
        result   = response.text.strip().lower().rstrip(".")
        return result if result in valid else fallback
    except Exception as e:
        print(f"[ai_engine] Gemini classify error: {e}")
        return fallback

# ─── Fallback functions ───────────────────────────────────────
def _fallback_severity(text: str) -> str:
    lower = text.lower()
    if any(k in lower for k in CRISIS_KEYWORDS):   return "crisis"
    if any(k in lower for k in SEVERE_KEYWORDS):   return "severe"
    if any(k in lower for k in MODERATE_KEYWORDS): return "moderate"
    return "mild"

def _fallback_emotion(text: str) -> str:
    lower = text.lower()
    if any(w in lower for w in ["anxi","panic","scared","fear","worry","nervous"]): return "anxious"
    if any(w in lower for w in ["sad","cry","depress","hopeless","down","miserable"]): return "sad"
    if any(w in lower for w in ["angry","rage","frustrated","mad","irritated"]): return "angry"
    if any(w in lower for w in ["stress","overwhelm","pressure","exhaust","burnout"]): return "stressed"
    if any(w in lower for w in ["lonely","alone","isolat","nobody","no one","abandoned"]): return "lonely"
    if any(w in lower for w in ["happy","good","better","great","thank","okay","fine"]): return "positive"
    return "neutral"

# ─── PUBLIC: detect_severity ──────────────────────────────────
def detect_severity(text: str) -> str:
    # Layer 1: Crisis always instant
    if any(k in text.lower() for k in CRISIS_KEYWORDS):
        return "crisis"
    # Layer 2: Gemini LLM
    return _gemini_classify(
        SEVERITY_PROMPT.format(text=text),
        ["mild", "moderate", "severe", "crisis"],
        _fallback_severity(text)
    )

# ─── PUBLIC: detect_emotion ───────────────────────────────────
def detect_emotion(text: str) -> str:
    # Layer 1: NRCLex pretrained model
    if NRCLEX_AVAILABLE:
        try:
            analysis = NRCLex(text)
            scores   = analysis.top_emotions
            if scores:
                top    = scores[0][0]
                mapped = NRC_LABEL_MAP.get(top, "neutral")
                print(f"[ai_engine] NRCLex: {top} → {mapped}")
                return mapped
        except Exception as e:
            print(f"[ai_engine] NRCLex error: {e}")
    # Layer 2: Gemini fallback
    return _gemini_classify(
        EMOTION_PROMPT.format(text=text),
        ["anxious","sad","angry","stressed","lonely","positive","neutral"],
        _fallback_emotion(text)
    )

# ─── Display helpers ──────────────────────────────────────────
EMOTION_EMOJIS  = {"anxious":"😰","sad":"😢","angry":"😤","stressed":"😩","lonely":"🫂","positive":"😊","neutral":"💭"}
EMOTION_COLORS  = {"anxious":"#a29bfe","sad":"#74b9ff","angry":"#ff7675","stressed":"#fd79a8","lonely":"#6c5ce7","positive":"#00b894","neutral":"#636e72"}
SEVERITY_COLORS = {"mild":"#2ed573","moderate":"#ffa502","severe":"#ff6b35","crisis":"#ff4757"}
SEVERITY_EMOJIS = {"mild":"☀️","moderate":"🌱","severe":"💙","crisis":"🆘"}

def get_engine_status():
    return {
        "transformers": NRCLEX_AVAILABLE,
        "groq":         llm_client is not None,
    }
