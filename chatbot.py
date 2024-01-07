import streamlit as st
import transformers
import torch

from transformers import pipeline
from utils import generate_context_text, get_chatbot_response, generate_model_input

st.title("Financial Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    # Create list to store past messages
    st.session_state.messages = []

    initialization_message = """
    Hello! I am a financial chatbot who uses marketwatch.com to try and answer your financial questions. 
    It may take me some time to generate a response so please be patient!
    """
    st.session_state.messages.append(
        {
            "role": "system",
            "content": "You are a financial chatbot who is answer the users question as accurately. Try to use details, be conversational, and work the question into the response",
        }
    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": initialization_message,
        }
    )

#  Initial Chatbot pipeline object
if "pipeline" not in st.session_state:
    try:
        st.session_state.pipeline = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", torch_dtype=torch.bfloat16, device_map="auto")
    except:
        st.session_state.pipeline = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", device_map="auto")


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

query = st.chat_input("Enter query here:")


if query:

    # Display Query
    with st.chat_message("user"):
        st.markdown(query)

    try:


        print(f"\nQuerying: {query}")

        with st.chat_message("assistant"):
            st.markdown("Generating Response...")

        # Generate context for the model and add it to the message list
        print("\tStarting to generate context")
        context_text = generate_context_text(query, 2)
        print("\tFinished generating context")
        
        # Generate model input
        model_input = generate_model_input(st.session_state.pipeline.tokenizer, query, context_text)

        # Add query to the message list
        user_query = model_input[-1]
        st.session_state.messages.append(user_query)

        # Generate Response
        print("\tStarting to Generate Model Response")
        model_prompt = st.session_state.pipeline.tokenizer.apply_chat_template(
            model_input, 
            tokenize=False, 
            add_generation_prompt=True,  
        )

        output = st.session_state.pipeline(
            model_prompt, 
            max_new_tokens=256, 
            do_sample=True, 
            temperature=0.7, 
            top_k=50, 
            top_p=0.95
        )
        print("\tFinished Generating Model Response")
        
        chatbot_response = get_chatbot_response(output)

        # Display response
        with st.chat_message("assistant"):
            st.markdown(chatbot_response)

        # Add response to message history
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": chatbot_response,
            }
        )

    # If there is an error in the users query
    except Exception as e:
        error_message = f"I'm sorry, there was an error generating your. Could you please try again? Here is the error message: {e}"

        with st.chat_message("assistant"):
            st.markdown(error_message)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": error_message,
            }
        )