import os
import sys
import streamlit as st
from agent import generate_workout_plan

# Ensure Streamlit sees the local directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def main():
    """Main function for the Streamlit UI."""
    st.set_page_config(page_title="AI Strength Coach", page_icon="🏋️")

    st.title("🏋️ AI Personal Trainer")
    st.subheader("Your Intelligent Workout Agent")

    # Step 1: Select Workout Category
    category = st.selectbox(
        "What do you want to train today?",
        ["Upper", "Lower", "Full Body"]
    )

    # Step 2: Generate Workout
    if st.button("Generate My Workout"):
        with st.spinner("Coach is thinking..."):
            workout = generate_workout_plan(category)
            st.success(f"Here is your {category} workout!")
            st.markdown(workout)

    # Step 3: Logging Session
    st.divider()
    st.write("### Log Your Session")

    with st.form("log_form"):
        ex_name = st.text_input("Exercise Name (e.g., Bench Press)")
        reps = st.number_input("Reps Performed", min_value=0, value=10)
        weight = st.number_input("Weight Used (kg)", min_value=0.0, value=20.0)
        target = 10

        if st.form_submit_button("Submit & Analyse"):
            # These now match the renamed 'agent.py'
            from agent import analyze_performance
            from database import update_weight

            new_weight = analyze_performance(ex_name, reps, target, weight)
            update_weight(ex_name, new_weight)

            if new_weight > weight:
                st.balloons()
                st.success(f"Goal hit! Next session weight: {new_weight}kg")
            else:
                st.warning(f"Stay at {new_weight}kg for now.")


if __name__ == "__main__":
    main()
