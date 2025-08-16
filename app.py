# enhanced_decision_app.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Enhanced Decision Alignment Helper", layout="centered")
st.title("🧭 Enhanced Decision Alignment Helper")
st.write("Rate options across aspects, assign weights, save past decisions, and compare visually.")

# --- Step 1: Input Options ---
num_options = st.number_input("How many options do you want to evaluate?", min_value=1, step=1)
options = []
for i in range(num_options):
    option_name = st.text_input(f"Enter name for Option {i+1}", key=f"option_{i}")
    options.append(option_name)

# --- Step 2: Define Aspects and Weights ---
aspects = ["Values Alignment", "Long-Term Vision", "Emotional Resonance", 
           "Impact on Others & System", "Risk Tolerance", "Intuition"]

st.subheader("Set importance (weights) for each aspect (1 = low, 5 = high)")
weights = {}
for aspect in aspects:
    weights[aspect] = st.slider(f"{aspect} Weight", 1, 5, 3, key=f"weight_{aspect}")

# --- Step 3: Evaluate Options ---
st.subheader("Rate each option (1-5)")
scores = {}
for option in options:
    if option:
        scores[option] = {}
        st.markdown(f"**{option}**")
        for aspect in aspects:
            score = st.slider(f"{aspect}", 1, 5, 3, key=f"{option}_{aspect}")
            scores[option][aspect] = score

# --- Step 4: Compute Weighted Scores and Show Results ---
if st.button("Compute Scores & Recommend"):
    results = []
    for option, option_scores in scores.items():
        weighted_total = sum(option_scores[a]*weights[a] for a in aspects)
        results.append({"Option": option, "Total Score": weighted_total})
    results_df = pd.DataFrame(results).sort_values(by="Total Score", ascending=False)
    
    st.subheader("✅ Weighted Decision Scores")
    st.dataframe(results_df.reset_index(drop=True))
    
    best_option = results_df.iloc[0]["Option"]
    st.success(f"🎯 Recommended Option (Highest Alignment): {best_option}")
    
    # --- Step 5: Visual Comparison ---
    st.subheader("📊 Visual Comparison")
    chart_df = pd.DataFrame(scores).T
    chart_df_weighted = chart_df.multiply(pd.Series(weights))
    st.bar_chart(chart_df_weighted)

    # --- Step 6: Save Decision ---
    csv = results_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="💾 Download Decision Data as CSV",
        data=csv,
        file_name='decision_scores.csv',
        mime='text/csv'
    )
