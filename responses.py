# ============================================================
# responses.py — MindBridge Response Generator (Gemini Version)
#
# LLM: Google Gemini 1.5 Flash (free, fast, no credit card)
# ============================================================

import os
import random


# ─── Gemini Setup ─────────────────────────────────────────────
try:
    import google.generativeai as genai
    GEMINI_API_KEY = "AIzaSyAi869jnfbTL-AeYicfaPRb04cYFoS0HqE"   # ← paste AIza... key here
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-2.0-flash")
    print("[responses] ✅ Gemini connected")
except Exception as e:
    gemini_model = None
    print(f"[responses] ⚠️ Gemini error: {e}")

# ─── Coping techniques pool ───────────────────────────────────
COPING_POOL = {
    "anxious": [
        "Try box breathing: inhale 4s, hold 4s, exhale 4s, hold 4s.",
        "Name 5 things you can see right now. Ground yourself in the present.",
        "Put cold water on your wrists. It activates your body's calming reflex.",
        "Tense your fists as hard as you can for 5 seconds, then release fully.",
        "Breathe in through your nose for 4 counts, out through mouth for 8 counts.",
        "Focus on one object near you. Describe it in your mind in detail.",
    ],
    "sad": [
        "It's okay to sit with this feeling without trying to fix it right now.",
        "Write down exactly how you feel — just 3 sentences. No editing.",
        "Put on one song that feels like it understands you.",
        "Step outside for 5 minutes, even just to feel the air.",
        "Text one person just to say you're thinking of them.",
        "Wrap yourself in something warm — a blanket, a hoodie.",
    ],
    "angry": [
        "Splash cold water on your face right now. Reset your nervous system.",
        "Write what made you angry — tear the paper after. Physical release.",
        "Walk fast for 5 minutes. Let your body process the adrenaline.",
        "Say out loud: 'I'm allowed to be angry. I'll decide what to do next.'",
        "Count backwards from 20 slowly. Each number, breathe out.",
        "Clench your jaw, hold 5 seconds, release. Repeat 3 times.",
    ],
    "stressed": [
        "Pick ONE task. Just one. Everything else can wait.",
        "Set a 10-minute timer and do nothing but breathe.",
        "Write down everything in your head — a full brain dump, no structure.",
        "Close your eyes and imagine a place that feels completely safe.",
        "Drink a full glass of water slowly. Dehydration worsens stress.",
        "Do 5 slow shoulder rolls. Your body holds stress in your shoulders.",
    ],
    "lonely": [
        "You don't have to solve loneliness right now. Just notice it without judgment.",
        "Send one message to someone you haven't talked to in a while.",
        "Write down 3 moments when you felt genuinely connected to someone.",
        "Go somewhere with people around, even if you don't interact.",
        "Create something small — draw, cook, write — for yourself.",
        "Remember: loneliness is temporary. Connection is always possible.",
    ],
    "neutral": [
        "What's one thing you could do today that would make tomorrow easier?",
        "Take 3 deep, slow breaths before continuing your day.",
        "Think of one thing — however small — that you're grateful for right now.",
    ],
    "positive": [
        "Hold onto this feeling. What made today feel this way?",
        "Tell someone what you're grateful for. Share the good energy.",
        "Write it down — future you will want to remember this moment.",
    ],
}

OPENINGS = {
    "anxious":  ["Anxiety can make everything feel urgent at once —","That tight, unsettled feeling is real —","When the mind races like this,","Feeling anxious is exhausting, especially when you can't pinpoint why."],
    "sad":      ["Sadness like this deserves space, not solutions.","What you're carrying sounds really heavy.","Sometimes there are no words — just this feeling.","That kind of sadness can feel so isolating."],
    "angry":    ["That frustration is completely valid.","Anger usually means something important was crossed.","It makes sense you're feeling this way.","Sometimes anger is just pain that has nowhere else to go."],
    "stressed": ["Being pulled in every direction like this is exhausting.","That level of overwhelm is hard to carry.","When everything piles up at once,","Stress like this can make even small things feel impossible."],
    "lonely":   ["Feeling invisible like that is one of the hardest things.","Loneliness can sit so quietly but weigh so much.","Not feeling understood is genuinely painful.","That sense of disconnection is real and it matters."],
    "positive": ["It's good to hear things feel a bit lighter.","That sounds like a real shift.","Moments like this are worth noticing.","Hold onto that feeling —"],
    "neutral":  ["I'm here and listening.","Tell me more — I want to understand.","What's been going on for you?","Sometimes it's hard to find the words."],
}

