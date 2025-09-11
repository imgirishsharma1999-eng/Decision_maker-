import streamlit as st
import pandas as pd
import json
from datetime import datetime
import plotly.express as px
import base64
import random
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# Set page config for mobile
st.set_page_config(
    page_title="🧭 The Philosopher's Mirror",
    layout="centered",
    initial_sidebar_state="collapsed"  # Better for mobile
)

# Custom CSS for mobile responsiveness
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: #e0e0e0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        padding: 10px;
    }
    .stSlider > div {
        background-color: #1a1a1a;
    }
    .stButton button {
        background: linear-gradient(45deg, #007bff, #00d4ff);
        color: white;
        border-radius: 12px;
        border: none;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: bold;
        transition: all 0.3s ease;
        width: 100%;
        margin: 5px 0;
    }
    .stButton button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 15px rgba(0,123,255,0.4);
    }
    .insight-box {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        padding: 15px;
        border-radius: 15px;
        margin: 15px 0;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        font-size: 14px;
    }
    .option-card {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        color: white;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        transition: transform 0.3s ease;
    }
    .option-card:hover {
        transform: translateY(-3px);
    }
    .aspect-box {
        background-color: rgba(255,255,255,0.1);
        padding: 15px;
        border-radius: 12px;
        margin: 10px 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    .reflection-box {
        background: linear-gradient(135deg, #3a1c71, #d76d77, #ffaf7b);
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        color: white;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .fade-in {
        animation: fadeIn 0.8s ease-out;
    }
    .progress-container {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        padding: 10px;
        margin: 15px 0;
    }
    /* Mobile-specific adjustments */
    @media (max-width: 768px) {
        .main {
            padding: 5px;
        }
        .stButton button {
            font-size: 14px;
            padding: 10px 20px;
        }
        .insight-box, .option-card, .aspect-box {
            padding: 12px;
        }
        h1, h2, h3, h4 {
            font-size: 1.2em;
        }
        p, div {
            font-size: 0.95em;
        }
    }
</style>
""", unsafe_allow_html=True)

# Add sound effects (fixed URLs)
st.markdown("""
<audio id="clickSound">
  <source src="https://www.soundjay.com/button/sounds/button-09.mp3" type="audio/mpeg">
</audio>
<audio id="successSound">
  <source src="https://www.soundjay.com/misc/sounds/bell-ringing-05.mp3" type="audio/mpeg">
</audio>
<script>
document.addEventListener('DOMContentLoaded', function() {
    var sliders = document.querySelectorAll('input[type="range"]');
    sliders.forEach(function(slider) {
        slider.addEventListener('input', function() {
            var sound = document.getElementById('clickSound');
            sound.volume = 0.3;
            sound.play();
        });
    });
});
</script>
""", unsafe_allow_html=True)

# Title & Description
st.markdown('<div class="fade-in">', unsafe_allow_html=True)
st.title("🧭 The Philosopher's Mirror")
st.write("Rate options across aspects, reflect deeply, and understand your choices better — through the lens of wisdom.")
st.markdown('</div>', unsafe_allow_html=True)

# --- Sidebar: Settings (now in expander for mobile) ---
with st.expander("⚙️ Settings"):
    use_custom_aspects = st.checkbox("Use custom aspects?", value=False)
    dark_mode = st.checkbox("Dark Mode", value=True)
    show_animations = st.checkbox("Show Animations", value=True)
    
    st.divider()
    if st.button("🔄 Reset All Data"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    with st.expander("❓ How to Use This Tool"):
        st.markdown("""
        1. Set number of options  
        2. Choose or define your decision aspects  
        3. Weight each aspect by importance  
        4. For each option, rate and reflect deeply  
        5. Click **Compute** to see your aligned choice  
        6. Unlock philosophical, psychological, and evolutionary insights  
        7. Save, download, or revisit past decisions
        """)

# --- Mood Tracker ---
st.subheader("😊 How are you feeling right now?")
mood = st.select_slider(
    "Select your current mood",
    options=["😢 Very Sad", "😕 Sad", "😐 Neutral", "🙂 Happy", "😄 Very Happy"],
    key="mood_tracker"
)

mood_insights = {
    "😢 Very Sad": "💡 You might be making cautious choices right now. That's okay.",
    "😕 Sad": "💡 You're in a reflective mood — great for deep decisions.",
    "😐 Neutral": "💡 Balanced state — good for objective thinking.",
    "🙂 Happy": "💡 Positive mood can lead to optimistic choices.",
    "😄 Very Happy": "💡 Joyful state — you might take more risks today."
}

st.markdown(f'<div class="insight-box">{mood_insights[mood]}</div>', unsafe_allow_html=True)

# --- Step 1: Input Options ---
num_options = st.number_input("How many options do you want to evaluate?", min_value=1, max_value=10, step=1, value=2)
options = []
for i in range(num_options):
    option_name = st.text_input(f"Enter name for Option {i+1}", key=f"option_{i}").strip()
    if option_name:
        options.append(option_name)

if not options:
    st.warning("⚠️ Please enter at least one valid option name.")
    st.stop()

# --- Step 2: Define Aspects with Icons & Insights ---
if use_custom_aspects:
    aspects = []
    num_aspects = st.number_input("Number of aspects:", min_value=1, max_value=10, value=6)
    for i in range(num_aspects):
        aspect = st.text_input(f"Aspect {i+1}:", key=f"aspect_{i}", value="")
        if aspect.strip():
            aspects.append(aspect.strip())
    if not aspects:
        st.warning("⚠️ Please define at least one aspect.")
        st.stop()
else:
    aspects = ["Values Alignment", "Long-Term Vision", "Emotional Resonance",
               "Impact on Others & System", "Risk Tolerance", "Intuition"]

st.subheader("🎯 Set importance (weights) for each aspect (1 = low, 5 = high)")
weights = {}
aspect_icons = {
    "Values Alignment": "🌟",
    "Long-Term Vision": "🚀",
    "Emotional Resonance": "❤️",
    "Impact on Others & System": "🤝",
    "Risk Tolerance": "⚠️",
    "Intuition": "🧠"
}

aspect_insights = {
    "Values Alignment": "How much your core values guide your life. High weight means you care deeply about doing what's right for you.",
    "Long-Term Vision": "How much you think about where you're headed in 5–10 years. High weight means you're future-focused.",
    "Emotional Resonance": "How strongly an option feels right or wrong in your heart. High weight means you trust your emotions.",
    "Impact on Others & System": "How much you care about the ripple effects of your choice. High weight means you're a team player.",
    "Risk Tolerance": "How much uncertainty you're willing to accept. High weight means you're bold and adventurous.",
    "Intuition": "How much you trust your gut feeling. High weight means you listen to your inner voice."
}

def render_aspect_input(aspect, icon, description, insight_map, weights, scores, reflections, option=None):
    st.markdown(f"<h4>{icon} {aspect}</h4>", unsafe_allow_html=True)
    st.write(f"💡 *{description}*")
    
    key_prefix = f"weight_{aspect}" if option is None else f"{option}_{aspect}"
    help_text = f"Set how important {aspect} is to you." if option is None else f"How much does {aspect} matter for {option}?"
    
    score = st.slider(
        f"Rate {aspect}{' for ' + option if option else ''}",
        1, 5, 3,
        key=key_prefix,
        help=help_text
    )
    
    if option:
        scores[option][aspect] = score
        why = st.text_area(
            f"🧠 Reflect: What made you choose {score} for {aspect}?",
            key=f"why_{option}_{aspect}",
            height=100,
            placeholder="Share your thoughts, memories, or feelings..."
        )
        reflections[option][aspect] = {"score": score, "why": why}
        st.write(f"📌 *Insight:* {insight_map[aspect]}")
    else:
        weights[aspect] = score
        if score == 1:
            st.write("📌 Low weight: You don't prioritize this much.")
        elif score == 2:
            st.write("📌 Moderate-low: This matters, but not top priority.")
        elif score == 3:
            st.write("📌 Balanced: This is important, but not dominant.")
        elif score == 4:
            st.write("📌 High: This is a major factor in your decision.")
        else:
            st.write("📌 Very high: This is your top priority.")

aspect_descriptions = {
    "Values Alignment": "How well does this option match your core beliefs and principles?",
    "Long-Term Vision": "Does this choice align with where you want to be in 5-10 years?",
    "Emotional Resonance": "How does this option make you feel emotionally?",
    "Impact on Others & System": "How will this choice affect the people around you?",
    "Risk Tolerance": "Are you comfortable with the uncertainty this option brings?",
    "Intuition": "What does your gut feeling tell you about this choice?"
}

aspect_insights_map = {
    "Values Alignment": "High score = your values are a strong guide. Low score = you're flexible.",
    "Long-Term Vision": "High score = future-focused. Low score = present-focused.",
    "Emotional Resonance": "High score = emotions drive you. Low score = logic leads.",
    "Impact on Others & System": "High score = you care about others. Low score = self-focused.",
    "Risk Tolerance": "High score = bold and adventurous. Low score = cautious and safe.",
    "Intuition": "High score = you trust your gut. Low score = you rely on facts."
}

for aspect in aspects:
    icon = aspect_icons.get(aspect, "🔍")
    render_aspect_input(aspect, icon, aspect_insights[aspect], aspect_insights_map, weights, {}, {}, None)

# --- Total Weight Summary ---
total_weight = sum(weights.values())
st.markdown('<div class="insight-box">', unsafe_allow_html=True)
st.write(f"📊 **Total Weight: {total_weight}/30**")
if total_weight < 15:
    st.write("→ You're more flexible — no single factor dominates.")
elif total_weight < 20:
    st.write("→ You're balanced — multiple factors matter equally.")
else:
    st.write("→ You're focused — one or two factors are driving your choice.")
st.markdown('</div>', unsafe_allow_html=True)

# --- Step 3: Evaluate Options with Deep Reflection ---
st.subheader("📊 Rate each option (1–5) + Self Reflection")

scores = {}
reflections = {}

for option in options:
    scores[option] = {}
    reflections[option] = {}
    
    # Option Card
    st.markdown(f'<div class="option-card"><h2>🎯 {option}</h2></div>', unsafe_allow_html=True)
    
    # Aspects Rating
    for aspect in aspects:
        st.markdown(f'<div class="aspect-box">', unsafe_allow_html=True)
        icon = aspect_icons.get(aspect, "🔍")
        render_aspect_input(aspect, icon, aspect_descriptions[aspect], aspect_insights_map, weights, scores, reflections, option)
        st.markdown('</div>', unsafe_allow_html=True)

    # Social Influence Section
    st.markdown(f'<div class="option-card"><h3>👥 Social Reflection for {option}</h3></div>', unsafe_allow_html=True)
    social = st.slider(
        f"How much did others influence your scores for {option}?", 
        1, 5, 3, 
        key=f"social_{option}"
    )
    whose = st.text_input(
        f"Whose opinion mattered most for {option}?", 
        key=f"whose_{option}",
        placeholder="e.g., My parents, My mentor, My friend..."
    )
    reflections[option]["social"] = {"influence": social, "whose": whose}

    # Values Section
    st.markdown(f'<div class="option-card"><h3>🌟 Your Core Values for {option}</h3></div>', unsafe_allow_html=True)
    st.write("List your top 3 values that matter most in this decision:")
    val1 = st.text_input("Value 1", key=f"val1_{option}", placeholder="e.g., Freedom")
    val2 = st.text_input("Value 2", key=f"val2_{option}", placeholder="e.g., Growth")
    val3 = st.text_input("Value 3", key=f"val3_{option}", placeholder="e.g., Compassion")
    reflections[option]["values"] = [val1, val2, val3]

# --- Progress Tracker ---
completed_aspects = sum(
    1 for opt in reflections 
    for aspect in reflections[opt] 
    if isinstance(reflections[opt][aspect], dict) 
    and reflections[opt][aspect].get('why', '').strip()
)
total_aspects = len(options) * len(aspects)
progress = (completed_aspects / total_aspects) * 100 if total_aspects > 0 else 0

st.markdown('<div class="progress-container">', unsafe_allow_html=True)
st.progress(progress / 100)
st.write(f"🎯 Reflection Progress: {completed_aspects}/{total_aspects} aspects completed")
st.markdown('</div>', unsafe_allow_html=True)

# --- Philosophical Lenses ---
PHILOSOPHICAL_LENS = {
    "stoic": {
        "name": "Stoic Lens",
        "focus": "Focus on virtue, control, and acceptance.",
        "insight": "What is within your control? What is not? A Stoic focuses on action, not outcome.",
        "quote": "“We suffer more in imagination than in reality.” — Seneca"
    },
    "buddhist": {
        "name": "Buddhist Lens",
        "focus": "Detachment, impermanence, compassion.",
        "insight": "Does this choice lead to suffering or liberation? Does it increase attachment?",
        "quote": "“All compounded things are subject to decay.” — Buddha"
    },
    "existentialist": {
        "name": "Existentialist Lens",
        "focus": "Freedom, responsibility, authenticity.",
        "insight": "Are you choosing this freely? Are you owning the consequences?",
        "quote": "“Man is condemned to be free.” — Jean-Paul Sartre"
    },
    "utilitarian": {
        "name": "Utilitarian Lens",
        "focus": "Greatest good for the greatest number.",
        "insight": "Which option benefits the most people? What is the net impact?",
        "quote": "“It is the greatest happiness of the greatest number that is the measure of right and wrong.” — Jeremy Bentham"
    },
    "nihilist": {
        "name": "Nihilist Lens",
        "focus": "Absurdity, meaninglessness, rebellion.",
        "insight": "Does this choice even matter? Is it worth the effort?",
        "quote": "“He who has a why to live can bear almost any how.” — Nietzsche"
    }
}

# --- Psychological Archetypes ---
PSYCHOLOGICAL_ARCHETYPES = {
    "hero": {
        "name": "The Hero",
        "description": "You are driven to overcome obstacles and seek transformation.",
        "traits": ["Courageous", "Goal-oriented", "Self-sacrificing"],
        "quote": "“A hero is someone who has given his or her life to something bigger than oneself.” — Joseph Campbell"
    },
    "caregiver": {
        "name": "The Caregiver",
        "description": "You are motivated by compassion and service to others.",
        "traits": ["Empathetic", "Nurturing", "Altruistic"],
        "quote": "“No one has ever become poor by giving.” — Anne Frank"
    },
    "explorer": {
        "name": "The Explorer",
        "description": "You seek freedom, discovery, and authenticity.",
        "traits": ["Adventurous", "Independent", "Curious"],
        "quote": "“Not all those who wander are lost.” — J.R.R. Tolkien"
    },
    "rebel": {
        "name": "The Rebel",
        "description": "You challenge norms and seek to disrupt systems.",
        "traits": ["Bold", "Anti-establishment", "Visionary"],
        "quote": "“The reasonable man adapts himself to the world; the unreasonable one persists in trying to adapt the world to himself.” — George Bernard Shaw"
    },
    "creator": {
        "name": "The Creator",
        "description": "You are driven to express yourself and build something new.",
        "traits": ["Imaginative", "Innovative", "Visionary"],
        "quote": "“Every creator painfully experiences the chasm between his inner vision and its ultimate expression.” — Isaac Bashevis Singer"
    }
}

# --- Evolutionary Insights ---
EVOLUTIONARY_INSIGHTS = {
    "risk_seeker": {
        "name": "Risk-Taking Behavior",
        "description": "You may be driven by reward-seeking, novelty, or social status.",
        "insight": "In ancestral times, risk-takers often became leaders or innovators — but also more vulnerable."
    },
    "security_seeker": {
        "name": "Security-Seeking Behavior",
        "description": "You prefer stability, safety, and known outcomes.",
        "insight": "Evolutionarily, this was a survival strategy — but may limit growth in modern contexts."
    },
    "social_oriented": {
        "name": "Socially Aligned",
        "description": "You are highly influenced by others and group dynamics.",
        "insight": "Humans evolved to survive in groups — your decisions reflect that deep wiring."
    },
    "autonomous": {
        "name": "Autonomous Decision-Maker",
        "description": "You prioritize independence and self-direction.",
        "insight": "This reflects a strong individualist trait — historically rare, now common in modern societies."
    }
}

# --- Compute Scores & Show Results ---
if st.button("✅ Unlock Insights & Wisdom"):
    with st.spinner("Analyzing your decisions through the lens of wisdom... 🧠"):
        # Play success sound
        st.markdown("""
        <script>
        var sound = document.getElementById('successSound');
        sound.volume = 0.5;
        sound.play();
        </script>
        """, unsafe_allow_html=True)
        
        # Ensure all options have all aspects (even if missing, fill with 3)
        all_aspects = set(aspects)
        for option in scores:
            for aspect in all_aspects:
                if aspect not in scores[option]:
                    scores[option][aspect] = 3  # default neutral
        
        results = []
        for option, option_scores in scores.items():
            weighted_total = sum(option_scores[a] * weights[a] for a in aspects)
            results.append({"Option": option, "Total Score": weighted_total})
        
        results_df = pd.DataFrame(results).sort_values(by="Total Score", ascending=False)
        
        # Display results
        st.subheader("🏆 Final Scores & Ranking")
        st.dataframe(results_df.reset_index(drop=True))
        
        best_option = results_df.iloc[0]["Option"]
        st.success(f"🎯 Recommended Option: **{best_option}**")
        
        # --- Visual Comparison (Radar Chart) ---
        st.subheader("📈 Visual Comparison (Radar Plot)")
        chart_data = pd.DataFrame(scores).T
        fig = px.line_polar(chart_data, r=chart_data.columns, theta=chart_data.columns, line_close=True, title="Radar Chart of Options", line_shape='spline')
        st.plotly_chart(fig, use_container_width=True)
        
        # --- Philosophical Insight Engine ---
        def get_philosophical_insight(scores, reflections):
            avg_risk = sum([scores[opt]["Risk Tolerance"] for opt in scores]) / len(scores)
            avg_emotion = sum([scores[opt]["Emotional Resonance"] for opt in scores]) / len(scores)
            avg_vision = sum([scores[opt]["Long-Term Vision"] for opt in scores]) / len(scores)
            
            if avg_risk > 4:
                lens = "nihilist"
            elif avg_vision > 4:
                lens = "stoic"
            elif avg_emotion > 4:
                lens = "buddhist"
            else:
                lens = random.choice(["utilitarian", "existentialist"])
            
            return PHILOSOPHICAL_LENS[lens]
        
        def get_archetype(scores):
            avg_risk = sum([scores[opt]["Risk Tolerance"] for opt in scores]) / len(scores)
            avg_emotion = sum([scores[opt]["Emotional Resonance"] for opt in scores]) / len(scores)
            avg_vision = sum([scores[opt]["Long-Term Vision"] for opt in scores]) / len(scores)
            avg_social = sum([scores[opt]["Impact on Others & System"] for opt in scores]) / len(scores)
            
            if avg_risk > 4:
                return "rebel"
            elif avg_emotion > 4 and avg_social > 4:
                return "caregiver"
            elif avg_vision > 4:
                return "hero"
            elif avg_social > 4:
                return "explorer"
            else:
                return "creator"
        
        def get_evolutionary_insight(scores):
            avg_risk = sum([scores[opt]["Risk Tolerance"] for opt in scores]) / len(scores)
            avg_social = sum([scores[opt]["Impact on Others & System"] for opt in scores]) / len(scores)
            
            if avg_risk > 4:
                return "risk_seeker"
            elif avg_risk < 3:
                return "security_seeker"
            elif avg_social > 4:
                return "social_oriented"
            else:
                return "autonomous"
        
        def calculate_wisdom_score(scores, weights):
            avg_virtue = (scores[best_option]["Values Alignment"] + scores[best_option]["Long-Term Vision"]) / 2
            avg_balance = (scores[best_option]["Emotional Resonance"] + scores[best_option]["Intuition"]) / 2
            avg_impact = scores[best_option]["Impact on Others & System"]
            wisdom = (avg_virtue + avg_balance + avg_impact) / 3
            return round(wisdom, 1)
        
        # --- Generate Insights ---
        philosophical = get_philosophical_insight(scores, reflections)
        archetype = get_archetype(scores)
        evolutionary = get_evolutionary_insight(scores)
        wisdom_score = calculate_wisdom_score(scores, weights)
        
        # --- Display Insights ---
        st.subheader("🧠 Wisdom Insights")
        
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.write(f"🧠 **Philosophical Lens**: {philosophical['name']}")
        st.write(f"💡 {philosophical['insight']}")
        st.write(f"📜 {philosophical['quote']}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.write(f"🎭 **Archetype**: {PSYCHOLOGICAL_ARCHETYPES[archetype]['name']}")
        st.write(f"💡 {PSYCHOLOGICAL_ARCHETYPES[archetype]['description']}")
        st.write(f"📜 {PSYCHOLOGICAL_ARCHETYPES[archetype]['quote']}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.write(f"🧬 **Evolutionary Insight**: {EVOLUTIONARY_INSIGHTS[evolutionary]['name']}")
        st.write(f"💡 {EVOLUTIONARY_INSIGHTS[evolutionary]['insight']}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.write(f"✨ **Wisdom Score**: {wisdom_score} / 5")
        if wisdom_score < 2:
            st.write("→ You may benefit from more reflection or philosophical grounding.")
        elif wisdom_score < 4:
            st.write("→ You are on a thoughtful path — continue exploring.")
        else:
            st.write("→ You are deeply aligned with wisdom and virtue.")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # --- Deep Reflection Report ---
        st.subheader("📖 Deep Reflection Report")
        for option in options:
            if option:
                st.markdown(f"### 📖 {option}")
                
                # Psychological
                st.write("🧠 **Psychological Insights:**")
                for aspect in aspects:
                    why = reflections[option][aspect]["why"]
                    if why.strip():
                        st.write(f"- **{aspect}**: {scores[option][aspect]} — *{why}*")
                
                # Social
                social = reflections[option]["social"]
                if social['whose'].strip():
                    st.write(f"👥 **Social Influence**: {social['influence']}/5 — *Influenced by {social['whose']}*")
                
                # Values
                vals = [v for v in reflections[option]["values"] if v.strip()]
                if vals:
                    st.write(f"🌟 **Core Values**: {', '.join(vals)}")
                
                # Evolutionary Insight
                avg_score = sum(scores[option].values()) / len(scores[option])
                if avg_score > 3.5:
                    insight = "🧬 This choice reflects high reward-seeking behavior, common in growth-oriented individuals."
                else:
                    insight = "🧬 This choice reflects security-seeking behavior, common in stability-focused individuals."
                st.write(insight)
                reflections[option]["evolutionary"] = insight
        
        # --- Save Decision ---
        def serialize_for_json(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, pd.DataFrame):
                return obj.to_dict(orient='records')
            if isinstance(obj, dict):
                return {k: serialize_for_json(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [serialize_for_json(item) for item in obj]
            return obj
        
        decision_data = {
            "timestamp": datetime.now(),
            "options": options,
            "aspects": aspects,
            "weights": weights,
            "scores": scores,
            "reflections": reflections,
            "results": results_df.to_dict(orient='records'),
            "mood": mood,
            "philosophical": philosophical,
            "archetype": archetype,
            "evolutionary": evolutionary,
            "wisdom_score": wisdom_score
        }
        
        decision_data = serialize_for_json(decision_data)
        
        # Save to session state
        if 'saved_decisions' not in st.session_state:
            st.session_state.saved_decisions = []
        st.session_state.saved_decisions.append(decision_data)
        
        # --- Export to PDF ---
        def create_pdf(decision_data):
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Title
            story.append(Paragraph("The Philosopher's Mirror - Decision Report", styles['Title']))
            story.append(Spacer(1, 12))

            # Timestamp
            story.append(Paragraph(f"<b>Timestamp:</b> {decision_data['timestamp']}", styles['Normal']))
            story.append(Spacer(1, 12))

            # Options
            story.append(Paragraph("<b>Options:</b>", styles['Heading2']))
            for opt in decision_data['options']:
                story.append(Paragraph(f"• {opt}", styles['Normal']))
            story.append(Spacer(1, 12))

            # Aspects
            story.append(Paragraph("<b>Aspects:</b>", styles['Heading2']))
            for aspect in decision_data['aspects']:
                story.append(Paragraph(f"• {aspect}", styles['Normal']))
            story.append(Spacer(1, 12))

            # Results
            story.append(Paragraph("<b>Results:</b>", styles['Heading2']))
            for result in decision_data['results']:
                story.append(Paragraph(f"{result['Option']}: {result['Total Score']}", styles['Normal']))
            story.append(Spacer(1, 12))

            # Philosophical Insight
            story.append(Paragraph("<b>Philosophical Lens:</b>", styles['Heading2']))
            story.append(Paragraph(f"{decision_data['philosophical']['name']}", styles['Normal']))
            story.append(Paragraph(f"{decision_data['philosophical']['insight']}", styles['Italic']))
            story.append(Paragraph(f"{decision_data['philosophical']['quote']}", styles['Normal']))
            story.append(Spacer(1, 12))

            # Archetype
            story.append(Paragraph("<b>Archetype:</b>", styles['Heading2']))
            story.append(Paragraph(f"{decision_data['archetype']['name']}", styles['Normal']))
            story.append(Paragraph(f"{decision_data['archetype']['description']}", styles['Italic']))
            story.append(Paragraph(f"{decision_data['archetype']['quote']}", styles['Normal']))
            story.append(Spacer(1, 12))

            # Evolutionary
            story.append(Paragraph("<b>Evolutionary Insight:</b>", styles['Heading2']))
            story.append(Paragraph(f"{decision_data['evolutionary']['name']}", styles['Normal']))
            story.append(Paragraph(f"{decision_data['evolutionary']['insight']}", styles['Normal']))
            story.append(Spacer(1, 12))

            # Wisdom Score
            story.append(Paragraph("<b>Wisdom Score:</b>", styles['Heading2']))
            story.append(Paragraph(f"{decision_data['wisdom_score']} / 5", styles['Normal']))
            story.append(Spacer(1, 12))

            # Reflections
            story.append(Paragraph("<b>Reflections:</b>", styles['Heading2']))
            for option in decision_data['options']:
                if option in decision_data['reflections']:
                    ref = decision_data['reflections'][option]
                    story.append(Paragraph(f"<b>{option}:</b>", styles['Heading3']))
                    for aspect in decision_data['aspects']:
                        if aspect in ref and 'why' in ref[aspect] and ref[aspect]['why'].strip():
                            story.append(Paragraph(f"<i>{aspect}:</i> {ref[aspect]['why']}", styles['Normal']))
                    if 'social' in ref and ref['social']['whose'].strip():
                        story.append(Paragraph(f"<i>Social:</i> Influenced by {ref['social']['whose']}", styles['Normal']))
                    vals = [v for v in ref['values'] if v.strip()]
                    if vals:
                        story.append(Paragraph(f"<i>Values:</i> {', '.join(vals)}", styles['Normal']))
            story.append(Spacer(1, 12))

            doc.build(story)
            buffer.seek(0)
            return buffer

        pdf_buffer = create_pdf(decision_data)
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_buffer,
            file_name=f"decision_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf"
        )

        # Export to CSV
        csv = results_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💾 Download Results as CSV",
            data=csv,
            file_name='decision_results.csv',
            mime='text/csv'
        )
        
        # Export to JSON
        json_str = json.dumps(decision_data, indent=2, ensure_ascii=False)
        b64_json = base64.b64encode(json_str.encode()).decode()
        href = f'<a href="file/json;base64,{b64_json}" download="decision_analysis.json">📥 Download Full Analysis (JSON)</a>'
        st.markdown(href, unsafe_allow_html=True)

# --- Step 9: Load Saved Decisions ---
st.subheader("📂 Past Decisions")
if 'saved_decisions' in st.session_state and st.session_state.saved_decisions:
    for i, decision in enumerate(st.session_state.saved_decisions):
        with st.expander(f"Decision #{i+1} - {decision['timestamp']}"):
            st.write("**Options:**", decision['options'])
            st.write("**Aspects:**", decision['aspects'])
            st.write("**Weights:**", decision['weights'])
            st.write("**Results:**")
            results_df = pd.DataFrame(decision['results'])
            st.dataframe(results_df)
            
            st.write("**Reflection Summary:**")
            for option in decision['options']:
                if option in decision['reflections']:
                    ref = decision['reflections'][option]
                    st.write(f"**{option}:**")
                    for aspect in decision['aspects']:
                        if aspect in ref and 'why' in ref[aspect] and ref[aspect]['why'].strip():
                            st.write(f"- {aspect}: {ref[aspect]['why']}")
                    if 'social' in ref and ref['social']['whose'].strip():
                        st.write(f"👥 Social: Influenced by {ref['social']['whose']}")
                    vals = [v for v in ref['values'] if v.strip()]
                    if vals:
                        st.write(f"🌟 Values: {', '.join(vals)}")
            
            st.write(f"🎭 Archetype: {decision.get('archetype', {}).get('name', 'N/A')}")
            st.write(f"🧠 Philosophical Lens: {decision.get('philosophical', {}).get('name', 'N/A')}")
            st.write(f"🧬 Evolutionary Insight: {decision.get('evolutionary', {}).get('name', 'N/A')}")
            st.write(f"✨ Wisdom Score: {decision.get('wisdom_score', 'N/A')}")
            st.write(f"😊 Mood: {decision.get('mood', 'N/A')}")

# Footer
st.markdown("---")
st.caption("🧠 Use this tool to make decisions aligned with your core values and long-term vision — through the lens of wisdom.")
