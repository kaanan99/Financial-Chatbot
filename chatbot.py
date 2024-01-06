import streamlit as st
from utils import create_chatbot_pipeline, generate_chatbot_output

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
            "role": "assistant",
            "content": initialization_message,
        }
    )

#  Initial Chatbot pipeline object
if "pipeline" not in st.session_state:
    model_name = "deepset/roberta-base-squad2"
    st.session_state.pipeline = create_chatbot_pipeline(model_name)


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

query = st.chat_input("Enter query here:")


if query:

    # Display Query
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.messages.append(
        {
            "role": "user",
            "content": query,
        }
    )

    try:
        # Generate and display chaty bot resposne
        chatbot_response = generate_chatbot_output(query, st.session_state.pipeline)
        with st.chat_message("assistant"):
            st.markdown(chatbot_response)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": chatbot_response,
            }
        )
    
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