import streamlit as st
import openai
import pandas as pd
import matplotlib.pyplot as plt
import io  # For handling in-memory file for download
from PIL import Image  # For displaying the saved image

# Show title and description.
st.title("💬 Chatbot with CSV Upload, Visualization, GPT Integration, and PNG Download")
st.write(
    "This is a chatbot that uses OpenAI's GPT-3.5 model to generate Python code for data visualization and allows you to download the generated plot as a PNG file."
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
        # Read CSV
        df = pd.read_csv(uploaded_file)
        st.write("CSV File loaded:")
        st.write(df.head())  # Display the first few rows of the file

        # Store the DataFrame in the session state for later use
        st.session_state["csv_data"] = df

        # Create a session state variable to store chat messages
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display existing chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Create a chat input field for the user to enter a message
        if prompt := st.chat_input("Ask about your data or request a graph (e.g., 'Plot a bar chart of column1 vs column2')..."):
            # Store and display the user's message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # If CSV data is uploaded, use it as part of the prompt
            if "csv_data" in st.session_state:
                csv_context = f"Here's a preview of the CSV data:\n{st.session_state['csv_data'].head().to_dict()}\n"
                prompt_with_data = f"{csv_context}\nUser request: {prompt}"
            else:
                prompt_with_data = prompt

            # Generate a response using the OpenAI API to create Python code
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that generates Python code for data visualization."},
                        {"role": "user", "content": prompt_with_data},
                    ]
                )

                generated_code = response['choices'][0]['message']['content']
                st.subheader("Generated Code:")
                st.code(generated_code, language="python")

                # Button to run the generated code
                if st.button("Run the generated code and save plot as PNG"):
                    try:
                        # Execute the generated code and save the plot as a PNG
                        exec(generated_code, globals())

                        # Save the plot to an in-memory file
                        buf = io.BytesIO()
                        plt.savefig(buf, format='png')
                        buf.seek(0)

                        # Convert the in-memory buffer to an image and display it
                        image = Image.open(buf)
                        st.image(image, caption="Generated Plot", use_column_width=True)

                        # Provide a download link for the PNG file
                        st.download_button(
                            label="Download plot as PNG",
                            data=buf,
                            file_name="generated_plot.png",
                            mime="image/png"
                        )

                    except Exception as e:
                        st.error(f"Error executing the code: {e}")

            except Exception as e:
                st.error(f"Error while generating response: {e}")
