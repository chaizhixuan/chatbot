import streamlit as st
import openai
import pandas as pd
import plotly.express as px

# Show title and description.
st.title("💬 GPT-Generated Code for CSV Visualization")
st.write(
    "This app allows you to upload a CSV, write a custom prompt, and have GPT-4 generate Python code for plotting. "
    "You can execute the generated code directly to visualize the data."
)

# Ask user for their OpenAI API key via `st.text_input`.
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    # Set the OpenAI API key
    openai.api_key = openai_api_key

    # Upload the CSV file
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    if uploaded_file is not None:
        # Try reading CSV with UTF-8 encoding, fallback to 'latin1' if necessary
        try:
            df = pd.read_csv(uploaded_file, encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(uploaded_file, encoding="latin1")

        st.write("CSV File loaded:")
        st.write(df.head())  # Display the first few rows of the file

        # Store the DataFrame in the session state for later use
        st.session_state["csv_data"] = df

        # Allow the user to input a custom prompt for GPT
        user_prompt = st.text_area(
            "Write your prompt for GPT to generate code for visualization (e.g., 'Write Python code to plot a bar chart using column1 and column2.')",
            height=100
        )

        # If the user has entered a prompt
        if user_prompt:
            # Display the prompt being sent to GPT
            st.write(f"User Prompt: {user_prompt}")

            try:
                # Generate a response using the OpenAI API (Updated for openai>=1.0.0)
                response = openai.Chat.create(
                    model="gpt-4",  # Use GPT-3.5-turbo or GPT-4
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": user_prompt},
                    ],
                    max_tokens=150,
                    temperature=0.5,
                )

                # Ensure response has expected structure
                if response and 'choices' in response and len(response['choices']) > 0:
                    # Get the generated code content from the response
                    generated_code = response['choices'][0]['message']['content']
                    st.subheader("Generated Code:")
                    st.code(generated_code, language="python")
                else:
                    st.error("Failed to get a valid response from OpenAI.")

            except Exception as e:
                st.error(f"Error while generating response: {e}")

            # Provide a button to execute the code
            if st.button("Run the generated code"):
                try:
                    # Execute the generated code safely
                    exec(generated_code)
                except Exception as e:
                    st.error(f"Error executing the code: {e}")
    else:
        st.write("Please upload a CSV file to proceed.")

    # Chatbot functionality
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display existing chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field for the user to enter a message
    if chat_prompt := st.chat_input("Ask anything..."):
        # Store and display the user's message
        st.session_state.messages.append({"role": "user", "content": chat_prompt})
        with st.chat_message("user"):
            st.markdown(chat_prompt)

        try:
            # Generate a response using the OpenAI API (Updated for openai>=1.0.0)
            stream = openai.Chat.create(
                model="gpt-4",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ] + [{"role": "user", "content": chat_prompt}],
                stream=True,
            )

            # Stream the response and store it in session state
            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})

        except Exception as e:
            st.error(f"Error while generating chat response: {e}")
