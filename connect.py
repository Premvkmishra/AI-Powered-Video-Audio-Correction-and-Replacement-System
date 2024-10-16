import streamlit as st
import openai
import requests
import json

def main():
    st.title("Azure OpenAI GPT-4o Connectivity Test")
    
    # Define the API key and endpoint
    azure_openai_key = "22ec84421ec24230a3638d1b51e3a7dc"  # Replace with your API key
    azure_openai_endpoint = "https://internshala.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-08-01-preview"
    
    if st.button("Connect and Get Response"):
        if azure_openai_key and azure_openai_endpoint:
            try:
                headers = {
                    "Content-Type": "application/json",
                    "api-key": azure_openai_key
                }
                
                data = {
                    "messages": [{"role": "user", "content": "Hello, Azure OpenAI!"}],
                    "max_tokens": 50
                }
                
                response = requests.post(azure_openai_endpoint, headers=headers, json=data)
                
                if response.status_code == 200:
                    result = response.json()
                    st.success(result["choices"][0]["message"]["content"].strip())
                else:
                    st.error(f"Failed to connect or retrieve response: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Failed to connect or retrieve response: {str(e)}")
        else:
            st.warning("Please enter all the required details.")

if __name__ == "__main__":
    main()
