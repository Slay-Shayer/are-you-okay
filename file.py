import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

# ===============================================================
# (A) CUSTOMIZABLE RESPONSE OPTIONS — YOU CAN EDIT THESE
# ===============================================================
CUSTOM_OPTIONS = {
    0: "Never",
    1: "Sometimes",
    2: "Often",
    3: "Almost Always",
}

# ===============================================================
# (B) CUSTOMIZABLE QUESTIONS — EDIT THIS LIST ONLY
# ===============================================================
CUSTOM_QUESTIONS = [
    ('S', "After an entire day of work, I cannot calm myself and unable see the beauty of life..."),
    ('A', "Even though I am not dehydrating, I feel my mouth getting all dried up. It feels parched, sticky and uncomfortable..."),
    ('D', "In a party full of people, I want to vibe around and enjoy the gathering just like others. Alas! I don't feel the energy even if I want to..."),
    ('A', "I feel suffocating, or unusually taking deep breaths, or often experience rapid breathing..."),
    ('D', "I want to start a hobby, or a business, or do better at my work to get the next promotion, or want to get better grades at school.\
        But before I initiate anything, I just give up..."),
    ('S', "Recently, I have been reacting too quick to any minor inconvenience. Afterwards, I regret of doing it because I know it's not who I am..."),
    ('A', "Shaky hands pisses me off! I have been doing that for quite a while, can't finish any of my work properly because of it!"),
    ('S', 'Small calculation, even while I am doing it with my fingers, makes me nervous. I am always worried about the inconvenient outcomes...'),
    ('A', 'Suppose, everything in my life is going according to my way, but still I panic about the bad situation I could fall into. This fear strikes me so badly...'), 
    ('D', 'I don\'t see any future for myself... All I see is darkness there... Hopes lost in void...'),
    ('S', 'My coworkers/classmates get the agitated attitude and restless behaviour from me, I don\'t do these intentionally...'),
    ('S', 'Cannot chill and relax at all, feel like losing patience too quickly...'),
    ('D', 'My spirit energy is so low that I always feel sad or melancholic...'),
    ('S', 'Either I am impatient or get distracted too easily from whatever I have on my hand. This is hampering my daily-to-daily task...'),
    ('A', 'Panic Attacks! I lose control over myself, my heart races too fast when it happens...'),  
    ('D', 'Almost nothing attracts me anymore. All those fun-times and hobbies died for me and abolished in the dull darkness...'), 
    ('D', "I feel worthless, I question my capabilities, feel pathetic about myself..."),
    ('S', 'I am emotionally fragile, too sensitive and get upset easily by minor comments and small actions/interruptions...'),
    ('A', 'During normal situations, my heart beat just goes up and gives me anxiety about things that never occurred...'),
    ('A', 'Things scare me no matter how small they are or even if they don\'t have any reason to do so...'), 
    ('D', 'Lost! Cannot find the meaning of life and going with the flow from zero expectations...'), 
]

# ===============================================================
# (C) DASS SEVERITY CUTOFFS (Keep As Is unless needed)
# ===============================================================
SEVERITY_CUTOFFS = {
    'd': [10, 14, 21, 28],
    'a': [8, 10, 15, 20],
    's': [15, 19, 26, 34],
}

def get_severity_label(score, subscale):
    cutoffs = SEVERITY_CUTOFFS[subscale]
    if score >= cutoffs[3]: return "Extremely Severe"
    elif score >= cutoffs[2]: return "Severe"
    elif score >= cutoffs[1]: return "Moderate"
    elif score >= cutoffs[0]: return "Mild"
    return "Normal"


# =====================================================================
# (D) PLACE TO INITIALIZE FIREBASE — CONNECT YOUR FIREBASE HERE
# =====================================================================
# NOTE:
# Uncomment this section and insert your Firebase credentials.

import firebase_admin
from firebase_admin import credentials, firestore


if not firebase_admin._apps:
    cred = credentials.Certificate("are-you-okay-f8cfd-firebase-adminsdk-fbsvc-1f7ae9b8d8.json")
    firebase_admin.initialize_app(cred, {
        "databaseURL": "https://are-you-okay-f8cfd-default-rtdb.asia-southeast1.firebasedatabase.app/"
    })


# =====================================================================
# HELPER — Generates Downloadable CSV
# =====================================================================
def generate_csv(df):
    return df.to_csv(index=False).encode('utf-8')


# =====================================================================
# HELPER — Creates Downloadable Chart Image
# =====================================================================
def generate_chart_image(df_scores):
    fig, ax = plt.subplots()

    ax.bar(df_scores["Scale"], df_scores["Score"], color = 'black')
    ax.set_ylabel("Score")
    ax.set_title("Your DASS Scale Scores")

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    return buf


# =====================================================================
# (E) STREAMLIT APP
# =====================================================================
def run_custom_dass():
    st.set_page_config(page_title="Are you okay?")

    st.title("Test your Depression, Anxiety and Stress level.")
    st.markdown("*Inspired by DASS 21*")

    option_labels = list(CUSTOM_OPTIONS.values())

    with st.form("custom_form"):
        st.subheader("Questions")

        responses = []

        for i, (scale, question) in enumerate(CUSTOM_QUESTIONS):
            st.write(f"### {i+1}. {question}")

            selected_label = st.radio(
                label="Choose your response:",
                options=option_labels,
                key=f"q{i}",
                horizontal=True
            )

            score = option_labels.index(selected_label)
            responses.append({"scale": scale, "score": score})
        st.markdown('*Click `Calculate Scores` to see Results.*')
        submitted = st.form_submit_button("Calculate Scores")

    if not submitted:
        return

    # ===========================================
    # Score calculation
    # ===========================================
    raw_d = sum(r["score"] for r in responses if r["scale"] == "D")
    raw_a = sum(r["score"] for r in responses if r["scale"] == "A")
    raw_s = sum(r["score"] for r in responses if r["scale"] == "S")

    d = raw_d * 2
    a = raw_a * 2
    s = raw_s * 2

    df_results = pd.DataFrame({
        "Scale": ["Depression", "Anxiety", "Stress"],
        "Score": [d, a, s],
        "Severity": [
            get_severity_label(d, 'd'),
            get_severity_label(a, 'a'),
            get_severity_label(s, 's')
        ]
    })

    st.subheader("Your Results")
    st.dataframe(df_results, hide_index=True)

    # =================================================================
    # 📊 Show Chart and make downloadable
    # =================================================================
    st.subheader("Graph")

    fig_buf = generate_chart_image(df_results)

    st.image(fig_buf, caption="Score Comparison Chart")

    st.download_button(
        label="📥 Download Chart as PNG",
        data=fig_buf,
        file_name="dass_chart.png",
        mime="image/png"
    )

    # =================================================================
    # 📥 CSV Download
    # =================================================================
    csv_data = generate_csv(df_results)
    st.download_button(
        label="📄 Download Results as CSV",
        data=csv_data,
        file_name="dass_results.csv",
        mime="text/csv"
    )




if __name__ == "__main__":
    run_custom_dass()










