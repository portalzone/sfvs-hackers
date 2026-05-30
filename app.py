import streamlit as st
import time

st.set_page_config(page_title="Triage AI Assistant", page_icon="💬")
st.title("💬 Triage Escalation Assistant")
st.caption("Ask me about clinical cases, vitals analysis, or escalation rules.")

# 1. Initialize chat history in session state so it persists
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello Samuel! I can help you evaluate the synthetic triage dataset. Ask me to review a specific case or analyze vitals."}
    ]

# 2. Display existing messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. Accept user input
if user_query := st.chat_input("Type your message here..."):
    
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_query)
        
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_query})

    # 4. Generate assistant response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # --- PLACEHOLDER FOR YOUR TRIAGE AGENT LOGIC ---
        # This is where you can plug in your backend logic from agent.yaml or escalation_tool.py
        mock_response = f"I received your request: '{user_query}'. If you provide a Case ID, I can parse its vitals from the CSV and determine the CTAS priority level."
        # -----------------------------------------------
        
        # Simulate typing/streaming effect
        for chunk in mock_response.split(" "):
            full_response += chunk + " "
            time.sleep(0.05)
            response_placeholder.markdown(full_response + "▌")
            
        response_placeholder.markdown(full_response)
        
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})