# app.py
# Pirate – Samurai – Cowboy Personality Test (Streamlit)
# Fixes:
# 1) Radios start with no selection; Next is disabled until chosen
# 2) Title shows all three emojis (🏴‍☠️🥋🤠)
# 3) Image share fixes: no deprecation warning, better layout, crisp Story Card text

import io
from math import sqrt
import textwrap
import urllib.parse
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib import font_manager
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

st.set_page_config(page_title="Pirate • Samurai • Cowboy Test", page_icon="⚔️", layout="centered")

# -----------------------
# Questionnaire + Weights
# -----------------------
QUESTIONS = [
    {
        "q": "1) What drives you to the gym most days?",
        "options": [
            ("To look good and feel dangerous.",       (2,0,0)),
            ("To master discipline and routine.",      (0,2,0)),
            ("To feel capable and ready for anything.",(0,1,2)),
            ("To decompress and stay centered.",       (0,1,1)),
        ],
    },
    {
        "q": "2) You wake up in a random country with $100 and no phone. What’s your move?",
        "options": [
            ("Find a bar, make friends, figure it out as you go.", (2,0,1)),
            ("Plan three steps ahead, find work, rebuild fast.",    (0,2,0)),
            ("Explore quietly, find shelter, adapt.",               (0,0,2)),
            ("Treat it like a test—see how long you last alone.",   (1,1,1)),
        ],
    },
    {
        "q": "3) Drug of choice (philosophically speaking).",
        "options": [
            ("Nicotine/alcohol — keeps the engine humming.", (2,0,1)),
            ("Psychedelics — open doors that fear keeps shut.", (0,2,0)),
            ("Weed — slow down, breathe, exist.", (0,0,2)),
            ("None — my mind’s already the trip.", (1,2,1)),
        ],
    },
    {
        "q": "4) You’re on a road trip. The vibe in the car should be:",
        "options": [
            ("Loud, unpredictable, stories for days.", (2,0,0)),
            ("Focused, organized, with a purpose.",   (0,2,0)),
            ("Chill, steady, good company and scenery.", (0,0,2)),
            ("Deep talks and quiet moments between chaos.", (1,1,1)),
        ],
    },
    {
        "q": "5) Which description of a hookup sounds the most like you?",
        "options": [
            ("The energy is chaotic, but everyone’s smiling after.", (2,0,0)),
            ("It’s slow, intentional, and hits like poetry.",        (0,2,0)),
            ("Easy connection, laughter, no rush.",                  (0,0,2)),
            ("Mutual respect and no weird morning energy.",          (1,1,1)),
        ],
    },
    {
        "q": "6) If someone bumps into you and spills your drink:",
        "options": [
            ("Laugh, clink glasses, turn it into a story.", (2,0,0)),
            ("Lock eyes, assess the intent, stay composed.",(0,2,0)),
            ("Brush it off, life’s too short for drama.",   (0,0,2)),
            ("Offer to replace theirs—accidents happen.",   (0,1,1)),
        ],
    },
    {
        "q": "7) You’re offered a risky adventure with a high reward. What’s your instinct?",
        "options": [
            ("Hell yes, I’ll figure it out on the way.", (2,0,0)),
            ("Only if I can control the outcome.",       (0,2,0)),
            ("Depends who’s going and what’s at stake.", (1,0,2)),
            ("I’d rather build something steady than gamble.", (0,1,2)),
        ],
    },
    {
        "q": "8) You’re mid backshots and she farts. What’s your next move?",
        "options": [
            ("Laugh so hard you almost fall over.",     (2,0,0)),
            ("Keep rhythm — act like nothing happened.",(0,2,0)),
            ("Slow down, check if she’s okay, then resume.", (0,0,2)),
            ("Say “bless you” and carry on like a gentleman.", (1,1,1)),
        ],
    },
    {
        "q": "9) Tits, ass, 50/50, prefer men.",
        "options": [
            ("Tits.",                             (2,0,0)),
            ("Ass.",                              (0,2,0)),
            ("50/50 — I’m fair and balanced.",    (0,1,2)),
            ("Prefer men — the vibes align.",     (1,1,1)),
        ],
    },
    {
        "q": "10) You’re in a gladiator ring. The gate opens. What’s your weapon?",
        "options": [
            ("Dual daggers — fast and unpredictable.", (2,0,0)),
            ("Katana — precision and discipline.",     (0,2,0)),
            ("Axe or hammer — raw power and weight.",  (0,0,2)),
            ("Bare hands — chaos and instinct.",       (2,1,0)),
        ],
    },
    {
        "q": "11) You walk into a room full of people you don’t know. What happens next?",
        "options": [
            ("Everyone knows you by the end.",             (2,0,0)),
            ("You observe, then engage strategically.",    (0,2,0)),
            ("You find one person worth your time.",       (0,0,2)),
            ("You find the dog and vibe in the corner.",   (0,1,2)),
        ],
    },
    {
        "q": "12) You’re at the gym and someone’s ego-lifting loudly.",
        "options": [
            ("Cheer them on—vibes over form.",          (2,0,0)),
            ("Focus harder on your own set.",           (0,2,0)),
            ("Shake your head and mind your business.", (0,0,2)),
            ("Spot them just in case they fold.",       (1,1,1)),
        ],
    },
    {
        "q": "13) You’re most respected for:",
        "options": [
            ("Charisma and confidence.",      (2,0,0)),
            ("Consistency and focus.",        (0,2,0)),
            ("Reliability and calm presence.",(0,0,2)),
            ("Loyalty and depth.",            (1,1,1)),
        ],
    },
    {
        "q": "14) How do you handle a challenge you didn’t ask for?",
        "options": [
            ("Jump in and thrive on chaos.", (2,0,0)),
            ("Plan, prepare, and conquer.",  (0,2,0)),
            ("Roll with it, make it manageable.", (0,0,2)),
            ("Step back, think long-term, then move.", (1,1,2)),
        ],
    },
    {
        "q": "15) “Pick your poison” — your social fuel:",
        "options": [
            ("A few drinks with strangers and bad decisions.", (2,0,0)),
            ("Pre-workout, cold showers, and routine.",        (0,2,0)),
            ("A quiet smoke under the stars.",                 (0,0,2)),
            ("Herbal tea and meditation—it’s balance.",        (0,1,1)),
        ],
    },
    {
        "q": "16) You’re stranded in the desert with two strangers. First move?",
        "options": [
            ("Crack a joke, lighten the mood, get moving.", (2,0,0)),
            ("Assess supplies and assign tasks.",          (0,2,0)),
            ("Stay calm, look for water and shelter.",     (0,0,2)),
            ("Wait till sunset to travel—it’s smarter.",   (1,1,1)),
        ],
    },
    {
        "q": "17) You find a $100 bill on the ground.",
        "options": [
            ("Spend it on an experience, not a thing.", (2,0,0)),
            ("Save it; discipline adds up.",            (0,2,0)),
            ("Treat everyone around you to a meal.",    (0,0,2)),
            ("Split it evenly and call it karma.",      (1,1,1)),
        ],
    },
    {
        "q": "18) Someone close betrays your trust.",
        "options": [
            ("Cut them off, no explanation needed.", (2,0,0)),
            ("Confront them directly.",             (0,2,0)),
            ("Distance yourself quietly.",          (0,0,2)),
            ("Forgive, but never forget.",          (1,1,1)),
        ],
    },
    {
        "q": "19) You get one week completely free of responsibility.",
        "options": [
            ("Travel, flirt, live spontaneously.", (2,0,0)),
            ("Train, refine, build a new skill.",  (0,2,0)),
            ("Sleep, hike, recharge in peace.",    (0,0,2)),
            ("Visit family, reset priorities.",    (1,1,2)),
        ],
    },
    {
        "q": "20) What keeps you moving long-term?",
        "options": [
            ("Freedom—stories and adrenaline.",      (2,0,0)),
            ("Purpose—discipline and growth.",       (0,2,0)),
            ("Peace—balance and stability.",         (0,0,2)),
            ("Connection—building something that lasts.", (1,1,1)),
        ],
    },
]

