"""Streamlit UI for the guideline-grounded clinical Q&A agent.

Run with: streamlit run app/app.py
"""

import streamlit as st

from qa import ask

st.set_page_config(page_title="Clinical Q&A Agent", page_icon="🩺")

st.title("🩺 Guideline-Grounded Clinical Q&A Agent")
st.caption(
    "Answers questions about adult hypertension screening and management, "
    "grounded in public WHO/USPSTF/CDC guideline documents."
)
st.warning(
    "**Informational only — not diagnostic or treatment advice.** "
    "This is a portfolio demo, not a deployable clinical tool."
)

with st.expander("What this can and can't answer"):
    st.markdown(
        "**Covered:** blood pressure thresholds for starting treatment, "
        "screening recommendations, and practice-level management strategies "
        "for adult hypertension — drawn from the WHO pharmacological "
        "treatment guideline, the USPSTF screening recommendation, and the "
        "CDC Million Hearts change package.\n\n"
        "**Declined by design:** hypertensive emergencies/urgencies, "
        "specific drug dosing, secondary/resistant hypertension, and "
        "anything else outside these three documents."
    )

question = st.text_input(
    "Ask a question",
    placeholder="e.g. What blood pressure threshold should trigger starting medication?",
)

if question:
    with st.spinner("Retrieving and generating an answer..."):
        result = ask(question)

    if result.declined:
        st.info(result.answer)
    else:
        st.markdown(result.answer)
        if result.citations:
            st.markdown("**Sources**")
            for i, citation in enumerate(result.citations, start=1):
                st.markdown(f"{i}. {citation}")
