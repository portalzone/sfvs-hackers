import streamlit as st
import time
import os

# 1. Import your backend tools directly
from tools.escalation_tool import analyze_triage_note

# 2. Pure Python .env loader (No 'import dotenv' needed!)
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        for line in f:
            # Clean up line and skip comments or empty lines
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                # Strip spaces and potential quotes around the value
                os.environ[key.strip()] = value.strip().strip('"').strip("'")

st.set_page_config(page_title="Triage AI Assistant", page_icon="💬")
st.title("💬 Triage Escalation Assistant")
st.caption("Ask me about clinical cases, vitals analysis, or escalation rules.")

# Safeguard check to ensure your keys are now loaded in the environment
if not os.getenv("WATSONX_API_KEY"):
    st.sidebar.warning("⚠ WATSONX_API_KEY not found in parent .env file.")

# Initialize chat history in session state so it persists
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello Samuel! I can help you evaluate the synthetic triage dataset. Ask me to review a specific case or analyze vitals."}
    ]

# Display existing messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if user_query := st.chat_input("Type your message here..."):
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_query)
        
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Generate assistant response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        with st.spinner("Analyzing presentation text..."):
            try:
                # 3. Call your live backend engine
                result = analyze_triage_note(
                    note=user_query,
                    hr=80, sbp=120, dbp=80, rr=16, o2=98.0, temp=36.8
                )
                
                # 4. Format the backend dictionary payload into a clean Markdown response
                flag_emoji = "🚨" if result.get('escalation_flag') == "YES" else "✅"
                
                live_response = f"""### {flag_emoji} Analysis Verdict: {result.get('escalation_flag', 'UNKNOWN')}
* **Estimated Acuity:** `{result.get('acuity_estimate', 'N/A')}`
* **Identified Risk Signals:** *{result.get('risk_signals', 'None flagged')}*

#### 📋 Recommended Action Plan
{result.get('recommended_action', 'Follow standard protocols.')}

#### 🧠 Clinical Reasoning
{result.get('reasoning', 'No structural breakdown provided.')}"""

            except Exception as e:
                live_response = f"❌ **Backend Processing Error:** {str(e)}"
        
        # 5. Simulate the typing/streaming effect
        for chunk in live_response.split(" "):
            full_response += chunk + " "
            time.sleep(0.03)
            response_placeholder.markdown(full_response + "▌")
            
        response_placeholder.markdown(full_response)
        
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})