# -----------------------
# Helper functions
# -----------------------
def pct(p, s, c):
    total = max(p + s + c, 1)
    return round(100*p/total, 1), round(100*s/total, 1), round(100*c/total, 1)

def blurb(pp, sp, cp):
    triples = [("Pirate", pp), ("Samurai", sp), ("Cowboy", cp)]
    top = sorted(triples, key=lambda x: x[1], reverse=True)
    top_name, _ = top[0]
    spread = max(pp, sp, cp) - min(pp, sp, cp)

    pirate = ("You lead with Pirate energy: bold, social, allergic to boredom. "
              "You collect stories like trophies and improvise under pressure.")
    samurai = ("You lead with Samurai energy: disciplined, precise, purpose-driven. "
               "You chase mastery and keep your cool when it counts.")
    cowboy = ("You lead with Cowboy energy: grounded, steady, self-sufficient. "
              "You value peace, loyalty, and showing up.")
    balanced = ("You’re a blended build—Pirate/Samurai/Cowboy in healthy tension. "
                "You can switch modes: charm, focus, or calm.")

    if spread <= 5:
        return balanced
    return {"Pirate": pirate, "Samurai": samurai, "Cowboy": cowboy}[top_name]

def _load_bg(uploaded_file):
    """Try uploaded file, then assets/triangle_bg.png, then triangle_bg.png at repo root."""
    if uploaded_file is not None:
        try:
            return Image.open(uploaded_file).convert("RGBA")
        except Exception:
            pass
    for path in [Path("assets/triangle_bg.png"), Path("triangle_bg.png")]:
        if path.exists():
            try:
                return Image.open(path).convert("RGBA")
            except Exception:
                continue
    return None

