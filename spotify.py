# ============================================================
# spotify.py — MindBridge Spotify Integration
#
# METHOD : Embed Spotify playlists based on detected emotion
# ACCESS : Free — no login, no Premium needed
# HOW    : Curated playlist IDs mapped to each emotion
#          Rendered as iframe embed in Streamlit
# ============================================================

# ─── Curated Playlist Map ────────────────────────────────────
# Each emotion has 3 playlists (rotated randomly for variety)
# Playlist IDs from Spotify's public mental health/mood playlists

EMOTION_PLAYLISTS = {
    "anxious": {
        "label":       "Calm Your Mind 🌊",
        "description": "Soft, slow music to quiet an anxious mind",
        "color":       "#a29bfe",
        "playlists": [
            "37i9dQZF1DWZqd5JICZI0u",   # Peaceful Piano
            "37i9dQZF1DX3Ogo9pFvBkY",   # Anxiety Relief
            "37i9dQZF1DWXe9gFZP0gtP",   # Deep Focus
        ]
    },
    "sad": {
        "label":       "Healing Space 💙",
        "description": "Gentle music to sit with your feelings",
        "color":       "#74b9ff",
        "playlists": [
            "37i9dQZF1DX7gIoKXt0gmx",   # Sad Songs
            "37i9dQZF1DWVrtsSlLKzro",   # Sad Indie
            "37i9dQZF1DX3YSRoSdA634",   # Life Sucks
        ]
    },
    "angry": {
        "label":       "Release & Reset 🔥",
        "description": "Let it out, then find your calm",
        "color":       "#ff7675",
        "playlists": [
            "37i9dQZF1DWWjGdmHm4h6S",   # Anger Management
            "37i9dQZF1DX1s9knjAsLLq",   # All Out 2000s (energy release)
            "37i9dQZF1DX4dyzvuaRJ0n",   # mint (upbeat reset)
        ]
    },
    "stressed": {
        "label":       "Unwind & Breathe 🌿",
        "description": "Decompress and let the tension melt away",
        "color":       "#fd79a8",
        "playlists": [
            "37i9dQZF1DWXe9gFZP0gtP",   # Deep Focus
            "37i9dQZF1DWZqd5JICZI0u",   # Peaceful Piano
            "37i9dQZF1DX4sWSpwq3LiO",   # Sleep
        ]
    },
    "lonely": {
        "label":       "You're Not Alone 🫂",
        "description": "Warm music that feels like company",
        "color":       "#6c5ce7",
        "playlists": [
            "37i9dQZF1DX4E3UdUs7fUx",   # Feeling Good
            "37i9dQZF1DX7gIoKXt0gmx",   # Sad Songs
            "37i9dQZF1DWVrtsSlLKzro",   # Warm Acoustic
        ]
    },
    "positive": {
        "label":       "Keep That Energy ⚡",
        "description": "Ride the good vibes even higher",
        "color":       "#00b894",
        "playlists": [
            "37i9dQZF1DX3rxVfibe1L0",   # Mood Booster
            "37i9dQZF1DX4E3UdUs7fUx",   # Feeling Good
            "37i9dQZF1DXdPec7aLItpV",   # Happy Hits
        ]
    },
    "neutral": {
        "label":       "Background Calm 🎵",
        "description": "Easy listening while you reflect",
        "color":       "#636e72",
        "playlists": [
            "37i9dQZF1DWZqd5JICZI0u",   # Peaceful Piano
            "37i9dQZF1DXe9gFZP0gtP",    # Deep Focus
            "37i9dQZF1DX4sWSpwq3LiO",   # Sleep
        ]
    },
}

# ─── Helper: Get playlist ID ──────────────────────────────────
import random

def get_playlist_id(emotion: str, index: int = None) -> str:
    """
    Returns a Spotify playlist ID for the given emotion.
    index: 0-2 to pick specific playlist, None for random
    """
    data = EMOTION_PLAYLISTS.get(emotion, EMOTION_PLAYLISTS["neutral"])
    playlists = data["playlists"]
    if index is not None:
        return playlists[index % len(playlists)]
    return random.choice(playlists)


def get_playlist_info(emotion: str) -> dict:
    """Returns full playlist info dict for the emotion."""
    return EMOTION_PLAYLISTS.get(emotion, EMOTION_PLAYLISTS["neutral"])


# ─── Spotify Embed HTML ───────────────────────────────────────
def get_spotify_embed(playlist_id: str, compact: bool = False) -> str:
    """
    Returns Spotify iframe embed HTML.
    compact=True → smaller player (80px height)
    compact=False → full player (352px height)
    """
    height = "80" if compact else "352"
    return f"""
    <iframe
        src="https://open.spotify.com/embed/playlist/{playlist_id}?utm_source=generator&theme=0"
        width="100%"
        height="{height}"
        frameBorder="0"
        allowfullscreen=""
        allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
        loading="lazy"
        style="border-radius: 14px;">
    </iframe>
    """


# ─── Full Music Card (shown in chat after bot reply) ──────────
def get_music_card_html(emotion: str, playlist_id: str) -> str:
    """
    Returns a styled music card HTML with Spotify embed.
    Shown below the bot's response in chat.
    """
    info  = get_playlist_info(emotion)
    color = info["color"]
    embed = get_spotify_embed(playlist_id, compact=False)

    return f"""
    <div style="
        background: {color}12;
        border: 1px solid {color}35;
        border-radius: 16px;
        padding: 16px 18px;
        margin: 10px 0;
        max-width: 76%;
    ">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
            <div style="
                width:36px;height:36px;border-radius:50%;
                background:{color}25;border:2px solid {color};
                display:flex;align-items:center;justify-content:center;
                font-size:1.1rem;">🎵</div>
            <div>
                <div style="font-weight:600;font-size:0.9rem;color:{color};">
                    {info['label']}
                </div>
                <div style="font-size:0.75rem;color:#707080;">
                    {info['description']}
                </div>
            </div>
            <div style="margin-left:auto;">
                <div style="
                    background:#1DB954;color:#000;
                    font-size:0.65rem;font-weight:700;
                    padding:3px 8px;border-radius:8px;
                    letter-spacing:0.05em;">
                    SPOTIFY
                </div>
            </div>
        </div>
        {embed}
    </div>
    """


# ─── Compact Mini Player (shown in sidebar) ───────────────────
def get_mini_player_html(emotion: str, playlist_id: str) -> str:
    """Small player for sidebar."""
    info  = get_playlist_info(emotion)
    color = info["color"]
    embed = get_spotify_embed(playlist_id, compact=True)
    return f"""
    <div style="margin:8px 0;">
        <div style="font-size:0.75rem;color:{color};font-weight:600;margin-bottom:6px;">
            🎵 {info['label']}
        </div>
        {embed}
    </div>
    """
