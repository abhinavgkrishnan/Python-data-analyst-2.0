import streamlit as st
import pandas as pd
from chains import create_chain
from datetime import datetime

if "responses" not in st.session_state:
    st.session_state.responses = []

def process_query(df: pd.DataFrame, query: str) -> None:
    try:
        chain = create_chain()
        result = chain.generate_code(query, df)
        
        response_entry = {
            "query": query,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        if result["type"] == "error":
            response_entry["response_type"] = "error"
            response_entry["content"] = result["value"]
        elif result["type"] == "plot":
            response_entry["response_type"] = "plot"
            response_entry["content"] = result["value"]
        elif result["type"] == "dataframe":
            response_entry["response_type"] = "dataframe"
            response_entry["content"] = result["value"]
        
        st.session_state.responses.append(response_entry)

    except Exception as e:
        st.session_state.responses.append({
            "query": query,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "response_type": "error",
            "content": f"Error processing query: {str(e)}"
        })

def main():
    st.title("AI Data Analyst")

    uploaded_file = st.file_uploader("Upload an Excel file", type=["xlsx", "xls"])
    
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        st.write("Data Preview:")
        st.dataframe(df.head())

        with st.form("query_form"):
            query = st.text_input("Enter your analysis query:")
            submit_button = st.form_submit_button("Submit")

            if submit_button and query:
                process_query(df, query)

        st.write("### Analysis History")
        for response in st.session_state.responses[::-1]:
            with st.expander(f"{response['timestamp']} - {response['query']}", expanded=True):
                if response["response_type"] == "error":
                    st.error(response["content"])
                elif response["response_type"] == "plot":
                    st.image(response["content"])
                elif response["response_type"] == "dataframe":
                    st.dataframe(response["content"])
                else:
                    st.write(response["content"])

if __name__ == "__main__":
    main()