import os
import re
import sys

import pandas as pd
import streamlit as st

from agent import generate_workout_plan


# Ensure Streamlit sees the local directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def onboarding_form():
    """Collect initial strength data to calibrate the AI Agent."""
    st.title("🏋️ Welcome to AI Coach")
    st.subheader("Let's calibrate your starting weights")

    with st.form("onboarding_form"):
        st.write("Enter your current working weights for the 'Big 3':")
        col1, col2, col3 = st.columns(3)
        bench = col1.number_input(
            "Bench Press (kg)", min_value=0.0, value=40.0)
        squat = col2.number_input("Squat (kg)", min_value=0.0, value=60.0)
        dead = col3.number_input("Deadlift (kg)", min_value=0.0, value=80.0)

        if st.form_submit_button("Complete Onboarding"):
            from database import update_weight
            update_weight("Bench Press", bench)
            update_weight("Squat", squat)
            update_weight("Deadlift", dead)

            st.success("Onboarding complete! Loading your coach...")
            st.session_state.onboarded = True
            st.rerun()


def main():
    """Main function handling onboarding check and UI."""
    st.set_page_config(page_title="AI Strength Coach", page_icon="🏋️")

    if "onboarded" not in st.session_state:
        from database import supabase
        data = supabase.table("user_progress").select("*").execute().data
        st.session_state.onboarded = True if data else False

    if not st.session_state.onboarded:
        onboarding_form()
        return

    st.title("🏋️ AI Personal Trainer")

    # --- SIDEBAR: Logging & Analytics ---
    with st.sidebar:
        # Professional Reset Button to handle Context Drift
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.session_state.active_workout = []
            st.rerun()

        st.header("📋 Log Your Session")

        active_exercises = st.session_state.get("active_workout", [])

        if not active_exercises:
            st.info("Ask for a workout to start logging!")
        else:
            for ex in active_exercises:
                with st.expander(f"Log {ex}", expanded=True):
                    reps = st.number_input(
                        "Reps", min_value=0, value=10, key=f"reps_{ex}"
                    )
                    weight = st.number_input(
                        "Weight (kg)", min_value=0.0,
                        value=20.0, key=f"weight_{ex}"
                    )

                    if st.button(f"Submit {ex}", key=f"btn_{ex}"):
                        from agent import analyze_performance
                        from database import update_weight

                        new_w = analyze_performance(ex, reps, 10, weight)
                        update_weight(ex, new_w)

                        if new_w > weight:
                            st.toast(f"💪 {ex} increased to {new_w}kg!")
                        else:
                            st.toast(f"✅ {ex} session logged.")

        st.divider()
        st.header("📈 Your Progress")
        from database import supabase
        progress_data = (
            supabase.table("user_progress").select("*").execute().data
        )

        if progress_data:
            df = pd.DataFrame(progress_data)
            st.bar_chart(data=df, x="exercise_name", y="current_weight")

    # --- MAIN: Chat Interface ---
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "How can I help you train today?"}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("e.g. Give me a 45min upper body workout"):
        st.session_state.active_workout = []
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Coach is thinking..."):
                full_response = generate_workout_plan(prompt)

                # 1. STRIP the hidden technical tags so the user doesn't see them
                clean_display = re.sub(r"<!--.*?-->", "", full_response).strip()
                # Also remove raw EXERCISES text if AI forgot the comment tags
                clean_display = re.sub(
                    r"EXERCISES:.*", "", clean_display, flags=re.IGNORECASE
                ).strip()

                # 2. SAVE and DISPLAY the clean version
                st.session_state.messages.append(
                    {"role": "assistant", "content": clean_display}
                )
                st.markdown(clean_display)

                # 3. USE the technical response for extraction logic
                pattern = r"EXERCISES:\s*(.*?)(?:\s*-->|$)"
                match = re.search(pattern, full_response, re.IGNORECASE)

                if match:
                    names_str = match.group(1).strip().strip("[]")
                    names_list = [
                        n.strip().strip("'\"") for n in names_str.split(",")
                        if n.strip()
                    ]

                    if names_list:
                        st.session_state.active_workout = names_list
                        st.rerun()


if __name__ == "__main__":
    main()