def triangle_plot(pp, sp, cp, bg_img=None):
    """
    Clean single-triangle output:
    - white background
    - ONE outlined equilateral triangle (no fill)
    - Correct corner labels: Pirate (top), Samurai (bottom-left), Cowboy (bottom-right)
    - Dot placed by barycentric mix of (Pirate, Samurai, Cowboy)
    - Percentages centered BELOW the figure
    NOTE: bg_img is intentionally ignored for a super clean look.
    """
    import io
    import matplotlib.pyplot as plt
    from math import sqrt

    # Triangle vertices (normalized)
    P = (0.0, 0.0)                # bottom-left  (Samurai)
    C = (1.0, 0.0)                # bottom-right (Cowboy)
    S = (0.5, sqrt(3)/2)          # top          (Pirate)

    # Normalize and compute barycentric mix
    total = max(pp + sp + cp, 1e-9)
    wp, ws, wc = pp/total, sp/total, cp/total

    # Interpolate point
    x = wp*P[0] + ws*S[0] + wc*C[0]
    y = wp*P[1] + ws*S[1] + wc*C[1]

    # Figure/canvas
    fig, ax = plt.subplots(figsize=(6, 6), facecolor="white")
    ax.set_facecolor("white")

    # ONE outlined triangle (no fill)
    xs = [P[0], C[0], S[0], P[0]]
    ys = [P[1], C[1], S[1], P[1]]
    ax.plot(xs, ys, color="#1f1f1f", linewidth=3, zorder=1)

    # Correct corner labels
    ax.text(S[0], S[1] + 0.03, "Pirate", fontsize=13, ha="center", va="bottom", zorder=2)
    ax.text(P[0] - 0.02, P[1] - 0.02, "Samurai", fontsize=13, ha="right", va="top", zorder=2)
    ax.text(C[0] + 0.02, C[1] - 0.02, "Cowboy", fontsize=13, ha="left", va="top", zorder=2)

    # Result dot
    ax.scatter([x], [y], s=180, color="orange", zorder=3)

    # Axes cosmetics
    pad = 0.1
    ax.set_xlim(-pad, 1 + pad)
    ax.set_ylim(-pad, S[1] + pad)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_aspect("equal", adjustable="box")
    ax.set_title("Pirate – Samurai – Cowboy Result", fontsize=14, pad=10)

    # Percentages BELOW the figure
    fig.text(0.5, 0.02, f"P {pp:.1f}%   S {sp:.1f}%   C {cp:.1f}%",
             ha="center", va="center", fontsize=12)

    # Save to buffer
    plt.tight_layout(rect=[0.04, 0.06, 0.96, 0.98])
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=180)
    plt.close(fig)
    buf.seek(0)
    return buf


def _load_font(size=48):
    """Load a real TTF (DejaVuSans from matplotlib) for crisp Story Card text."""
    try:
        font_path = font_manager.findfont("DejaVu Sans")
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()

def story_card(png_plot_bytes, pp, sp, cp, app_url=""):
    """Make a 1080x1920 Instagram story card with readable text."""
    W, H = 1080, 1920
    card = Image.new("RGB", (W, H), (16, 16, 20))

    plot_img = Image.open(io.BytesIO(png_plot_bytes.getvalue())).convert("RGBA")
    target_w = int(W * 0.86)
    aspect = plot_img.height / plot_img.width
    plot_resized = plot_img.resize((target_w, int(target_w * aspect)))
    px = (W - plot_resized.width) // 2
    py = int(H * 0.28)
    card.paste(plot_resized, (px, py), plot_resized)

    draw = ImageDraw.Draw(card)
    font_title = _load_font(72)
    font_sub   = _load_font(44)
    font_meta  = _load_font(38)

    title = "🏴‍☠️ Pirate • 🥋 Samurai • 🤠 Cowboy"
    subtitle = f"P {pp:.1f}%   S {sp:.1f}%   C {cp:.1f}%"
    urltxt = f"Try it: {app_url}" if app_url else ""

    def center(text, y, font, fill=(240,240,240)):
        w, _ = draw.textbbox((0,0), text, font=font)[2:]
        draw.text(((W - w) / 2, y), text, font=font, fill=fill)

    center(title, 80, font_title)
    center("Your PSC Result", 170, font_sub, (200, 210, 230))
    center(subtitle, py + plot_resized.height + 36, font_sub, (230, 230, 235))
    if urltxt:
        center(urltxt, H - 120, font_meta, (180, 200, 255))

    out = io.BytesIO()
    card.save(out, format="PNG", optimize=True)
    out.seek(0)
    return out

