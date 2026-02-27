# ============================================================
# app.py — MindBridge v2.0 (Full Feature Update)
#
# NEW FEATURES:
#   ✅ Activities tab (breathing, grounding, mindfulness)
#   ✅ Mood Quiz tab (5-question emotional self-check)
#   ✅ 8-tab structure
#   ✅ Session-based memory with reset
#   ✅ Privacy protection messaging
#   ✅ Interactive breathing timer
# ============================================================

import streamlit as st
from datetime import datetime
import random
import time
from ai_engine import (
    detect_severity, detect_emotion, get_engine_status,
    EMOTION_EMOJIS, EMOTION_COLORS, SEVERITY_COLORS, SEVERITY_EMOJIS
)
from responses import (
    generate_response, HELPLINES,
    ETHICAL_BOUNDARIES, COPING_TECHNIQUES
)
from spotify import (
    get_playlist_id, get_playlist_info,
    get_music_card_html, get_mini_player_html,
    EMOTION_PLAYLISTS
)

# ─── Page Config ─────────────────────────────────────────────
st.set_page_config(
    page_title="MindBridge — Mental Health First-Aid",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Styles ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background:linear-gradient(135deg,#07080f 0%,#0a1020 60%,#07080f 100%); color:#e0ddf0; }

.brand { font-family:'DM Serif Display',serif; font-size:2.2rem;
    background:linear-gradient(135deg,#7c6af7,#a78bfa,#5eead4);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }

.live-dot { display:inline-block; width:7px; height:7px; border-radius:50%;
    background:#2ed573; box-shadow:0 0 8px #2ed573; margin-right:6px; animation:glow 2s infinite; }
@keyframes glow { 0%,100%{opacity:1} 50%{opacity:0.3} }

.bubble-user {
    background:linear-gradient(135deg,#5c54e8,#7c6af7); color:#fff;
    padding:13px 18px; border-radius:20px 20px 4px 20px;
    margin:8px 0 8px auto; max-width:72%;
    font-size:0.9rem; line-height:1.65;
    box-shadow:0 4px 22px rgba(92,84,232,0.35); }
.bubble-bot {
    background:rgba(255,255,255,0.046); border:1px solid rgba(255,255,255,0.09);
    color:#ddd8f0; padding:14px 18px; border-radius:4px 20px 20px 20px;
    margin:8px 0; max-width:76%; font-size:0.9rem; line-height:1.7; }
.sev-badge {
    display:inline-block; padding:2px 10px; border-radius:20px;
    font-size:0.72rem; font-weight:600; margin-bottom:8px; }
.crisis-card {
    background:rgba(255,71,87,0.09); border:1px solid rgba(255,71,87,0.35);
    border-radius:11px; padding:11px 15px; margin:5px 0;
    display:flex; justify-content:space-between; align-items:center; }
.tag {
    display:inline-block; background:rgba(46,213,115,0.1);
    border:1px solid rgba(46,213,115,0.28); color:#2ed573;
    padding:2px 9px; border-radius:8px; font-size:0.7rem; font-weight:600; margin:2px; }
.spotify-tag {
    display:inline-block; background:#1DB95420;
    border:1px solid #1DB95440; color:#1DB954;
    padding:2px 9px; border-radius:8px; font-size:0.7rem; font-weight:600; margin:2px; }
.card {
    background:rgba(255,255,255,0.035); border:1px solid rgba(255,255,255,0.07);
    border-radius:13px; padding:15px 18px; margin-bottom:12px; }
.metric-card {
    background:rgba(255,255,255,0.035); border:1px solid rgba(255,255,255,0.07);
    border-radius:13px; padding:16px; text-align:center; }

.stTextInput>div>div>input {
    background:rgba(255,255,255,0.055)!important; border:1px solid rgba(255,255,255,0.11)!important;
    color:#e0ddf0!important; border-radius:12px!important; font-family:'DM Sans',sans-serif!important; }
.stButton>button {
    background:linear-gradient(135deg,#5c54e8,#7c6af7)!important; color:#fff!important;
    border:none!important; border-radius:12px!important;
    font-family:'DM Sans',sans-serif!important; font-weight:500!important; }
.stButton>button:hover { box-shadow:0 4px 22px rgba(92,84,232,0.45)!important; transform:translateY(-1px)!important; }
div[data-testid="stSidebar"] { background:rgba(7,8,15,0.97)!important; border-right:1px solid rgba(255,255,255,0.055)!important; }
.stTabs [data-baseweb="tab-list"] {
    background:rgba(255,255,255,0.03); border-radius:12px; padding:4px; gap:2px;
    border:1px solid rgba(255,255,255,0.07); flex-wrap:wrap; }
.stTabs [data-baseweb="tab"] { border-radius:10px!important; color:#707080!important; font-size:0.82rem!important; }
.stTabs [aria-selected="true"] { background:rgba(124,106,247,0.2)!important; color:#a78bfa!important; }
</style>

""", unsafe_allow_html=True)

# ─── Session State ────────────────────────────────────────────
defaults = {
    "messages":           [],
    "llm_history":        [],
    "mood_history":       [],
    "music_enabled":      True,
    "current_playlist":   None,
    "current_emotion":    "neutral",
    "quiz_answers":       {},
    "quiz_completed":     False,
    "quiz_result":        None,
    "current_prompt":     None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

eng = get_engine_status()

# ─── SIDEBAR ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 MindBridge")
    st.markdown("<div style='font-size:0.72rem;color:#404050;margin-bottom:4px;'>Mental Health First-Aid · v2.0</div>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown(f"""
    <div class="card">
        <div style="font-size:0.75rem;color:#505060;margin-bottom:8px;font-weight:600;">AI ENGINE</div>
        <div style="font-size:0.8rem;color:#a0a0b0;line-height:2.1;">
            🤗 NRCLex: <strong>{'🟢 Active' if eng['transformers'] else '🔴 Off'}</strong><br>
            ✨ Gemini: <strong>{'🟢 Active' if eng['groq'] else '🔴 No key'}</strong><br>
            🎵 Spotify: <strong style="color:#1DB954;">🟢 Ready</strong><br>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎵 Music Therapy")
    st.session_state.music_enabled = st.toggle("Auto-play music", value=st.session_state.music_enabled)

    if st.session_state.music_enabled and st.session_state.current_playlist:
        st.markdown(get_mini_player_html(st.session_state.current_emotion, st.session_state.current_playlist), unsafe_allow_html=True)
        if st.button("🔀 Shuffle Playlist", use_container_width=True):
            st.session_state.current_playlist = get_playlist_id(st.session_state.current_emotion)
            st.rerun()

    st.markdown("---")

    if st.session_state.mood_history:
        st.markdown("### 📊 Session")
        total  = len(st.session_state.mood_history)
        crisis = sum(1 for m in st.session_state.mood_history if m["severity"]=="crisis")
        c1, c2 = st.columns(2)
        c1.metric("Messages", total)
        c2.metric("🆘 Crisis", crisis)
        if crisis > 0:
            st.error("⚠️ Crisis detected!")
        last  = st.session_state.mood_history[-1]
        color = SEVERITY_COLORS.get(last["severity"], "#2ed573")
        st.markdown(f"""
        <div class="card" style="border-color:{color}30;">
            <div style="font-size:0.72rem;color:#505060;margin-bottom:4px;">Last Detection</div>
            <div style="color:{color};font-weight:600;">{SEVERITY_EMOJIS.get(last['severity'],'☀️')} {last['severity'].upper()}</div>
            <div style="font-size:0.78rem;color:#909098;margin-top:3px;">
                {EMOTION_EMOJIS.get(last['emotion'],'💭')} {last['emotion'].capitalize()} · {last['time']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div class="card" style="border-color:rgba(255,71,87,0.2);">
        <div style="font-size:0.78rem;color:#ff6b81;font-weight:600;margin-bottom:7px;">🆘 In Crisis?</div>
        <div style="font-size:0.78rem;color:#909098;line-height:2.1;">
            iCall: <strong style="color:#ccc">9152987821</strong><br>
            Vandrevala: <strong style="color:#ccc">1860-2662-345</strong><br>
            AASRA: <strong style="color:#ccc">9820466627</strong>
        </div>
    </div>
    <div style="font-size:0.7rem;color:#303040;text-align:center;padding:6px 0;">
        🔒 Zero data stored · Session only · No PII
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🔄 New Session", use_container_width=True):
        for k in list(defaults.keys()):
            st.session_state[k] = defaults[k]
        st.rerun()

# ─── Header ──────────────────────────────────────────────────
_, hcol, _ = st.columns([1,2,1])
with hcol:
    st.markdown("""
    <div style="text-align:center;padding:20px 0 14px;">
        <div style="font-size:2.6rem;margin-bottom:8px;">🧠</div>
        <div class="brand">MindBridge</div>
        <div style="color:#505068;font-size:0.82rem;margin-top:5px;letter-spacing:0.05em;">
            <span class="live-dot"></span>Mental Health First-Aid · Ethics-First AI · v2.0
        </div>
        <div style="margin-top:10px;">
            <span class="tag">✓ Never Diagnoses</span>
            <span class="tag">✓ Crisis-Safe</span>
            <span class="tag">✓ LLM Safeguarded</span>
            <span class="spotify-tag">🎵 Music Therapy</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ─── TABS ────────────────────────────────────────────────────
tab1, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "💬 Chat",
    "🎵 Music Therapy",
    "📊 Insights",
    "🧘 Activities",
    "🧠 Mood Quiz",
    "📞 Resources",
    "📄 Ethics Doc"
])

# ════════════════════════════════════════════════════════════
# TAB 1 — CHAT
# ════════════════════════════════════════════════════════════
with tab1:
    chat_col, info_col = st.columns([2.2, 1])

    with chat_col:
        if not st.session_state.messages:
            st.markdown("""
            <div class="bubble-bot">
                <strong>👋 Hey, I'm MindBridge.</strong><br><br>
                A safe, judgment-free space — I'm an AI here to listen and support you.<br><br>
                🎵 <strong>Music Therapy:</strong> Each response comes with a Spotify playlist matched to your emotion.<br>
                <em>What's on your mind today?</em>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='color:#3a3850;font-size:0.78rem;margin:14px 0 8px;text-transform:uppercase;letter-spacing:0.08em;'>Try saying...</div>", unsafe_allow_html=True)
            starters = [
                "I've been feeling really anxious lately",
                "I'm completely overwhelmed with everything",
                "I feel totally alone and no one understands",
                "I can't sleep and my mind won't stop racing",
            ]
            c1, c2 = st.columns(2)
            for i, s in enumerate(starters):
                with (c1 if i%2==0 else c2):
                    if st.button(s, key=f"s{i}", use_container_width=True):
                        st.session_state._starter = s
                        st.rerun()

        # Render messages
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                sev     = msg.get("severity", "mild")
                emo     = msg.get("emotion", "neutral")
                color   = SEVERITY_COLORS.get(sev, "#2ed573")
                emoji   = SEVERITY_EMOJIS.get(sev, "🧠")
                e_color = EMOTION_COLORS.get(emo, "#636e72")
                e_emoji = EMOTION_EMOJIS.get(emo, "💭")
                content = msg["content"].replace("\n", "<br>")

                st.markdown(f"""
                <div class="bubble-bot" style="border-color:{color}22;">
                    <span class="sev-badge" style="background:{color}18;color:{color};border:1px solid {color}35;">
                        {emoji} {sev.upper()}
                    </span>
                    <span class="sev-badge" style="background:{e_color}18;color:{e_color};border:1px solid {e_color}35;margin-left:4px;">
                        {e_emoji} {emo}
                    </span><br>
                    {content}
                </div>
                """, unsafe_allow_html=True)

                if st.session_state.music_enabled and sev != "crisis" and "playlist_id" in msg:
                    st.markdown(get_music_card_html(emo, msg["playlist_id"]), unsafe_allow_html=True)

                if sev == "crisis":
                    st.markdown("**🚨 Please reach out right now:**")
                    for h in HELPLINES[:3]:
                        st.markdown(f"""
                        <div class="crisis-card">
                            <div>
                                <div style="font-weight:600;color:#ff6b81;font-size:0.88rem;">{h['name']}</div>
                                <div style="font-size:0.75rem;color:#606070;">{h['desc']}</div>
                            </div>
                            <div style="font-weight:700;color:#ff4757;font-size:0.88rem;margin-left:12px;">📞 {h['number']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                elif sev == "severe":
                    st.info("💙 Free confidential support: **iCall — 9152987821**")

        # Input area
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        default = ""
        if hasattr(st.session_state, "_starter"):
            default = st.session_state._starter
            del st.session_state._starter

        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input(
                "msg", value=default,
                placeholder="Share what's on your mind...",
                label_visibility="collapsed"
            )
            submitted = st.form_submit_button("Send 💬", use_container_width=True)

        if submitted and user_input.strip():
            text = user_input.strip()
            with st.spinner("🧠 Understanding your message..."):
                severity = detect_severity(text)
                emotion  = detect_emotion(text)

            playlist_id = get_playlist_id(emotion) if severity != "crisis" else None
            st.session_state.current_emotion  = emotion
            st.session_state.current_playlist = playlist_id

            st.session_state.messages.append({"role": "user", "content": text})
            st.session_state.llm_history.append({"role": "user", "content": text})
            st.session_state.mood_history.append({
                "time":     datetime.now().strftime("%H:%M"),
                "severity": severity,
                "emotion":  emotion,
            })

            with st.spinner("💙 Crafting a personalised response..."):
                reply = generate_response(st.session_state.llm_history, severity, emotion)

            st.session_state.messages.append({
                "role": "assistant", "content": reply,
                "severity": severity, "emotion": emotion, "playlist_id": playlist_id,
            })
            st.session_state.llm_history.append({"role": "assistant", "content": reply})
            st.rerun()

    with info_col:
        st.markdown("### 🔬 AI Pipeline")
        for layer, desc, color, tag in [
            ("Layer 1", "Crisis Keywords", "#ff4757", "Instant"),
            ("Layer 2", "NRCLex Model",   "#ffa502", "Local"),
            ("Layer 3", "Gemini LLM",     "#7c6af7", "Smart"),
            ("Layer 4", "Rule Fallback",  "#2ed573", "Safe"),
        ]:
            active = ((layer=="Layer 2" and eng["transformers"]) or
                      (layer=="Layer 3" and eng["groq"]) or
                      layer in ["Layer 1","Layer 4"])
            st.markdown(f"""
            <div class="card" style="border-color:{color}25;margin-bottom:7px;opacity:{'1' if active else '0.4'};">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <div style="font-size:0.7rem;color:{color};font-weight:600;">{layer}</div>
                        <div style="font-size:0.82rem;color:#c0c0d0;">{desc}</div>
                    </div>
                    <div style="font-size:0.68rem;background:{color}20;color:{color};
                         padding:2px 7px;border-radius:7px;font-weight:600;">{tag}</div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("### 🎵 Music Status")
        if st.session_state.current_playlist:
            info  = get_playlist_info(st.session_state.current_emotion)
            color = info["color"]
            st.markdown(f"""
            <div class="card" style="border-color:{color}30;">
                <div style="font-size:0.72rem;color:#505060;margin-bottom:4px;">Now Playing For</div>
                <div style="color:{color};font-weight:600;">{EMOTION_EMOJIS.get(st.session_state.current_emotion,'🎵')} {st.session_state.current_emotion.capitalize()}</div>
                <div style="font-size:0.75rem;color:#1DB954;margin-top:4px;">🎵 {info['label']}</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown('<div class="card"><div style="font-size:0.78rem;color:#404050;">Send a message to get your playlist 🎵</div></div>', unsafe_allow_html=True)

        st.markdown("### ✅ Features")
        features = [
            ("Mental health bot", True),
            ("Music therapy", True),     ("Crisis escalation", True),
            ("Activities tab", True),    ("Mood quiz", True),
            ("Ethical AI doc", True),    ("Privacy protected", True),
        ]
        for label, done in features:
            c = "#2ed573" if done else "#505060"
            st.markdown(f"<div style='font-size:0.78rem;color:{c};padding:2px 0;'>{'✅' if done else '⏳'} {label}</div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TAB 3 — MUSIC THERAPY
# ════════════════════════════════════════════════════════════
with tab3:
    st.markdown("## 🎵 Music Therapy")
    st.markdown("<div style='color:#505060;margin-bottom:22px;'>Curated Spotify playlists matched to each emotional state. No login required.</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="card" style="border-left:3px solid #1DB954;margin-bottom:24px;">
        <div style="font-weight:600;color:#1DB954;margin-bottom:8px;">🎵 How Music Therapy Works</div>
        <div style="font-size:0.85rem;color:#909098;line-height:2.0;">
            1. Share how you're feeling in the 💬 Chat tab<br>
            2. AI detects your emotion (anxious, sad, stressed...)<br>
            3. A curated Spotify playlist appears below your response<br>
            4. Music is matched to your emotional state — not random<br>
            5. Shuffle for a different playlist anytime
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎭 Browse by Emotion")
    emotions = list(EMOTION_PLAYLISTS.keys())
    selected_emotion = st.selectbox(
        "Select emotion",
        emotions,
        format_func=lambda e: f"{EMOTION_EMOJIS.get(e,'💭')} {e.capitalize()} — {EMOTION_PLAYLISTS[e]['label']}",
        label_visibility="collapsed"
    )
    if selected_emotion:
        info  = get_playlist_info(selected_emotion)
        color = info["color"]
        pid   = get_playlist_id(selected_emotion, 0)
        st.markdown(f"""
        <div style="background:{color}10;border:1px solid {color}30;border-radius:16px;padding:18px 20px;margin:12px 0;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
                <div style="width:44px;height:44px;border-radius:50%;background:{color}25;border:2px solid {color};
                     display:flex;align-items:center;justify-content:center;font-size:1.4rem;">
                    {EMOTION_EMOJIS.get(selected_emotion,'💭')}
                </div>
                <div>
                    <div style="font-size:1.1rem;font-weight:600;color:{color};">{info['label']}</div>
                    <div style="font-size:0.82rem;color:#707080;">{info['description']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        from spotify import get_spotify_embed
        st.markdown(get_spotify_embed(pid), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        if st.button("🔀 Shuffle Playlist", key="shuffle_t3"):
            st.rerun()

    st.markdown("### 🌈 All Emotion Playlists")
    cols = st.columns(4)
    for i, (emotion, data) in enumerate(EMOTION_PLAYLISTS.items()):
        with cols[i % 4]:
            color = data["color"]
            emoji = EMOTION_EMOJIS.get(emotion, "💭")
            st.markdown(f"""
            <div class="card" style="border-color:{color}30;text-align:center;padding:14px;">
                <div style="font-size:1.6rem;margin-bottom:6px;">{emoji}</div>
                <div style="font-size:0.82rem;font-weight:600;color:{color};">{emotion.capitalize()}</div>
                <div style="font-size:0.7rem;color:#505060;margin-top:4px;">{data['label']}</div>
            </div>
            """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TAB 4 — INSIGHTS
# ════════════════════════════════════════════════════════════
with tab4:
    st.markdown("## 📊 Your Mood Journey")
    if not st.session_state.mood_history:
        st.markdown("""
        <div style="text-align:center;padding:60px;border:1px dashed rgba(255,255,255,0.08);border-radius:20px;color:#303040;">
            <div style="font-size:3rem;margin-bottom:14px;">💭</div>
            <div>Start chatting to unlock your emotional insights</div>
        </div>""", unsafe_allow_html=True)
    else:
        history = st.session_state.mood_history
        total   = len(history)
        sev_cnt, emo_cnt = {}, {}
        for m in history:
            sev_cnt[m["severity"]] = sev_cnt.get(m["severity"], 0) + 1
            emo_cnt[m["emotion"]]  = emo_cnt.get(m["emotion"], 0) + 1

        c1, c2, c3, c4 = st.columns(4)
        for col, sev, label in zip([c1,c2,c3,c4],
            ["mild","moderate","severe","crisis"],
            ["🟢 Mild","🟡 Moderate","🟠 Severe","🔴 Crisis"]):
            color = SEVERITY_COLORS[sev]
            with col:
                st.markdown(f"""
                <div class="metric-card" style="border-color:{color}28;">
                    <div style="font-size:1.8rem;font-weight:700;color:{color}">{sev_cnt.get(sev,0)}</div>
                    <div style="font-size:0.75rem;color:#505060;margin-top:4px;">{label}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)
        st.markdown("### 🕐 Emotion Timeline")
        tl = "<div style='display:flex;gap:10px;flex-wrap:wrap;padding:8px 0;'>"
        for m in history:
            e     = m["emotion"]
            color = EMOTION_COLORS.get(e, "#636e72")
            tl += f"""<div style="text-align:center;">
                <div style="width:42px;height:42px;border-radius:50%;
                     background:{color}22;border:2px solid {color};
                     display:flex;align-items:center;justify-content:center;
                     font-size:1.15rem;margin-bottom:4px;">{EMOTION_EMOJIS.get(e,'💭')}</div>
                <div style="font-size:0.62rem;color:#404050;">{m['time']}</div>
            </div>"""
        tl += "</div>"
        st.markdown(tl, unsafe_allow_html=True)

        st.markdown("### 🎭 Emotion Breakdown")
        for emo, cnt in sorted(emo_cnt.items(), key=lambda x: -x[1]):
            color = EMOTION_COLORS.get(emo, "#636e72")
            pct   = int((cnt / total) * 100)
            st.markdown(f"""
            <div style="margin-bottom:14px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:5px;font-size:0.85rem;">
                    <span>{EMOTION_EMOJIS.get(emo,'💭')} {emo.capitalize()}</span>
                    <span style="color:{color};">{cnt}x ({pct}%)</span>
                </div>
                <div style="height:7px;background:rgba(255,255,255,0.055);border-radius:4px;">
                    <div style="height:100%;width:{pct}%;background:{color};border-radius:4px;box-shadow:0 0 8px {color}55;"></div>
                </div>
            </div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TAB 5 — ACTIVITIES
# ════════════════════════════════════════════════════════════
with tab5:
    st.markdown("## 🧘 Grounding Activities")
    st.markdown("<div style='color:#505060;margin-bottom:22px;'>Interactive exercises to regulate emotions — no app needed.</div>", unsafe_allow_html=True)

    act_tab1, act_tab2, act_tab3, act_tab4 = st.tabs(["🌬️ Breathing", "🌍 Grounding", "💪 Quick Relief", "🧘 Mindfulness"])

    with act_tab1:
        st.markdown("### 🌬️ Breathing Exercises")
        breathing_exercises = [
            {
                "name": "Box Breathing (4-4-4-4)", "emoji": "🟦", "for": "Anxiety, panic attacks",
                "color": "#a29bfe", "duration": "3–5 minutes",
                "steps": ["Inhale through nose for **4 seconds**", "Hold your breath for **4 seconds**", "Exhale slowly for **4 seconds**", "Hold empty for **4 seconds**", "Repeat 4–6 times"],
                "science": "Activates the parasympathetic nervous system, reducing cortisol.",
            },
            {
                "name": "4-7-8 Breathing", "emoji": "🌙", "for": "Stress, insomnia, anxiety",
                "color": "#74b9ff", "duration": "2–4 minutes",
                "steps": ["Inhale quietly through nose for **4 seconds**", "Hold breath for **7 seconds**", "Exhale completely through mouth for **8 seconds**", "Repeat 3–4 cycles"],
                "science": "Developed by Dr. Andrew Weil. Acts as a natural tranquilizer for the nervous system.",
            },
            {
                "name": "Diaphragmatic Breathing", "emoji": "🫁", "for": "Stress, overwhelm",
                "color": "#55efc4", "duration": "5 minutes",
                "steps": ["Place one hand on chest, one on belly", "Breathe so only your belly rises (not chest)", "Inhale for **4 counts**", "Exhale for **6 counts**", "Feel your belly fall completely"],
                "science": "Strengthens the diaphragm and improves oxygen exchange efficiency.",
            },
        ]
        for ex in breathing_exercises:
            color = ex["color"]
            with st.expander(f"{ex['emoji']} **{ex['name']}** — *{ex['for']}*"):
                c1, c2 = st.columns([2,1])
                with c1:
                    st.markdown(f"<div style='font-size:0.82rem;color:#909098;margin-bottom:10px;'>⏱️ {ex['duration']}</div>", unsafe_allow_html=True)
                    for i, step in enumerate(ex["steps"], 1):
                        st.markdown(f"<div style='font-size:0.85rem;color:#c0c0d0;padding:4px 0;'><span style='color:{color};font-weight:600;'>{i}.</span> {step}</div>", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                    <div style="background:{color}12;border:1px solid {color}30;border-radius:12px;padding:14px;text-align:center;">
                        <div style="font-size:2.5rem;margin-bottom:8px;">{ex['emoji']}</div>
                        <div style="font-size:0.7rem;color:#707080;line-height:1.6;">🔬 {ex['science']}</div>
                    </div>""", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### ⏱️ Interactive Box Breathing Timer")
        if st.button("▶️ Start 3-Cycle Box Breathing", use_container_width=False):
            phases = [("🌬️ Inhale", 4, "#a29bfe"), ("⏸️ Hold", 4, "#ffa502"), ("💨 Exhale", 4, "#2ed573"), ("⏸️ Hold", 4, "#ffa502")]
            placeholder = st.empty()
            for cycle in range(3):
                for phase, duration, pcolor in phases:
                    for t in range(duration, 0, -1):
                        placeholder.markdown(f"""
                        <div style="text-align:center;padding:30px;background:{pcolor}12;
                             border:2px solid {pcolor}40;border-radius:20px;margin:10px 0;">
                            <div style="font-size:2.5rem;margin-bottom:8px;">{phase}</div>
                            <div style="font-size:4rem;font-weight:700;color:{pcolor};">{t}</div>
                            <div style="font-size:0.8rem;color:#707080;margin-top:8px;">Cycle {cycle+1} of 3</div>
                        </div>""", unsafe_allow_html=True)
                        time.sleep(1)
            placeholder.success("✅ Great job! 3 cycles of box breathing complete.")

    with act_tab2:
        st.markdown("### 🌍 Grounding Techniques")
        st.markdown("""
        <div class="card" style="border-left:3px solid #5eead4;">
            <div style="font-weight:600;color:#5eead4;margin-bottom:12px;">🌿 5-4-3-2-1 Grounding</div>
            <div style="font-size:0.85rem;color:#909098;line-height:2.0;">
                Uses your 5 senses to anchor you in the present moment.
                Especially powerful during panic attacks or dissociation.
            </div>
        </div>""", unsafe_allow_html=True)
        senses = [
            ("👁️ 5 things you can SEE",  "#a29bfe", "Look around slowly. Name them out loud or in your mind."),
            ("✋ 4 things you can TOUCH", "#74b9ff", "Feel the texture. Is it rough, smooth, warm, cold?"),
            ("👂 3 things you can HEAR",  "#55efc4", "Listen beyond the obvious. Background sounds count."),
            ("👃 2 things you can SMELL", "#fd79a8", "If nothing obvious, remember a comforting smell."),
            ("👅 1 thing you can TASTE",  "#ffa502", "Notice the taste in your mouth right now."),
        ]
        for sense, color, tip in senses:
            st.markdown(f"""
            <div class="card" style="border-color:{color}30;margin-bottom:8px;">
                <div style="font-size:0.95rem;font-weight:600;color:{color};margin-bottom:4px;">{sense}</div>
                <div style="font-size:0.8rem;color:#707080;">{tip}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div class="card" style="border-left:3px solid #6c5ce7;margin-top:16px;">
            <div style="font-weight:600;color:#6c5ce7;margin-bottom:12px;">🧊 Cold Water Reset</div>
            <div style="font-size:0.85rem;color:#909098;line-height:2.0;">
                1. Go to the nearest sink<br>
                2. Splash <strong>cold water</strong> on your face and wrists<br>
                3. Activates the mammalian dive reflex — slows heart rate within seconds<br>
                4. Best for: intense distress, anger, panic
            </div>
        </div>""", unsafe_allow_html=True)

    with act_tab3:
        st.markdown("### 💪 Quick Stress Relief (2–5 Minutes)")
        quick_reliefs = [
            ("🏃 Walk Fast for 5 Min",      "Physical movement burns off stress hormones. Even your room works.",             "#ff6b35"),
            ("✍️ Brain Dump Journal",        "Set a 5-min timer. Write EVERYTHING with no editing, no judgment.",             "#a29bfe"),
            ("💪 Muscle Relaxation",         "Tense each muscle 5 seconds, release. Feet → face. Full body.",                "#74b9ff"),
            ("🚿 Temperature Contrast",      "Alternate warm/cool water in the shower. Resets the nervous system.",          "#55efc4"),
            ("🎵 One Song Break",            "Play the song that always moves you. Full attention, no distractions.",        "#1DB954"),
            ("📵 10-Min Phone Detox",        "Phone face-down. Sit with yourself. Notice thoughts without social media.",    "#fd79a8"),
        ]
        c1, c2 = st.columns(2)
        for i, (title, desc, color) in enumerate(quick_reliefs):
            with (c1 if i%2==0 else c2):
                st.markdown(f"""
                <div class="card" style="border-color:{color}30;margin-bottom:10px;">
                    <div style="font-weight:600;color:{color};font-size:0.92rem;margin-bottom:6px;">{title}</div>
                    <div style="font-size:0.8rem;color:#909098;line-height:1.6;">{desc}</div>
                </div>""", unsafe_allow_html=True)

    with act_tab4:
        st.markdown("### 🧘 Mindfulness & Reflection")
        st.markdown("""
        <div class="card" style="border-left:3px solid #a29bfe;">
            <div style="font-weight:600;color:#a29bfe;margin-bottom:10px;">🌸 Body Scan Meditation</div>
            <div style="font-size:0.85rem;color:#909098;line-height:2.2;">
                Close your eyes. Take 3 deep breaths.<br>
                Scan slowly from the top of your head downward.<br>
                Notice any tension without judgment. Breathe into each area.<br>
                Head → neck → shoulders → chest → belly → legs → feet.<br>
                Total time: 5–10 minutes.
            </div>
        </div>""", unsafe_allow_html=True)

        reflection_prompts = [
            "What is one thing — however small — you're grateful for right now?",
            "Describe your current physical environment using only positive words.",
            "What would you tell your past self from exactly 1 year ago?",
            "Name three people who have positively impacted your life, and how.",
            "What's one small thing you could do today to make tomorrow easier?",
            "If your current emotion was a weather pattern, what would it look like?",
            "What does 'feeling okay' specifically look like for you?",
            "What is one boundary you need to set that would reduce your stress?",
        ]

        st.markdown("### 💭 Reflection Prompts")
        st.markdown("<div style='color:#505060;font-size:0.85rem;margin-bottom:14px;'>Journal for 5 minutes — no editing, no judgment.</div>", unsafe_allow_html=True)

        if not st.session_state.current_prompt:
            st.session_state.current_prompt = random.choice(reflection_prompts)

        st.markdown(f"""
        <div class="card" style="border-color:rgba(162,155,254,0.4);background:rgba(162,155,254,0.06);text-align:center;padding:24px;">
            <div style="font-size:1.05rem;color:#c0b8f0;line-height:1.8;font-style:italic;">
                "{st.session_state.current_prompt}"
            </div>
        </div>""", unsafe_allow_html=True)

        if st.button("🔄 New Prompt", key="new_prompt"):
            st.session_state.current_prompt = random.choice(reflection_prompts)
            st.rerun()

# ════════════════════════════════════════════════════════════
# TAB 6 — MOOD QUIZ
# ════════════════════════════════════════════════════════════
with tab6:
    st.markdown("## 🧠 Mood Check-In Quiz")
    st.markdown("<div style='color:#505060;margin-bottom:22px;'>A 5-question emotional self-assessment. Takes about 2 minutes.</div>", unsafe_allow_html=True)

    QUIZ_QUESTIONS = [
        {
            "id": "q1", "question": "How has your energy been today?", "emoji": "⚡",
            "options": [
                {"text": "High and motivated",           "score": 1, "emotion": "positive"},
                {"text": "Normal, getting through",      "score": 2, "emotion": "neutral"},
                {"text": "Low, dragging myself through", "score": 3, "emotion": "sad"},
                {"text": "Completely drained",           "score": 4, "emotion": "stressed"},
            ]
        },
        {
            "id": "q2", "question": "How well did you sleep last night?", "emoji": "😴",
            "options": [
                {"text": "Really well, feel rested",       "score": 1, "emotion": "positive"},
                {"text": "Okay, a bit tired",              "score": 2, "emotion": "neutral"},
                {"text": "Struggled to fall asleep",       "score": 3, "emotion": "anxious"},
                {"text": "Barely slept, mind was racing",  "score": 4, "emotion": "anxious"},
            ]
        },
        {
            "id": "q3", "question": "How connected do you feel to people around you?", "emoji": "🤝",
            "options": [
                {"text": "Very connected and supported",          "score": 1, "emotion": "positive"},
                {"text": "Somewhat connected",                   "score": 2, "emotion": "neutral"},
                {"text": "A bit isolated",                       "score": 3, "emotion": "lonely"},
                {"text": "Completely alone and misunderstood",   "score": 4, "emotion": "lonely"},
            ]
        },
        {
            "id": "q4", "question": "How are you handling responsibilities right now?", "emoji": "📋",
            "options": [
                {"text": "On top of everything",             "score": 1, "emotion": "positive"},
                {"text": "Managing, with some effort",       "score": 2, "emotion": "neutral"},
                {"text": "Feeling overwhelmed",              "score": 3, "emotion": "stressed"},
                {"text": "Can't cope with anything",         "score": 4, "emotion": "stressed"},
            ]
        },
        {
            "id": "q5", "question": "What best describes your emotional state right now?", "emoji": "💭",
            "options": [
                {"text": "Calm, content, or happy",       "score": 1, "emotion": "positive"},
                {"text": "Neutral — neither good nor bad","score": 2, "emotion": "neutral"},
                {"text": "Anxious, worried, or sad",      "score": 3, "emotion": "anxious"},
                {"text": "Very low, hopeless, or numb",   "score": 4, "emotion": "sad"},
            ]
        },
    ]

    if not st.session_state.quiz_completed:
        answered = len(st.session_state.quiz_answers)
        total_q  = len(QUIZ_QUESTIONS)
        st.progress(answered / total_q, text=f"Progress: {answered}/{total_q} questions answered")

        for q in QUIZ_QUESTIONS:
            qid = q["id"]
            st.markdown(f"""
            <div class="card" style="border-color:rgba(124,106,247,0.25);">
                <div style="font-size:1rem;font-weight:600;color:#c0b8f0;margin-bottom:12px;">
                    {q['emoji']} {q['question']}
                </div>
            </div>""", unsafe_allow_html=True)

            cols = st.columns(2)
            for i, opt in enumerate(q["options"]):
                with cols[i % 2]:
                    selected   = st.session_state.quiz_answers.get(qid) == opt["text"]
                    btn_label  = f"{'✅ ' if selected else ''}{opt['text']}"
                    if st.button(btn_label, key=f"{qid}_{i}", use_container_width=True):
                        st.session_state.quiz_answers[qid]      = opt["text"]
                        st.session_state[f"{qid}_score"]        = opt["score"]
                        st.session_state[f"{qid}_emotion"]      = opt["emotion"]
                        st.rerun()

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if answered == total_q:
            if st.button("🎯 Get My Results", use_container_width=True):
                total_score = sum(st.session_state.get(f"{q['id']}_score", 2) for q in QUIZ_QUESTIONS)
                emotions_chosen = [st.session_state.get(f"{q['id']}_emotion", "neutral") for q in QUIZ_QUESTIONS]
                dominant = max(set(emotions_chosen), key=emotions_chosen.count)
                st.session_state.quiz_result    = {"score": total_score, "dominant_emotion": dominant, "emotions": emotions_chosen}
                st.session_state.quiz_completed = True
                st.rerun()
        else:
            st.info(f"Please answer all {total_q} questions ({total_q - answered} remaining)")

    else:
        result  = st.session_state.quiz_result
        score   = result["score"]
        emotion = result["dominant_emotion"]
        color   = EMOTION_COLORS.get(emotion, "#a29bfe")
        emoji   = EMOTION_EMOJIS.get(emotion, "💭")

        if score <= 7:
            level, lc, le = "You're doing well", "#2ed573", "🌟"
            insight    = "Your responses suggest a relatively stable emotional state. Keep doing what's working."
            suggestion = "Stay connected with people who matter. Celebrate small wins."
            music_emo  = "positive"
        elif score <= 12:
            level, lc, le = "Some challenges present", "#ffa502", "🌱"
            insight    = "You're managing, but carrying some weight. Very normal — life gets heavy."
            suggestion = "Try a breathing exercise from the 🧘 Activities tab. Even 5 minutes shifts your state."
            music_emo  = emotion
        elif score <= 17:
            level, lc, le = "You're struggling", "#ff6b35", "💙"
            insight    = "You're going through a difficult time. You deserve support."
            suggestion = "iCall (9152987821) is free and confidential. They get it."
            music_emo  = "sad"
        else:
            level, lc, le = "Significant distress", "#ff4757", "🆘"
            insight    = "You're carrying a lot right now. Please don't do this alone."
            suggestion = "Please reach out: iCall 9152987821 · Vandrevala 1860-2662-345. You matter."
            music_emo  = "sad"

        st.markdown(f"""
        <div style="text-align:center;padding:30px;background:{lc}0d;
             border:2px solid {lc}35;border-radius:20px;margin-bottom:24px;">
            <div style="font-size:3.5rem;margin-bottom:12px;">{le}</div>
            <div style="font-size:1.4rem;font-weight:700;color:{lc};margin-bottom:8px;">{level}</div>
            <div style="font-size:0.9rem;color:#b0b0c0;max-width:480px;margin:0 auto;line-height:1.7;">{insight}</div>
            <div style="margin-top:16px;">
                <span style="font-size:1.5rem;">{emoji}</span>
                <span style="color:{color};font-weight:600;margin-left:8px;">Primary emotion: {emotion.capitalize()}</span>
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="card" style="border-left:3px solid {lc};">
            <div style="font-weight:600;color:{lc};margin-bottom:8px;">💡 Suggested Next Step</div>
            <div style="font-size:0.88rem;color:#c0c0d0;">{suggestion}</div>
        </div>""", unsafe_allow_html=True)

        if music_emo in EMOTION_PLAYLISTS:
            st.markdown("### 🎵 Recommended Playlist for Your Mood")
            from spotify import get_spotify_embed
            st.markdown(get_spotify_embed(get_playlist_id(music_emo)), unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 Retake Quiz", use_container_width=True):
                st.session_state.quiz_completed = False
                st.session_state.quiz_answers   = {}
                st.session_state.quiz_result    = None
                for q in QUIZ_QUESTIONS:
                    for suffix in ["_score", "_emotion"]:
                        st.session_state.pop(f"{q['id']}{suffix}", None)
                st.rerun()
        with c2:
            if st.button("💬 Talk to MindBridge", use_container_width=True):
                st.info("Switch to the 💬 Chat tab to continue!")

# ════════════════════════════════════════════════════════════
# TAB 7 — RESOURCES
# ════════════════════════════════════════════════════════════
with tab7:
    st.markdown("## 📞 Crisis Escalation & Resources")
    st.markdown("<div style='color:#505060;margin-bottom:22px;'>Deliverable #3 — Auto-triggers on crisis detection.</div>", unsafe_allow_html=True)

    st.markdown("### 🔄 Crisis Escalation Workflow")
    st.markdown("""
    <div class="card" style="border-left:3px solid #ff4757;">
        <div style="font-size:0.85rem;color:#909098;line-height:2.4;">
            <span style="color:#ff4757;font-weight:600;">Step 1</span> → User sends message<br>
            <span style="color:#ff6b35;font-weight:600;">Step 2</span> → 30+ crisis keywords checked instantly<br>
            <span style="color:#ffa502;font-weight:600;">Step 3</span> → NRCLex model detects emotion<br>
            <span style="color:#a78bfa;font-weight:600;">Step 4</span> → Gemini LLM classifies severity<br>
            <span style="color:#5eead4;font-weight:600;">Step 5</span> → If CRISIS: helplines auto-appear, music paused<br>
            <span style="color:#2ed573;font-weight:600;">Step 6</span> → Safeguarded LLM generates unique response
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("### 📞 Verified Indian Helplines")
    for h in HELPLINES:
        st.markdown(f"""
        <div class="card" style="border-color:{h['color']}22;display:flex;justify-content:space-between;align-items:center;">
            <div>
                <div style="display:flex;align-items:center;gap:9px;margin-bottom:4px;">
                    <span style="font-weight:600;font-size:0.92rem;">{h['name']}</span>
                    <span style="font-size:0.7rem;padding:2px 9px;border-radius:9px;
                         background:{h['color']}18;color:{h['color']};font-weight:600;">{h['category']}</span>
                </div>
                <div style="font-size:0.78rem;color:#585865;">{h['desc']}</div>
            </div>
            <div style="font-weight:700;color:{h['color']};padding:9px 14px;border-radius:10px;
                 background:{h['color']}14;margin-left:16px;white-space:nowrap;">📞 {h['number']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("### 🧘 Coping Techniques")
    for k, t in COPING_TECHNIQUES.items():
        with st.expander(f"**{t['name']}** — for *{t['for']}*"):
            st.markdown(f"<div style='color:#a0a0b0;font-size:0.9rem;'>{t['steps']}</div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TAB 8 — ETHICS DOC
# ════════════════════════════════════════════════════════════
with tab8:
    st.markdown("## 📄 Ethical AI Guidelines")
    st.markdown("<div style='color:#505060;margin-bottom:22px;'>Deliverable #4 — Ethics in AI at the core.</div>", unsafe_allow_html=True)

    ethics_sections = [
        {"title":"1. Safety Boundaries","color":"#7c6af7","emoji":"🛡️",
         "points":["NEVER diagnoses conditions","NEVER recommends medications",
                   "NEVER replaces therapy","NEVER provides harmful info",
                   "10-rule safeguarded LLM system prompt"]},
        {"title":"2. Safeguarded LLM","color":"#5eead4","emoji":"🤖",
         "points":["Gemini 1.5 Flash with strict system prompt",
                   "Forbidden phrase filter prevents repetition",
                   "Emotion-aware dynamic response generation",
                   "Fallback rules if LLM unavailable",
                   "Unique response every message guaranteed"]},
        {"title":"3. Crisis Protocol","color":"#ff4757","emoji":"🆘",
         "points":["30+ keywords checked instantly (rule-based)",
                   "Never waits for API — instant safety",
                   "Helplines auto-display — no user action needed",
                   "Music paused automatically during crisis",
                   "Crisis LLM overlay activated"]},
        {"title":"4. Data Privacy","color":"#2ed573","emoji":"🔒",
         "points":["Zero data stored to database",
                   "Session only — clears on browser close",
                   "No PII collected","No third-party sharing",
                   "Full reset available anytime"]},
        {"title":"6. Music Ethics","color":"#1DB954","emoji":"🎵",
         "points":["Spotify not shown during crisis",
                   "Music is supplementary — not primary treatment",
                   "No auto-play — user controls playback",
                   "Playlists curated by mental health context",
                   "Clearly labelled as music therapy, not medicine"]},
    ]

    for s in ethics_sections:
        st.markdown(f"""
        <div class="card" style="border-left:3px solid {s['color']};">
            <div style="font-weight:600;font-size:0.95rem;color:{s['color']};margin-bottom:11px;">{s['emoji']} {s['title']}</div>
            {"".join(f'<div style="font-size:0.82rem;color:#909098;padding:3px 0;">✓ {p}</div>' for p in s['points'])}
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div class="card" style="border-color:rgba(124,106,247,0.25);background:rgba(124,106,247,0.06);">
        <strong style="color:#a78bfa;">📋 Compliance Statement</strong><br><br>
        <div style="font-size:0.82rem;color:#909098;line-height:1.8;">
        MindBridge v2.0 combines AI conversation, music therapy,
        grounding activities, and mood assessment. All outputs are safeguarded.
        Music is supplementary and never shown during crisis.
        <br><br><strong style="color:#a78bfa;">HackWithAI #27 · Healthcare · Ethics in AI</strong>
        </div>
    </div>""", unsafe_allow_html=True)
