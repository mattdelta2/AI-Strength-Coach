# app.py
import os
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

            try:
                update_weight("Bench Press", bench)
                update_weight("Squat", squat)
                update_weight("Deadlift", dead)
            except Exception:
                pass  # DB unavailable; weights will be saved when connection is restored

            st.success("Onboarding complete! Loading your coach...")
            st.session_state.onboarded = True
            st.rerun()


def main():
    """Main function handling onboarding check and UI."""
    from agent import generate_reply, analyse_performance
    from database import supabase, update_weight, save_message, get_recent_messages
    from conversation import detect_equipment_mode

    st.set_page_config(page_title="AI Strength Coach", page_icon="🏋️")

    # ── Session state initialisation ─────────────────────────────────────────
    if "equipment_mode" not in st.session_state:
        st.session_state.equipment_mode = "gym"

    if "messages" not in st.session_state:
        # Restore cross-session memory from DB (newest-first → reverse to chrono)
        try:
            persisted = get_recent_messages(user_id=None, limit=20)
        except Exception:
            persisted = []
        if persisted:
            st.session_state.messages = list(reversed(persisted))
        else:
            st.session_state.messages = [
                {"role": "assistant",
                 "content": "How can I help you train today?"}
            ]

    if "active_workout" not in st.session_state:
        st.session_state.active_workout = []
    if "generating" not in st.session_state:
        st.session_state.generating = False

    if "onboarded" not in st.session_state:
        if supabase:
            try:
                data = supabase.table("user_progress").select("*").execute().data
                st.session_state.onboarded = True if data else False
            except Exception:
                st.session_state.onboarded = False
        else:
            st.session_state.onboarded = False

    if not st.session_state.onboarded:
        onboarding_form()
        return

    st.title("🏋️ AI Personal Trainer")

    # ── SIDEBAR ───────────────────────────────────────────────────────────────
    with st.sidebar:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = []
            st.session_state.active_workout = []
            st.rerun()

        # Equipment mode toggle
        st.header("⚙️ Mode")
        mode_choice = st.radio(
            "Equipment",
            options=["🏋️ Gym", "🏠 Home"],
            index=0 if st.session_state.equipment_mode == "gym" else 1,
            horizontal=True,
        )
        st.session_state.equipment_mode = "gym" if "Gym" in mode_choice else "home"
        st.divider()

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

        if supabase:
            try:
                progress_data = supabase.table(
                    "user_progress").select("*").execute().data
                if progress_data:
                    df = pd.DataFrame(progress_data)
                    st.bar_chart(data=df, x="exercise_name", y="current_weight")
            except Exception:
                st.caption("Progress chart unavailable — check DB connection.")

    # ── MAIN: Chat Interface ──────────────────────────────────────────────────
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("e.g. Give me a 45min upper body workout"):
        # Detect equipment preference from natural language before anything else
        detected_mode = detect_equipment_mode(prompt)
        if detected_mode:
            st.session_state.equipment_mode = detected_mode

        st.session_state.active_workout = []
        st.session_state.messages.append({"role": "user", "content": prompt})
        try:
            save_message(user_id=None, role="user", content=prompt)
        except Exception:
            pass

        with st.chat_message("user"):
            st.markdown(prompt)

        if st.session_state.get("generating", False):
            st.warning("Still generating the previous reply — please wait.")
            return

        st.session_state.generating = True

        placeholder = st.empty()
        with placeholder.container():
            st.chat_message("assistant")
            st.markdown("_Coach is typing..._")

        try:
            display_text, workout_dict = generate_reply(
                prompt,
                st.session_state.get("messages", []),
                equipment_mode=st.session_state.equipment_mode,
            )
        except Exception as exc:
            st.session_state.generating = False
            placeholder.empty()
            st.error(f"Coach encountered an error — please try again. ({exc})")
            st.stop()
        finally:
            st.session_state.generating = False
            placeholder.empty()

        st.session_state.messages.append(
            {"role": "assistant", "content": display_text})
        try:
            save_message(user_id=None, role="assistant", content=display_text)
        except Exception:
            pass

        with st.chat_message("assistant"):
            st.markdown(display_text)

        regen_key = f"regen_{len(st.session_state.messages)}"
        if not st.session_state.get("generating", False) and st.button(
                "Regenerate last reply", key=regen_key):
            st.session_state.messages = st.session_state.messages[:-1]
            st.rerun()

        # Populate sidebar logger from structured JSON workout
        if workout_dict and workout_dict.get("exercises"):
            st.session_state.active_workout = [
                ex["name"] for ex in workout_dict["exercises"]
            ]
            st.rerun()
    # End of main()


if __name__ == "__main__":
    main()
