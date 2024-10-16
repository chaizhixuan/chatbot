import streamlit as st
from openai import OpenAI
import pandas as pd
import numpy as np
import plotly.express as px
import json

# Show title and description.
st.title("💬 Chatbot with CSV Upload and Visualization")
st.write(
    "This is a simple chatbot that uses OpenAI's GPT-3.5 model to generate responses. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys)."
)

# Ask user for their OpenAI API key via `st.text_input`.
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Upload the file
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    if uploaded_file is not None:
        # Read CSV
        df = pd.read_csv(uploaded_file)
        st.write("CSV File loaded:")
        st.write(df.head())  # Display the first few rows of the file

        # Store the DataFrame in the session state for later use
        st.session_state["csv_data"] = df.to_dict()

    # Create a session state variable to store chat messages
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display existing chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field for the user to enter a message
    if prompt := st.chat_input("Ask about your data or anything else..."):
        # Store and display the user's message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # If CSV data is uploaded, use it as part of the prompt
        if "csv_data" in st.session_state:
            csv_context = f"Here's the CSV data:\n{st.session_state['csv_data']}\n"
            prompt_with_data = f"{csv_context}\nUser question: {prompt}"
        else:
            prompt_with_data = prompt

        # Generate a response using the OpenAI API
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ] + [{"role": "user", "content": prompt_with_data}],
            stream=True,
        )

        # Stream the response and store it in session state
        with st.chat_message("assistant"):
            response_text = st.write_stream(stream)

        st.session_state.messages.append({"role": "assistant", "content": response_text})

        # Check if the response contains code to generate a plot
        try:
            response_data = json.loads(response_text)
            if 'code' in response_data and response_data['code']:
                st.code(response_data['code'])
                exec(response_data['code'])
        except Exception as e:
            st.error(f"Failed to parse response: {e}")

        # If no code generated, simply show the response as text
        if isinstance(response_text, str):
            st.session_state.messages.append({"role": "assistant", "content": response_text})

# Example data visualization function that could be generated from AI response
def plot_example(df):
    if 'time_spend_company' in df.columns and 'satisfaction_level' in df.columns:
        fig = px.line(df, x='time_spend_company', y='satisfaction_level', title='Satisfaction vs Time Spent in Company')
        st.plotly_chart(fig)

# Call this visualization function if the appropriate columns exist in the uploaded CSV
if 'csv_data' in st.session_state:
    df = pd.DataFrame(st.session_state['csv_data'])
    plot_example(df)
