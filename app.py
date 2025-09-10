# enhanced_decision_app_final.py
import streamlit as st
import pandas as pd
import json
from datetime import datetime
import plotly.express as px
import base64

# Set page config
st.set_page_config(
    page_title="🧭 Enhanced Decision Alignment Helper",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        color: #e0e0e0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
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
    }
    .stButton button:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 15px rgba(0,123,255,0.4);
    }
    .insight-box {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .option-card {
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        color: white;
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        transition: transform 0.3s ease;
    }
    .option-card:hover {
        transform: translateY(-5px);
    }
    .aspect-box {
        background-color: rgba(255,255,255,0.1);
        padding: 20px;
        border-radius: 12px;
        margin: 15px 0;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    .reflection-box {
        background: linear-gradient(135deg, #3a1c71, #d76d77, #ffaf7b);
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
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
        padding: 15px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# Add sound effects
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
st.title("🧭 Enhanced Decision Alignment Helper")
st.write("Rate options across aspects, reflect deeply, and understand your choices better.")
st.markdown('</div>', unsafe_allow_html=True)

# --- Sidebar: Settings ---
with st.sidebar:
    st.header("⚙️ Settings")
    use_custom_aspects = st.checkbox("Use custom aspects?", value=False)
    dark_mode = st.checkbox("Dark Mode", value=True)
    show_animations = st.checkbox("Show Animations", value=True)

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
    option_name = st.text_input(f"Enter name for Option {i+1}", key=f"option_{i}")
    options.append(option_name)

# --- Step 2: Define Aspects with Icons & Insights ---
if use_custom_aspects:
    aspects = []
    num_aspects = st.number_input("Number of aspects:", min_value=1, max_value=10, value=6)
    for i in range(num_aspects):
        aspect = st.text_input(f"Aspect {i+1}:", key=f"aspect_{i}", value="")
        if aspect:
            aspects.append(aspect)
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

for aspect in aspects:
    icon = aspect_icons.get(aspect, "🔍")
    st.markdown(f"<h4>{icon} {aspect}</h4>", unsafe_allow_html=True)
    
    # Add insight
    st.write(f"💡 {aspect_insights[aspect]}")
    
    # Add slider
    weight = st.slider(
        f"{aspect} Weight", 
        1, 5, 3, 
        key=f"weight_{aspect}",
        help=f"Set how important {aspect} is to you. Higher = more important."
    )
    weights[aspect] = weight
    
    # Add psychological insight
    if weight == 1:
        st.write("📌 Low weight: You don't prioritize this much.")
    elif weight == 2:
        st.write("📌 Moderate-low: This matters, but not top priority.")
    elif weight == 3:
        st.write("📌 Balanced: This is important, but not dominant.")
    elif weight == 4:
        st.write("📌 High: This is a major factor in your decision.")
    else:
        st.write("📌 Very high: This is your top priority.")

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

# Aspect descriptions
aspect_descriptions = {
    "Values Alignment": "How well does this option match your core beliefs and principles?",
    "Long-Term Vision": "Does this choice align with where you want to be in 5-10 years?",
    "Emotional Resonance": "How does this option make you feel emotionally?",
    "Impact on Others & System": "How will this choice affect the people around you?",
    "Risk Tolerance": "Are you comfortable with the uncertainty this option brings?",
    "Intuition": "What does your gut feeling tell you about this choice?"
}

# Aspect insights
aspect_insights_map = {
    "Values Alignment": "High score = your values are a strong guide. Low score = you're flexible.",
    "Long-Term Vision": "High score = future-focused. Low score = present-focused.",
    "Emotional Resonance": "High score = emotions drive you. Low score = logic leads.",
    "Impact on Others & System": "High score = you care about others. Low score = self-focused.",
    "Risk Tolerance": "High score = bold and adventurous. Low score = cautious and safe.",
    "Intuition": "High score = you trust your gut. Low score = you rely on facts."
}

for option in options:
    if option:
        scores[option] = {}
        reflections[option] = {}
        
        # Option Card
        st.markdown(f'<div class="option-card"><h2>🎯 {option}</h2></div>', unsafe_allow_html=True)
        
        # Aspects Rating
        for aspect in aspects:
            st.markdown(f'<div class="aspect-box">', unsafe_allow_html=True)
            
            # Emoji + Aspect Name
            emoji = aspect_icons.get(aspect, "🔍")
            st.markdown(f"<h4>{emoji} {aspect}</h4>", unsafe_allow_html=True)
            
            # Why this matters
            st.write(f"💡 *{aspect_descriptions[aspect]}*")
            
            # Rating Slider
            score = st.slider(
                f"Rate {aspect} for {option}", 
                1, 5, 3, 
                key=f"{option}_{aspect}",
                help=f"How much does {aspect} matter for {option}?"
            )
            scores[option][aspect] = score
            
            # Real-time insight
            st.write(f"📌 *Insight:* {aspect_insights_map[aspect]}")
            
            # Reflection prompt
            why = st.text_area(
                f"🧠 Reflect: What made you choose {score} for {aspect}?", 
                key=f"why_{option}_{aspect}", 
                height=100,
                placeholder="Share your thoughts, memories, or feelings..."
            )
            reflections[option][aspect] = {"score": score, "why": why}
            
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
completed_aspects = sum(1 for opt in reflections for aspect in reflections[opt] 
                       if isinstance(reflections[opt][aspect], dict) and reflections[opt][aspect].get('why'))
total_aspects = len(options) * len(aspects)
progress = (completed_aspects / total_aspects) * 100 if total_aspects > 0 else 0

st.markdown('<div class="progress-container">', unsafe_allow_html=True)
st.progress(progress / 100)
st.write(f"🎯 Reflection Progress: {completed_aspects}/{total_aspects} aspects completed")
st.markdown('</div>', unsafe_allow_html=True)

# --- Step 4: Compute Scores & Show Results ---
if st.button("✅ Compute Scores & Show Reflection Report"):
    # Play success sound
    st.markdown("""
    <script>
    var sound = document.getElementById('successSound');
    sound.volume = 0.5;
    sound.play();
    </script>
    """, unsafe_allow_html=True)
    
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

    # --- Step 5: Visual Comparison (Radar Chart) ---
    st.subheader("📈 Visual Comparison (Radar Plot)")
    chart_data = pd.DataFrame(scores).T
    fig = px.line_polar(chart_data, r=chart_data.columns, theta=chart_data.columns, line_close=True, title="Radar Chart of Options")
    st.plotly_chart(fig, use_container_width=True)

    # --- Step 6: Insightful Analysis ---
    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
    st.write("💡 **Insights:**")
    top_score = results_df.iloc[0]["Total Score"]
    bottom_score = results_df.iloc[-1]["Total Score"]
    diff = top_score - bottom_score
    if diff < 1:
        st.write("The options are very close in alignment — consider deeper reflection or additional criteria.")
    elif diff < 3:
        st.write("There's a moderate gap — the top choice is likely strong but not decisive.")
    else:
        st.write("There's a clear winner — this option aligns most strongly with your values and goals.")
    
    # Suggest re-evaluation
    if len(options) > 1 and diff < 1.5:
        st.write("📌 Consider revisiting the weightings or gathering more information before deciding.")
    st.markdown('</div>', unsafe_allow_html=True)

    # --- AI Insights ---
    def generate_ai_insight(scores, reflections):
        emotional_scores = [scores[opt]["Emotional Resonance"] for opt in scores]
        risk_scores = [scores[opt]["Risk Tolerance"] for opt in scores]
        
        avg_emotion = sum(emotional_scores) / len(emotional_scores)
        avg_risk = sum(risk_scores) / len(risk_scores)
        
        if avg_emotion > 3.5 and avg_risk > 3.5:
            return "🤖 AI Insight: You're an adventurous decision-maker who trusts emotions and takes bold steps!"
        elif avg_emotion > 3.5:
            return "🤖 AI Insight: You're emotionally guided but play it safe — thoughtful yet feeling-driven."
        elif avg_risk > 3.5:
            return "🤖 AI Insight: You're bold and logical — willing to take risks but think before acting."
        else:
            return "🤖 AI Insight: You're cautious and balanced — you weigh all factors carefully before deciding."

    ai_insight = generate_ai_insight(scores, reflections)
    st.markdown(f'<div class="insight-box">{ai_insight}</div>', unsafe_allow_html=True)

    # --- Personality Type ---
    def get_personality_type(scores):
        avg_values = sum([scores[opt]["Values Alignment"] for opt in scores]) / len(scores)
        avg_emotion = sum([scores[opt]["Emotional Resonance"] for opt in scores]) / len(scores)
        avg_risk = sum([scores[opt]["Risk Tolerance"] for opt in scores]) / len(scores)
        avg_vision = sum([scores[opt]["Long-Term Vision"] for opt in scores]) / len(scores)
        
        if avg_vision > 4:
            return "🚀 The Visionary"
        elif avg_emotion > 4:
            return "❤️ The Feelings Expert"
        elif avg_risk > 4:
            return "⚠️ The Risk-Taker"
        elif avg_values > 4:
            return "🌟 The Values Keeper"
        else:
            return "⚖️ The Balanced Thinker"

    personality = get_personality_type(scores)
    st.markdown(f'<div class="insight-box">🎭 Your Decision Personality: <b>{personality}</b></div>', unsafe_allow_html=True)

    # --- Step 7: Deep Reflection Report ---
    st.subheader("📖 Deep Reflection Report")
    for option in options:
        if option:
            st.markdown(f"### 📖 {option}")
            
            # Psychological
            st.write("🧠 **Psychological Insights:**")
            for aspect in aspects:
                why = reflections[option][aspect]["why"]
                if why:
                    st.write(f"- **{aspect}**: {scores[option][aspect]} — *{why}*")
            
            # Social
            social = reflections[option]["social"]
            if social["whose"]:
                st.write(f"👥 **Social Influence**: {social['influence']}/5 — *Influenced by {social['whose']}*")

            # Values
            vals = [v for v in reflections[option]["values"] if v]
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

    # --- Step 8: Save Decision ---
    decision_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "options": options,
        "aspects": aspects,
        "weights": weights,
        "scores": scores,
        "reflections": reflections,
        "results": results_df.to_dict(orient='records'),
        "mood": mood,
        "personality": personality,
        "ai_insight": ai_insight
    }

    # Save to session state
    if 'saved_decisions' not in st.session_state:
        st.session_state.saved_decisions = []
    st.session_state.saved_decisions.append(decision_data)

    # Export to CSV
    csv = results_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 Download Results as CSV",
        data=csv,
        file_name='decision_results.csv',
        mime='text/csv'
    )

    # Export to JSON
    json_str = json.dumps(decision_data, indent=2)
    b64_json = base64.b64encode(json_str.encode()).decode()
    href = f'<a href="data:file/json;base64,{b64_json}" download="decision_analysis.json">📥 Download Full Analysis (JSON)</a>'
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
                        if aspect in ref and 'why' in ref[aspect]:
                            st.write(f"- {aspect}: {ref[aspect]['why']}")
                    if 'social' in ref and ref['social']['whose']:
                        st.write(f"👥 Social: Influenced by {ref['social']['whose']}")
                    vals = [v for v in ref['values'] if v]
                    if vals:
                        st.write(f"🌟 Values: {', '.join(vals)}")
            
            st.write(f"🎭 Personality: {decision.get('personality', 'N/A')}")
            st.write(f"🤖 AI Insight: {decision.get('ai_insight', 'N/A')}")
            st.write(f"😊 Mood: {decision.get('mood', 'N/A')}")

# Footer
st.markdown("---")
st.caption("🧠 Use this tool to make decisions aligned with your core values and long-term vision.")
