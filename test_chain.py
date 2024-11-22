import pandas as pd
from chains import create_chain
import os
from typing import Dict, Any

def print_result(result: Dict[str, Any]) -> None:
    """Pretty print the analysis result."""
    print("\nResult:")
    print("-" * 50)
    print(f"Type: {result['type']}")

    if result['type'] == 'plot':
        print(f"Plot saved as: {result['value']}")
        if not os.path.exists(result['value']):
            print("Warning: Plot file not found!")
    elif result['type'] == 'dataframe':
        print("\nDataFrame Output:")
        print(result['value'])
    elif result['type'] == 'error':
        print(f"Error: {result['value']}")
    else:
        print(f"Value: {result['value']}")
    print("-" * 50)

def test_analysis(file_path: str) -> None:
    """Run analysis tests on the data."""
    try:
        # Load data
        df = pd.read_excel(file_path)
        print(f"Data loaded successfully:")
        print(f"- Rows: {df.shape[0]}")
        print(f"- Columns: {df.shape[1]}")
        print(f"- Available columns: {', '.join(df.columns.tolist())}\n")

        # Create chain
        chain = create_chain()
        print("Analysis chain created successfully\n")

        # Test queries
        queries = [
            # "show scatter plot of Age vs Sales",
            # "calculate summary statistics",
            # "show correlation matrix",
            # "create histogram of Age"
            "run linear regression on age vs sales"
        ]

        for i, query in enumerate(queries, 1):
            print(f"\nTest #{i}: {query}")
            print("=" * 50)

            print("Generating code...")
            result = chain.generate_code(query, df)

            print_result(result)

            # Add a separator between tests
            if i < len(queries):
                print("\n" + "=" * 70 + "\n")

    except FileNotFoundError:
        print(f"Error: Could not find the data file at {file_path}")
    except pd.errors.EmptyDataError:
        print(f"Error: The data file at {file_path} is empty")
    except Exception as e:
        print(f"Error during analysis: {str(e)}")

if __name__ == "__main__":
    FILE_PATH = "/Users/gk/Python-Data-Analyst/sample_data_for_development.xlsx"
    test_analysis(FILE_PATH)
