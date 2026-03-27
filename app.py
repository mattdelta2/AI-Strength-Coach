# app.py
import os
import re
import sys

import pandas as pd
import streamlit as st

# Ensure Streamlit sees the local directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Local imports are performed inside main() to avoid E402 lint errors
# and to ensure sys.path has been set before importing local modules.


def onboarding_form():
    """Collect initial strength data to calibrate the AI Coach."""
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
    # Local imports after sys.path append to satisfy linters and avoid E402
    from agent import generate_reply, analyse_performance
    from database import supabase, update_weight

    st.set_page_config(page_title="AI Strength Coach", page_icon="🏋️")

    # Defensive initialisation of session state keys
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "How can I help you train today?"}
        ]
    if "active_workout" not in st.session_state:
        st.session_state.active_workout = []
    if "generating" not in st.session_state:
        st.session_state.generating = False

    if "onboarded" not in st.session_state:
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
                        # Use the analyse_performance function from agent.py
                        new_w = analyse_performance(ex, reps, 10, weight)
                        update_weight(ex, new_w)

                        if new_w > weight:
                            try:
                                st.toast(f"💪 {ex} increased to {new_w}kg!")
                            except Exception:
                                st.success(f"💪 {ex} increased to {new_w}kg!")
                        else:
                            try:
                                st.toast(f"✅ {ex} session logged.")
                            except Exception:
                                st.info(f"✅ {ex} session logged.")

        st.divider()
        st.header("📈 Your Progress")

        progress_data = supabase.table(
            "user_progress").select("*").execute().data

        if progress_data:
            df = pd.DataFrame(progress_data)
            st.bar_chart(data=df, x="exercise_name", y="current_weight")

    # --- MAIN: Chat Interface ---
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("e.g. Give me a 45min upper body workout"):
        # Reset active workout until we parse a new one
        st.session_state.active_workout = []
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Prevent concurrent generations
        if st.session_state.get("generating", False):
            st.warning("Still generating the previous reply — please wait.")
            return

        st.session_state.generating = True

        # Show a typing placeholder while the model generates a reply
        placeholder = st.empty()
        with placeholder.container():
            st.chat_message("assistant")
            st.markdown("_Coach is typing..._")

        try:
            # Generate reply using the conversation-aware wrapper
            full_response = generate_reply(
                prompt, st.session_state.get("messages", []))
        finally:
            st.session_state.generating = False
            placeholder.empty()

        # 1. STRIP the hidden technical tags so the user doesn't see them
        clean_display = re.sub(r"<!--.*?-->", "", full_response).strip()
        # Also remove raw EXERCISES text if AI forgot the comment tags
        clean_display = re.sub(
            r"EXERCISES:.*", "", clean_display, flags=re.IGNORECASE).strip()

        # 2. SAVE and DISPLAY the clean version
        st.session_state.messages.append(
            {"role": "assistant", "content": clean_display})
        with st.chat_message("assistant"):
            st.markdown(clean_display)

        # Small regenerate control for the last assistant reply
        regen_key = f"regen_{len(st.session_state.messages)}"
        if not st.session_state.get("generating", False) and st.button(
                "Regenerate last reply", key=regen_key):
            # Remove last assistant message and re-run generation
            st.session_state.messages = st.session_state.messages[:-1]
            st.rerun()

        # 3. USE the technical response for extraction logic (robust pattern)
        pattern = r"<!--\s*EXERCISES\s*:\s*(\[[^\]]*\])\s*-->"
        match = re.search(pattern, full_response, re.IGNORECASE)

        if match:
            names_str = match.group(1).strip().lstrip("[").rstrip("]")
            names_list = [
                n.strip().strip("'\"") for n in names_str.split(
                    ",") if n.strip()]

            if names_list:
                st.session_state.active_workout = names_list
                # Immediately rerun so the sidebar shows the new logging UI
                st.rerun()
    # End of main()


if __name__ == "__main__":
    main()
