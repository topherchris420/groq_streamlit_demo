import streamlit as st
from typing import Generator
from groq import Groq
import os
from typing import Optional, Dict, Union

def _get_system_prompt() -> str:
    """Get system prompt from a file."""
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "system_prompt.txt")
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

system_prompt = _get_system_prompt()

st.set_page_config(page_icon="coast_chris.png", layout="wide", page_title="Vers3Dynamics")

def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(f'<span style="font-size: 78px; line-height: 1">{emoji}</span>', unsafe_allow_html=True)

icon("🐶")
st.markdown('<a href="https://christopher.streamlit.app/" style="text-decoration:none; color: #00C6C3;"><h2>Vers3Dynamics</h2></a>', unsafe_allow_html=True)
st.subheader("Meet Your FurBuddy, Powered by Groq 🚀")

# Add a picture with a caption
st.image("images/WelcomeHometitle.png", caption="Woof woof!", width=200)

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Initialize chat history and selected model
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_model" not in st.session_state:
    st.session_state.selected_model = None

# Define model details
models = {
    "gemma-7b-it": {"name": "Gemma-7b-it", "tokens": 8192, "developer": "Google"},
    "llama2-70b-4096": {"name": "LLaMA2-70b-chat", "tokens": 4096, "developer": "Meta"},
    "llama3-70b-8192": {"name": "LLaMA3-70b-8192", "tokens": 8192, "developer": "Meta"},
    "llama3-8b-8192": {"name": "LLaMA3-8b-8192", "tokens": 8192, "developer": "Meta"},
    "mixtral-8x7b-32768": {"name": "Mixtral-8x7b-Instruct-v0.1", "tokens": 32768, "developer": "Mistral"},
}

# Layout for model selection and max_tokens slider
col1, col2 = st.columns(2)

with col1:
    model_option = st.selectbox(
        "Connect with the perfect AI:",
        options=list(models.keys()),
        format_func=lambda x: models[x]["name"],
        index=2  # Default to LLaMA
    )

# Detect model change and clear chat history if model has changed
if st.session_state.selected_model != model_option:
    st.session_state.messages = []
    st.session_state.selected_model = model_option

max_tokens_range = models[model_option]["tokens"]

with col2:
    max_tokens = st.slider(
        "Max Tokens 🪙:",
        min_value=512,
        max_value=max_tokens_range,
        value=min(32768, max_tokens_range),
        step=512,
        help=f"Adjust the maximum number of tokens for the model's response. Max for selected model: {max_tokens_range}"
    )

# Process the user's input and respond accordingly
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

if st.session_state.user_input:
    st.session_state.messages.append({"role": "user", "content": st.session_state.user_input})

    try:
        chat_completion = client.chat.completions.create(
            model=model_option,
            messages=st.session_state.messages,
            max_tokens=max_tokens,
            stream=True
        )

        # Use the generator function with st.write_stream
        with st.chat_message("assistant", avatar="🐶"):
            chat_responses_generator = generate_chat_responses(chat_completion)
            full_response = st.write_stream(chat_responses_generator)
    except Exception as e:
        st.error(f"Oops! Something went wrong: {e}", icon="🐢🚨")

    # Append the full response to session_state.messages
    if isinstance(full_response, str):
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    else:
        combined_response = "\n".join(str(item) for item in full_response)
        st.session_state.messages.append({"role": "assistant", "content": combined_response})
