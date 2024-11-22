# AI Data Analyst with Ollama

## Overview

This project is a **Streamlit-based AI-powered data analysis application** that leverages the Ollama LLM for interpreting user queries and provides analytical insights, visualizations, and statistical operations on uploaded datasets.

## Features
- **Natural Language Query Interpretation**: Converts user queries into actionable analysis tasks.
- **Automatic Code Generation**: Dynamically generates Python code to perform the requested analysis.
- **Interactive Visualizations**: Displays results as plots or data summaries in the web app.
- **Error Handling**: Provides detailed error feedback and retries for code corrections.
- **Session History**: Maintains a history of queries and results for easy reference.

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- Local mistral:7b LLM instance (accessible via `http://localhost:11434/v1`).
- Required Python libraries

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/abhinavgkrishnan/Python-data-analyst-2.0.git
   cd Python-data-analyst-2.0
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Start the Streamlit application:
   ```bash
   streamlit run analyst.py
   ```
### Assumptions
- The uploaded Excel file has column names in the first row.
- The Ollama LLM model: Mistral:7b is pre-configured and running locally.

---

## Documentation

### Key Files

#### 1. `chains.py`
This script processes user queries and handles:

**Query Interpretation:** Identifies statistical actions and data columns using _get_action.
**Code Generation:** Creates Python scripts for analysis using _get_code.
**Execution & Error Correction:** Executes code and corrects errors iteratively.

---

#### 2. `analyst.py`
A Streamlit-based interface for user interaction:

**Features:**
- **File Upload:**
  Allows users to upload an Excel file for analysis.
- **User Query Input:**
  Accepts user queries in natural language.
- **LLM Interpretation:**
  Uses `chains.py` to interpret the query and determine the appropriate action.
- **Result Display:**
  Dynamically displays results or visualizations based on user queries.

**Key Implementation:**
- User queries are processed through the Ollama LLM to determine the required action and columns.
- Results are displayed alongside the user's query in the Streamlit interface.
- Responses persist in `st.session_state` to ensure previous results remain visible.

---

## Unique Implementation Details

**Iterative Error Correction:** Automatically retries failed executions by sending errors back to the LLM for correction.
**Visualization Management:** Saves all generated plots in the output_plots directory.
**Session History:** Logs and displays all user queries and responses interactively.

## Example Usage
1. Upload an Excel file containing your dataset (e.g., `Age`, `Income`, `Sales`).
2. Enter queries such as:
   - "Run linear regression on income vs sales"
   - "Show histogram of sales"
   - "show scatter plot of age vs sales"
   - "show summary"
3. View results or visualizations directly in the Streamlit interface.

---


For any issues, suggestions, or contributions, please contact Abhinav G Krishnan at abhinavgkrishnan@gmail.com
