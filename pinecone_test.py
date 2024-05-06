import streamlit as st
import pandas as pd
from pinecone import Pinecone
from openai import OpenAI
import os, requests
from dotenv import load_dotenv
import threading
import time
# Load .env variables
load_dotenv()

# Get Pinecone and OpenAI API keys
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.environ.get("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


def make_api_request(text_input, context, response_placeholder):
    try:
        # Make API request
        response = requests.post(
            "http://localhost:8090/analyze",
            headers={"accept": "*/*", "Content-Type": "application/json"},
            json={"search_parameter": text_input, "context": context},
        )
        # Update the response placeholder with the API response
        response_placeholder.markdown(f"##### Why is it relevant? :\n{response.json()}")
    except Exception as e:
        st.error(f"Error: {e}")


# Function to generate embeddings
def generate_embedding(text):
    # Replace 'YOUR_API_KEY' with your OpenAI API key
    client = OpenAI()

    # Call the OpenAI API to generate embeddings
    response = client.embeddings.create(
        model="text-embedding-ada-002", input=[text], encoding_format="float"
    )

    # Return the embedding
    return response.data[0].embedding


# Main function for Streamlit app
def main():
    st.set_page_config(page_title="Pinecone Search Demo")
    st.title("🔍 Pinecone Search Enhanced Demo")
    st.write("📝 Enter a text below and click on 'Search' to find similar items.")

    # Text input for user
    text_input = st.text_area("✍️ Enter text:")

    # Search button
    if st.button("🔍 Search"):
        # Generate embedding for input text
        msg = st.toast("Making embeddings for the text...  🍳")
        time.sleep(1)
        msg = st.toast('Connecting to Pinecone...  🌲')
        embedding = generate_embedding(text_input)
        
        pc = Pinecone(api_key=PINECONE_API_KEY)
        pc_index = pc.Index(PINECONE_INDEX_NAME)
        msg = st.toast('Connected!  🌲')
        time.sleep(1)
        msg.toast('Searching...  🕵️‍♂️')
        with st.spinner("Searching...  🕵️‍♂️"):
            results = pc_index.query(
            namespace="test-3rd",
            vector=embedding,
            include_metadata=True,
            top_k=10,
            )
        time.sleep(1)
        msg.toast('Fetching Results!', icon = "🎉")
        # Perform search
        
        st.success("Search completed! 🎉")
        st.balloons()

        # Display search results
        st.write("## 🔎 Search Results:")

        # Custom CSS styles
        st.markdown(
            """
            <style>
                .big-card {
                    background-color: #f8f8f8;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 16px;
                    margin-bottom: 16px;
                }
                .result-card {
                    background-color: #ffffff;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 16px;
                    margin-bottom: 16px;
                }
                .result-title {
                    font-size: 18px;
                    font-weight: bold;
                    color: #333;
                    margin-bottom: 8px;
                }
                .result-info {
                    font-size: 14px;
                    color: #666;
                    margin-bottom: 4px;
                }
                .result-link {
                    font-size: 14px;
                    color: #0078e7;
                }
                .api-response {
                    font-size: 14px;
                    color: #666;
                    margin-top: 16px;
                    background-color: #f0f0f0;
                    border-radius: 4px;
                    padding: 8px;
                }
                
                </style>
                """,
            unsafe_allow_html=True,
        )

        # Display each search result in a big card format
        for idx, result in enumerate(results["matches"]):
            metadata = result["metadata"]
            with st.container():
                

                





                context = (
                    metadata.get("text", "")
                    .replace("'", "")
                    .replace('"', "")
                    .replace("\n", "")
                )

                try:

                    
                    

                    st.markdown(
                        f"""
                            <div class="big-card">
                                <div class="result-card">
                                    <div class="result-title">📄 {metadata["name"]}</div>
                                    <div class="result-info">📋 Case Code: {metadata["case_code"]}</div>
                                    <div class="result-info">🏛️ District: {", ".join(metadata["district"])}</div>
                                    <div class="result-info">⚖️ Decision: {metadata["decision"]}</div>
                                    <div class="result-info">🔗 <a class="result-link" href="{metadata["file_link"]}" target="_blank">View PDF</a></div>
                                </div>
                            </div>
                            """,
                        unsafe_allow_html=True,
                    )
                    st.write("#### 📄 Text:")
                    with st.expander("📋 View Text"):
                        st.markdown(
                            f'📋 {metadata["text"]}'
                        )

                    response = requests.post(
                        "http://localhost:8090/analyze",
                        headers={"accept": "*/*", "Content-Type": "application/json"},
                        json={"search_parameter": text_input, "context": context},
                    )

                    response_json = response.json()
                    st.info(
                        f"""
                    💡 Why is it relevant? \n {response_json}</div>
                    """
                    )

                    

                except Exception as e:
                    st.write(e)


if __name__ == "__main__":
    main()



