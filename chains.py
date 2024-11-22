from typing import Dict, Any, Optional
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from datetime import datetime

class AnalysisChain:
    def __init__(self):
        self.api_base = "http://localhost:11434/v1"
        self.model_name = "mistral:7b"
        self.output_dir = "output_plots"
        os.makedirs(self.output_dir, exist_ok=True)

    def _get_action(self, query: str, df: pd.DataFrame) -> Dict[str, Optional[str]]:
        prompt = """You are an assistant specializing in data analysis tasks.
        Interpret the user's query and identify the most relevant statistical action or visualization type.
        Always respond in the following format:
        action: [specific action, concise, such as 'linear regression', 'logistic regression', 'polynomial regression', 'summary', 'describe', 'correlation', 'scatter plot', 'histogram', 'clean data', 'line graph', 'bar chart', 'covariance', 'skew', 'kurtosis']
        x: [single column name for single-variable analysis or x-axis]
        y: [single column name for y-axis when comparing two variables]
        
        Rules:
        1. For descriptive statistics (describe, summary):
           - Leave both x and y empty
           - These analyze all numeric columns automatically
        
        2. For single-variable analysis (histogram, distribution):
           - Include only x, leave y empty
           - x must be a single column name
        
        3. For two-variable analysis (scatter plot, regression, correlation):
           - Include both x and y
           - Both must be single column names
        
        4. Column names must be:
           - Exactly as they appear in the data
           - One column per field
           - No lists or multiple columns
        
        5. Never include:
           - Lists of columns
           - Comma-separated values
           - Multiple columns in one field
        
        Respond only with action, x, and y (if applicable) on separate lines."""

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Query: {query}\nAvailable columns: {list(df.columns)}"},
            ],
        }

        response = requests.post(
            f"{self.api_base}/chat/completions",
            json=payload,
        )

        content = response.json()["choices"][0]["message"]["content"].strip()

        action, x, y = None, None, None
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('action:'):
                action = line.split('action:')[1].strip()
            elif line.startswith('x:'):
                x = line.split('x:')[1].strip()
            elif line.startswith('y:'):
                y = line.split('y:')[1].strip()

        column_map = {col.lower(): col for col in df.columns}
        if x and x.lower() in column_map:
            x = column_map[x.lower()]
        if y and y.lower() in column_map:
            y = column_map[y.lower()]

        return {"action": action, "x": x, "y": y}

    def _get_code(self, action: Dict[str, Optional[str]], query: str, output_path: str) -> str:
        prompt = f"""You are a Python data analysis expert. Generate code for the following task:
    Action: {action['action']}
    X column: {action['x']}
    Y column: {action['y'] if action['y'] else 'None'}
    
    Requirements:
    1. Use the pre-existing DataFrame 'df'
    2. DO NOT include import statements
    3. If the task involves visualization or plotting:
       - Save to '{output_path}' exactly
       - Must set result = {{"type": "plot", "value": "{output_path}"}}
       - Use plt.figure(figsize=(10, 6)) for consistent sizing
       - Always include plt.close() after saving
       - Include appropriate titles and labels
    4. If the task involves data analysis without visualization, like 'summary', 'describe', 'clean data'
       - Set result = {{"type": "dataframe", "value": computed_data}}
       - Return relevant statistics or analysis results
    5. Use exact column names as provided
    6. Return only ONE result - either a plot or a dataframe, not both
    7. Choose the most appropriate output type based on the action requested
    
    Generate only the code, no explanations or imports."""
    
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": query},
            ],
        }
    
        response = requests.post(
            f"{self.api_base}/chat/completions",
            json=payload,
        )
    
        code = response.json()["choices"][0]["message"]["content"].strip()
        
        if "```python" in code:
            code = code.split("```python")[1].split("```")[0].strip()
        elif "```" in code:
            code = code.split("```")[1].strip()
    
        return code

    def generate_code(self, query: str, df: pd.DataFrame, max_retries: int = 5) -> Dict[str, Any]:
        try:
            plt.close('all')

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            output_path = os.path.join(self.output_dir, f"plot_{timestamp}.png")

            try:
                action = self._get_action(query, df)
                print(f"\nInterpreted action: {action}")
            except Exception as e:
                return {"type": "error", "value": f"Action interpretation failed: {str(e)}"}

            try:
                code = self._get_code(action, query, output_path)
            except Exception as e:
                return {"type": "error", "value": f"Initial code generation failed: {str(e)}"}

            last_error = None
            for attempt in range(max_retries):
                try:
                    print(f"\nAttempt {attempt + 1} of {max_retries}")
                    print("\nExecuting code:")
                    print("-" * 50)
                    print(code)
                    print("-" * 50)

                    namespace = {
                        'pd': pd,
                        'plt': plt,
                        'sns': sns,
                        'np': np,
                        'df': df.copy(),
                        'result': None
                    }

                    exec(code, namespace)
                    plt.close('all')

                    result = namespace.get('result')

                    if not isinstance(result, dict) or 'type' not in result or 'value' not in result:
                        raise ValueError(f"Invalid result format. Got: {result}")

                    if result['type'] == 'plot' and not os.path.exists(result['value']):
                        raise ValueError(f"Plot file {result['value']} was not created")

                    return result

                except Exception as exec_error:
                    error_msg = str(exec_error)
                    last_error = error_msg
                    print(f"Attempt {attempt + 1} failed: {error_msg}")

                    if attempt == max_retries - 1:
                        return {"type": "error", "value": "Could not generate result. Please try again."}

                    correction_prompt = f"""The user asked the following question:
### QUERY
{query}

You generated this python code:
{code}

It fails with the following error:
{error_msg}

Requirements:
1. Use exact filename '{output_path}' for saving plots
2. Set result = {{"type": "plot", "value": "{output_path}"}} for plots
3. Set result = {{"type": "dataframe", "value": computed_data}} for analysis

Fix the python code above and return ONLY the corrected code without any explanations or markdown formatting."""

                    try:
                        payload = {
                            "model": self.model_name,
                            "messages": [
                                {"role": "system", "content": "You are a Python data analysis expert. Fix the code to handle the error."},
                                {"role": "user", "content": correction_prompt},
                            ],
                        }

                        response = requests.post(
                            f"{self.api_base}/chat/completions",
                            json=payload,
                        )

                        code = response.json()["choices"][0]["message"]["content"].strip()
                        
                        if "```python" in code:
                            code = code.split("```python")[1].split("```")[0].strip()
                        elif "```" in code:
                            code = code.split("```")[1].strip()

                    except Exception as e:
                        return {"type": "error", "value": f"Code correction failed: {str(e)}"}

                    plt.close('all')
                    if os.path.exists(output_path):
                        try:
                            os.remove(output_path)
                        except Exception as e:
                            return {"type": "error", "value": f"Cleanup failed: {str(e)}"}

            return {"type": "error", "value": f"Unexpected end of execution. Last error: {last_error}"}

        except Exception as e:
            return {"type": "error", "value": f"Unexpected error: {str(e)}"}
        finally:
            plt.close('all')

def create_chain() -> AnalysisChain:
    return AnalysisChain()