FOLLOWUPS = {
    "anxious":  ["What's the one thing making you most anxious right now?","Has anything helped with this kind of anxiety before?","When did this feeling start — was there a moment?","Is this anxiety about something specific or more general?"],
    "sad":      ["How long have you been feeling this way?","Is there something specific that triggered this, or has it been building?","What does this sadness feel like in your body?","Is there anyone around you who knows you're feeling this?"],
    "angry":    ["What happened — can you tell me more?","Has this been building for a while or did something specific set it off?","What do you need right now — to vent, or to problem-solve?","Who or what is at the centre of this frustration?"],
    "stressed": ["What feels most urgent to you right now?","How long have you been running at this pace?","Is there one thing on your list you could let go of, even temporarily?","What would 'less stressed' actually look like for you?"],
    "lonely":   ["What does connection look like for you when things are good?","Is this loneliness around specific people, or more general?","Has anything changed recently that made this feeling stronger?","Who in your life do you feel most yourself around?"],
    "positive": ["What's been making things feel better?","Is this a recent shift or has it been building?","What would help keep this momentum going?"],
    "neutral":  ["What's been on your mind the most lately?","Is there something specific you wanted to talk about today?","What would feel most helpful right now — to vent, or to think things through?","How have you been feeling overall this week?"],
}

# ─── Build system prompt ──────────────────────────────────────
def _build_prompt(conversation_history: list, severity: str,
                  emotion: str, last_bot_reply: str, message_count: int) -> str:

    tip      = random.choice(COPING_POOL.get(emotion, COPING_POOL["neutral"]))
    followup = random.choice(FOLLOWUPS.get(emotion, FOLLOWUPS["neutral"]))
    opening  = random.choice(OPENINGS.get(emotion, OPENINGS["neutral"]))

    severity_instructions = {
        "mild":     "Tone: Warm, curious. Action: Open the conversation, invite them to share more. No coping tips yet.",
        "moderate": f"Tone: Validating and grounding. Action: Acknowledge their feeling + include this coping tip naturally: '{tip}'",
        "severe":   f"Tone: Deep empathy, gentle. Action: Validate + suggest iCall (9152987821) naturally as a free option. Include tip: '{tip}'",
        "crisis":   "Tone: Immediate, warm, safety-focused. Action: Express you care + provide helplines: iCall 9152987821, Vandrevala 1860-2662-345, AASRA 9820466627. Keep SHORT.",
    }

    # Build conversation string
    conv = ""
    trimmed = conversation_history[-6:]
    for msg in trimmed:
        role = "User" if msg["role"] == "user" else "MindBridge"
        conv += f"{role}: {msg['content']}\n"

    prompt = f"""You are MindBridge — a warm, empathetic mental health first-aid AI for Indian users.

STRICT RULES:
1. NEVER diagnose, prescribe, or replace a therapist
2. NEVER repeat yourself — every response must be DIFFERENT
3. NEVER use: "I hear you", "That sounds hard", "Thank you for sharing", "I'm here for you"
4. ALWAYS respond to what the user ACTUALLY said
5. Keep response under 90 words
6. End with this question: "{followup}"

THIS MESSAGE:
- Emotion: {emotion}
- Severity: {severity}
- Suggested opening: "{opening}"
- {severity_instructions.get(severity, "")}

WHAT YOU SAID LAST (DO NOT REPEAT):
{last_bot_reply if last_bot_reply else "This is the first message."}

CONVERSATION:
{conv}
MindBridge:"""

    return prompt

# ─── Get last bot reply ───────────────────────────────────────
def _get_last_bot_reply(history: list) -> str:
    for msg in reversed(history):
        if msg["role"] == "assistant":
            return msg["content"][:300]
    return ""

