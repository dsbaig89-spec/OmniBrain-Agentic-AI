import glob
import os
import re

import duckdb
import pandas as pd
from groq import Groq
from dotenv import load_dotenv


# ==========================================
# Environment
# ==========================================

load_dotenv("backend/.env")

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

CSV_FOLDER = "backend/uploads/csv"

MODEL = "openai/gpt-oss-20b"


# ==========================================
# Find Latest CSV
# ==========================================

def get_latest_csv():

    files = glob.glob(
        os.path.join(CSV_FOLDER, "*.csv")
    )

    if not files:
        return None

    return max(
        files,
        key=os.path.getmtime
    )


# ==========================================
# Generate SQL
# ==========================================

def generate_sql(question, df):
    
    columns = "\n".join(
        f"- {column}"
        for column in df.columns
    )

    # Give the LLM ALL categorical values, not just first 5 rows
    unique_values = {}

    for column in df.columns:
        if df[column].dtype == "object":
            unique_values[column] = (
                df[column]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )

    values_text = "\n"

    for column, values in unique_values.items():
        values_text += f"\nColumn: {column}\n"

        for value in values:
            values_text += f"- {value}\n"

    sample = df.head(5).to_string(index=False)

    prompt = f"""
You are an expert data analyst.

A CSV file has been loaded into a DuckDB table named `data`.

Columns:
{columns}

Sample:
{sample}

All categorical values in the dataset:
{values_text}

User question:
{question}

Generate ONE read-only DuckDB SQL query.

Rules:
- Return ONLY SQL.
- Use SELECT or WITH only.
- Never use INSERT, UPDATE, DELETE, DROP or ALTER.
- Use the actual column names.
- Perform the requested calculation using ALL relevant rows.
- Do not ignore valid categories just because they are not in the sample.
- Exclude rows such as Total, TotalStated, Not stated, and Response unidentifiable
  when calculating statistics for actual observations.
- Never invent values.

IMPORTANT FOR RENT QUESTIONS:

If the user asks for average rent and the rent column contains ranges:

Under $50 → midpoint 25

$50–$74 → midpoint 62

$75–$99 → midpoint 87

$100–$124 → midpoint 112

$125–$149 → midpoint 137

$150–$174 → midpoint 162

$175–$199 → midpoint 187

$200–$249 → midpoint 224.5

$250–$299 → midpoint 274.5

$300–$349 → midpoint 324.5

$350–$399 → midpoint 374.5

$400–$449 → midpoint 424.5

$450–$499 → midpoint 474.5

$500–$549 → midpoint 524.5

$550–$599 → midpoint 574.5

$600 and over → use 600 as the lower-bound estimate and clearly mention
that the open-ended category prevents an exact average.

For weighted average rent:

SUM(midpoint * household_count)
/
SUM(household_count)

Use all valid rent categories.

Return ONLY the SQL query.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    sql = response.choices[0].message.content.strip()

    sql = re.sub(
        r"```sql|```",
        "",
        sql,
        flags=re.IGNORECASE
    ).strip()

    return sql
# ==========================================
# SQL Agent
# ==========================================

def sql_agent(question):

    csv_path = get_latest_csv()

    # ------------------------------------------
    # No CSV
    # ------------------------------------------

    if not csv_path:

        return {
            "answer": "Please upload a CSV file first.",
            "sql": None,
            "data": None
        }

    try:

        # ------------------------------------------
        # Load CSV
        # ------------------------------------------

        try:

            df = pd.read_csv(
                csv_path,
                encoding="utf-8"
            )

        except UnicodeDecodeError:

            # Handles CSV files containing
            # characters such as en-dash (–)
            df = pd.read_csv(
                csv_path,
                encoding="cp1252"
            )

        # ------------------------------------------
        # Generate SQL
        # ------------------------------------------

        sql = generate_sql(
            question,
            df
        )

        # ------------------------------------------
        # Security Check
        # ------------------------------------------

        if not re.match(
            r"^\s*(SELECT|WITH)\b",
            sql,
            re.IGNORECASE
        ):

            return {
                "answer": "Only read-only data queries are allowed.",
                "sql": sql,
                "data": None
            }

        # ------------------------------------------
        # Execute SQL using DuckDB
        # ------------------------------------------

        result = duckdb.query_df(
            df,
            "data",
            sql
        ).df()

        # ------------------------------------------
        # Convert result to text
        # ------------------------------------------

        result_text = result.to_string(
            index=False
        )

        # ------------------------------------------
        # Generate Explanation
        # ------------------------------------------

        explanation_prompt = f"""
You are a data analyst.

User question:
{question}

SQL executed:
{sql}

Actual SQL result:
{result_text}

Explain the result clearly and concisely.

IMPORTANT:
- Do not invent values.
- Use ONLY the SQL result.
- If the result is empty, say that no matching data was found.
"""

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": explanation_prompt
                }
            ],
            temperature=0
        )

        answer = response.choices[0].message.content

        # ------------------------------------------
        # Return Result
        # ------------------------------------------

        return {
            "answer": answer,
            "sql": sql,
            "data": result.to_dict(
                orient="records"
            )
        }

    # ------------------------------------------
    # Error Handling
    # ------------------------------------------

    except Exception as e:

        return {
            "answer": f"Unable to analyze the CSV: {str(e)}",
            "sql": None,
            "data": None
        }