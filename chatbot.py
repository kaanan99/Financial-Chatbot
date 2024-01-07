import streamlit as st
from transformers import pipeline
import torch
from utils import generate_context_text, get_chatbot_response

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
    st.session_state.pipeline = pipeline("text-generation", model="TinyLlama/TinyLlama-1.1B-Chat-v1.0", torch_dtype=torch.bfloat16, device_map="auto")


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

        model_input = [
            {
                "role": "system",
                "content": "You are a financial chatbot who is answer the users question as accurately. Try be conversational, concise, and work the question into the response. Use proper grammar in your response",
            },
        ]


        with st.chat_message("assistant"):
            st.markdown("Generating Response...")

        # Generate context for the model and add it to the message list
        print("Starting to generate context")
        context_texts = generate_context_text(query, 1)
        for text in context_texts:

            model_input.append(
                {
                    "role": "system",
                    "content": text,
                }
            )
        print("Finished generating context")
        
        # Add query to the message list
        user_query = {
            "role": "user",
            "content": query,
        }

        st.session_state.messages.append(user_query)
        model_input.append(user_query)

        # Generate Response
        print("Starting to Generate Model Response")
        model_prompt = st.session_state.pipeline.tokenizer.apply_chat_template(
            model_input, 
            tokenize=False, 
            add_generation_prompt=True,  
            max_length=2000,
            truncation=True
        )

        output = st.session_state.pipeline(
            model_prompt, 
            max_new_tokens=256, 
            do_sample=True, 
            temperature=0.7, 
            top_k=50, 
            top_p=0.95
        )
        print("Finished Generating Model Response")
        
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
    except:
        error_message = "I'm sorry, I had trouble understanding your query. Could you please try again?"

        with st.chat_message("assistant"):
            st.markdown(error_message)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": error_message,
            }
        )