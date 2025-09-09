# enhanced_decision_app_v2.py
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
        background-color: #0a0a0a;
        color: #e0e0e0;
    }
    .stSlider > div {
        background-color: #1a1a1a;
    }
    .stButton button {
        background-color: #007bff;
        color: white;
        border-radius: 8px;
    }
    .stButton button:hover {
        background-color: #0056b3;
    }
    .insight-box {
        background-color: #1c1c1c;
        padding: 15px;
        border-left: 4px solid #007bff;
        margin: 15px 0;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

# Title & Description
st.title("🧭 Enhanced Decision Alignment Helper")
st.write("Rate options across aspects, assign weights, save past decisions, and compare visually.")

# --- Sidebar: Settings ---
with st.sidebar:
    st.header("⚙️ Settings")
    use_custom_aspects = st.checkbox("Use custom aspects?", value=False)
    show_notes = st.checkbox("Show notes for each option", value=False)
    dark_mode = st.checkbox("Dark Mode", value=True)
    if dark_mode:
        st.markdown("<style>body {background-color: #0a0a0a; color: #e0e0e0;}</style>", unsafe_allow_html=True)

# --- Step 1: Input Options ---
num_options = st.number_input("How many options do you want to evaluate?", min_value=1, max_value=10, step=1, value=2)
options = []
for i in range(num_options):
    option_name = st.text_input(f"Enter name for Option {i+1}", key=f"option_{i}")
    options.append(option_name)

# --- Step 2: Define Aspects ---
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

# Set weights
st.subheader("🎯 Set importance (weights) for each aspect (1 = low, 5 = high)")
weights = {}
for aspect in aspects:
    weights[aspect] = st.slider(f"{aspect} Weight", 1, 5, 3, key=f"weight_{aspect}")

# --- Step 3: Evaluate Options with Notes ---
st.subheader("📊 Rate each option (1–5)")
scores = {}
notes = {}  # Store user notes
for option in options:
    if option:
        scores[option] = {}
        notes[option] = ""
        st.markdown(f"### {option}")
        for aspect in aspects:
            score = st.slider(f"{aspect}", 1, 5, 3, key=f"{option}_{aspect}")
            scores[option][aspect] = score
        if show_notes:
            notes[option] = st.text_area(f"📝 Notes for {option}", key=f"note_{option}")

# --- Step 4: Compute Scores & Show Results ---
if st.button("✅ Compute Scores & Recommend"):
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
    chart_data['Category'] = chart_data.index
    fig = px.line_polar(chart_data, r=chart_data.columns[:-1], theta=chart_data.columns[:-1], line_close=True, title="Radar Chart of Options")
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

    # --- Step 7: Save Decision ---
    decision_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "options": options,
        "aspects": aspects,
        "weights": weights,
        "scores": scores,
        "notes": notes,
        "results": results_df.to_dict(orient='records')
    }

    # Save to session state (can be expanded to local file later)
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

# --- Step 8: Load Saved Decisions ---
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
            if decision['notes']:
                st.write("**Notes:**", decision['notes'])

# Footer
st.markdown("---")
st.caption("🧠 Use this tool to make decisions aligned with your core values and long-term vision.")