# ─── MAIN: generate_response ─────────────────────────────────
def generate_response(conversation_history: list,
                      severity: str,
                      emotion: str = "neutral") -> str:

    last_reply    = _get_last_bot_reply(conversation_history)
    message_count = len([m for m in conversation_history if m["role"] == "user"])
    prompt        = _build_prompt(conversation_history, severity, emotion,
                                  last_reply, message_count)

    if not gemini_model:
        return _smart_fallback(conversation_history, severity, emotion)

    try:
        response = gemini_model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.9,
                max_output_tokens=200,
                top_p=0.95,
            )
        )
        reply = response.text.strip()

        # Safety check — if same as last reply, regenerate
        if last_reply and reply[:60] == last_reply[:60]:
            response = gemini_model.generate_content(
                prompt + "\n\nIMPORTANT: Your last response was too similar. Write something completely different.",
                generation_config=genai.types.GenerationConfig(temperature=0.95, max_output_tokens=200)
            )
            reply = response.text.strip()

        return reply

    except Exception as e:
        print(f"[responses] Gemini error: {e}")
        return _smart_fallback(conversation_history, severity, emotion)

# ─── Smart fallback ───────────────────────────────────────────
def _smart_fallback(history: list, severity: str, emotion: str) -> str:
    opening  = random.choice(OPENINGS.get(emotion, OPENINGS["neutral"]))
    tip      = random.choice(COPING_POOL.get(emotion, COPING_POOL["neutral"]))
    followup = random.choice(FOLLOWUPS.get(emotion, FOLLOWUPS["neutral"]))

    if severity == "crisis":
        return f"""{opening}\n\nYou are not alone. Please reach out right now:\n📞 iCall: 9152987821 (free)\n📞 Vandrevala: 1860-2662-345 (24/7)\n📞 AASRA: 9820466627\n\nThese are real people trained to help. Please call. 💙"""
    elif severity == "severe":
        return f"{opening}\n\n{tip}\n\niCall (9152987821) has people trained for exactly this — free and confidential.\n\n{followup}"
    elif severity == "moderate":
        return f"{opening}\n\n{tip}\n\n{followup}"
    else:
        return f"{opening}\n\n{followup}"

# ─── Static data ─────────────────────────────────────────────
HELPLINES = [
    {"name":"iCall",                "number":"9152987821",    "desc":"Free counseling by TISS. Mon–Sat 8AM–10PM.",   "category":"General",          "color":"#6c63ff"},
    {"name":"Vandrevala Foundation","number":"1860-2662-345", "desc":"Free 24/7 crisis support. Multilingual.",      "category":"24/7 Crisis",      "color":"#ff4757"},
    {"name":"AASRA",                "number":"9820466627",    "desc":"Suicide prevention. 24 hours.",                "category":"Crisis",           "color":"#ff6b35"},
    {"name":"Snehi",                "number":"044-24640050",  "desc":"Emotional support helpline.",                  "category":"Emotional Support","color":"#a29bfe"},
    {"name":"NIMHANS",              "number":"080-46110007",  "desc":"Expert psychiatric guidance.",                 "category":"Expert Care",      "color":"#00b894"},
    {"name":"Tele-MANAS",           "number":"14416",         "desc":"Govt helpline. 20+ languages. Free.",          "category":"Government",       "color":"#ffa502"},
]

COPING_TECHNIQUES = {
    "breathing":    {"name":"Box Breathing",            "steps":"Inhale 4s → Hold 4s → Exhale 4s → Hold 4s.",     "for":"anxiety, panic"},
    "grounding":    {"name":"5-4-3-2-1 Grounding",     "steps":"5 see, 4 touch, 3 hear, 2 smell, 1 taste.",       "for":"overwhelm, dissociation"},
    "muscle_relax": {"name":"Progressive Muscle Relax","steps":"Tense each muscle group 5s, release, head to toe.","for":"stress, tension"},
    "cold_water":   {"name":"Cold Water Technique",    "steps":"Splash cold water on face. Calming reflex.",       "for":"intense distress, anger"},
    "journaling":   {"name":"5-Minute Journaling",     "steps":"Write freely 5 minutes, no editing.",             "for":"stress, confusion, grief"},
}

ETHICAL_BOUNDARIES = [
    "Never diagnoses conditions",
    "Never recommends medications",
    "Never replaces therapy",
    "Always escalates in crisis",
    "Zero data stored",
    "Always identifies as AI",
    "Unique response every message",
    "Forbidden phrase filter active",
    "History trimmed to prevent loops",
    "Safeguarded Gemini system prompt",
]