def share_text(pp, sp, cp, app_url: str):
    base = f"I got Pirate {pp:.1f}%, Samurai {sp:.1f}%, Cowboy {cp:.1f}% on the PSC test."
    if app_url:
        base += f" Try it: {app_url}"
    return base

# -----------------------
# App State
# -----------------------
if "answers" not in st.session_state:
    st.session_state.answers = [None] * len(QUESTIONS)
if "page" not in st.session_state:
    st.session_state.page = 0

def next_page():
    if st.session_state.page < len(QUESTIONS):
        st.session_state.page += 1

def prev_page():
    if st.session_state.page > 0:
        st.session_state.page -= 1

# -----------------------
# UI
# -----------------------
st.title("🏴‍☠️Pirate • 🥋Samurai • 🤠Cowboy Test")
st.caption("Answer honestly. Phone-friendly. Share your dot on the triangle at the end.")

with st.sidebar:
    st.subheader("Branding & Share")
    app_url = st.text_input(
        "Your hosted app URL (optional)",
        placeholder="https://your-streamlit-app-url",
        help="Paste your Streamlit Cloud URL here to include it in the share text & story card."
    )
    uploaded_bg = st.file_uploader("Upload background image (optional)", type=["png","jpg","jpeg"])
    st.markdown("Or keep a file at **assets/triangle_bg.png** or **triangle_bg.png** in the repo root.")

page = st.session_state.page

if page < len(QUESTIONS):
    q = QUESTIONS[page]
    st.markdown(f"### {q['q']}")

    options = [opt for opt, _ in q["options"]]
    # --- No default selection: index=None; return value is the option text or None ---
    choice = st.radio(
        "Choose one:",
        options=options,
        index=None,                 # <-- nothing selected initially
        label_visibility="collapsed",
        key=f"radio_{page}",        # unique key per page
    )

    # update state answer if chosen
    if choice is not None:
        st.session_state.answers[page] = options.index(choice)
    else:
        st.session_state.answers[page] = None

    cols = st.columns(2)
    with cols[0]:
        st.button("← Back", on_click=prev_page, disabled=(page == 0))
    with cols[1]:
        st.button("Next →", on_click=next_page, disabled=(st.session_state.answers[page] is None))

    st.progress((page+1)/len(QUESTIONS))
else:
    # Compute scores
    p = s = c = 0
    for i, q in enumerate(QUESTIONS):
        idx = st.session_state.answers[i] if st.session_state.answers[i] is not None else 0
        wp, ws, wc = q["options"][idx][1]
        p += wp; s += ws; c += wc

    pp, sp, cp = pct(p, s, c)
    st.subheader("Your Results")
    st.write(f"**Pirate:** {pp:.1f}% &nbsp;&nbsp; **Samurai:** {sp:.1f}% &nbsp;&nbsp; **Cowboy:** {cp:.1f}%")
    st.info(textwrap.fill(blurb(pp, sp, cp), width=80))

    # Brand bg (uploaded > assets > root)
    bg_img = _load_bg(uploaded_bg)

    # Plot
    png_buf = triangle_plot(pp, sp, cp, bg_img=bg_img)
    st.image(png_buf, caption="Your dot on the triangle", use_container_width=True)

    # Download image
    st.download_button("Download result image", data=png_buf, file_name="psc_result.png", mime="image/png")

    # Share section
    st.divider()
    st.subheader("Share my result")
    txt = share_text(pp, sp, cp, app_url.strip())
    st.text_area("Share text (copy anywhere):", value=txt, height=80)

    encoded = urllib.parse.quote_plus(txt)
    twitter_url = f"https://twitter.com/intent/tweet?text={encoded}"
    whatsapp_url = f"https://api.whatsapp.com/send?text={encoded}"
    colx = st.columns(2)
    with colx[0]:
        st.link_button("Share on X/Twitter", twitter_url, use_container_width=True)
    with colx[1]:
        st.link_button("Share on WhatsApp", whatsapp_url, use_container_width=True)

    # Story card export
    st.divider()
    st.subheader("Instagram Story Card")
    story_png = story_card(png_buf, pp, sp, cp, app_url.strip())
    st.download_button("Download Story Card (1080x1920)", data=story_png, file_name="psc_story.png", mime="image/png")

    st.divider()
    st.button(
        "Retake quiz",
        on_click=lambda: [st.session_state.update({"answers":[None]*len(QUESTIONS), "page":0})],
        type="primary"
    )
