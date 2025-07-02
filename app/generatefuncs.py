import re
from app.models.user_connection import UserConnection
import psycopg
import mysql.connector
import pyodbc
import oracledb
from sqlalchemy.orm import Session
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()  # Load from .env
api_key = os.getenv("DEEPSEEK_API_KEY")

client = OpenAI(api_key=api_key)



def clean_sql(raw_sql: str, as_single_line: bool = False) -> str:
    """
    Cleans an LLM-generated SQL string by removing markdown, explanations, and formatting.

    Args:
        raw_sql (str): Raw output from LLM containing SQL and possibly descriptions.
        as_single_line (bool): Whether to return the query in one line.

    Returns:
        str: Cleaned SQL query.
    """
    # Remove markdown
    cleaned = raw_sql.replace("```sql", "").replace("```", "").strip()

    # Split into lines and find where actual SQL starts (e.g., SELECT, WITH, INSERT, etc.)
    lines = cleaned.splitlines()
    sql_start_keywords = ("SELECT", "WITH", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP")
    
    for i, line in enumerate(lines):
        if line.strip().upper().startswith(sql_start_keywords):
            sql_lines = lines[i:]
            break
    else:
        sql_lines = lines  # fallback if no keyword found

    cleaned_sql = "\n".join(sql_lines).strip()

    if as_single_line:
        cleaned_sql = " ".join(cleaned_sql.split())

    return cleaned_sql


def generate_sql_from_prompt(user_prompt, schema_description, database_type):
    print(database_type)
    """
    Converts natural language questions to raw SQL queries using LLM via RunPod.
    
    Args:
        user_prompt (str): User's question in plain English.
        schema_description (str): Database table/column schema.

    Returns:
        str: Cleaned raw SQL query string (no explanation, no formatting).
    """
    # Construct a strict prompt
    prompt = f"""
You are a professional AI SQL assistant.

Your job is to generate a syntactically correct SQL query for a {database_type} database,
given the schema and user question.

### SCHEMA ###
{schema_description}

### INSTRUCTIONS ###
- Generate ONLY the SQL query.
- DO NOT include explanations, comments, markdown formatting, or any intro like "Here's your query".
- Ensure the SQL follows {database_type} syntax precisely, go with query which you think will definitely work.
- If filters, conditions, or joins are needed, infer them from the schema and question.

### QUESTION ###
{user_prompt}
"""

    # Call the model (DeepSeek/Llama etc.)
    sqlquery = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    # Extract only SQL from response
    #if sqlsquery startswith("Here's the SQL query to retrieve") remove content till /n
    sqlquery= clean_sql(sqlquery.choices[0].message.content.strip())
    return sqlquery
    #return sqlquery.choices[0].message.content.strip().removeprefix("```sql").removesuffix("```").strip()



def detect_chart_type(prompt: str) -> str:
    """
    Detects a chart or analysis type from the user prompt.

    Returns:
        A human-readable label like "Bar Graph", "Pie Chart", "AI Report"

    Raises:
        ValueError if no match or multiple matches are found.
    """

    chart_patterns = {
        "Bar Graph": r"\bbar[\s-]?(graph|chart)\b",
        "Line Graph": r"\bline[\s-]?(graph|chart)\b",
        "Pie Chart": r"\bpie[\s-]?chart\b",
        "Scatter Plot": r"\bscatter[\s-]?plot\b",
        "AI Report": r"\b(ai[\s-]?(analysis|report|insight)|machine learning|intelligent summary|ai[\s-]?generated[\s-]?(report|analysis)|report)\b"

    }

    matches = [label for label, pattern in chart_patterns.items()
               if re.search(pattern, prompt, re.IGNORECASE)]
    print(f"Detected matches: {matches}")  # Debugging output

    if len(matches) == 0:
        raise ValueError("No known chart or analysis type found in the prompt.")
    elif len(matches) > 1:
        raise ValueError(f"Multiple chart types detected: {', '.join(matches)}. Please specify only one.")

    return matches[0]




import json
import re

def generate_echarts_config(user_prompt, results, chart_type):
    """
    Generates visualization specifications using predefined JSON templates
    
    Args:
        user_prompt: The visualization request
        results: Data to visualize
        chart_type: Chart type ('pie', 'bar', 'line', etc.)
        
    Returns:
        dict: Valid ECharts configuration JSON
    """
    chart_type = chart_type or "bar"

    # Templates
    bar_chart_template = {
            "title": "Top 5 Products Sold",
            "xAxisData": ["Product A", "Product B", "Product C", "Product D", "Product E"],
            "seriesData": [
                {"name": "Total Sold", "type": "bar", "data": [14, 13, 12, 11, 10]}
            ]
        }
    line_chart_template = {
            "title": "Monthly Sales Trend",
            "xAxisData": ["Jan", "Feb", "Mar", "Apr"],
            "seriesData": [
                {"name": "Total Sales", "type": "line", "data": [12, 19, 8, 15]}
            ]
        }
    pie_chart_template = {
            "title": "Product Distribution",
            "seriesData": [
                {"name": "Product A", "value": 35},
                {"name": "Product B", "value": 25},
                {"name": "Product C", "value": 40}
            ]
        }

    # Choose template
    if chart_type == "line":
        template = line_chart_template
    elif chart_type == "pie":
        template = pie_chart_template
    else:
        template = bar_chart_template

    prompt = f"""
You are a chart generation assistant.
Question: {user_prompt}
Chart type: {chart_type}
Data: {results}

Use this JSON template:
{template}

Instructions:
1. Fill in the template with the provided data
2. Return ONLY valid JSON
3. No explanations or additional text
4. Include appropriate colors if the template has color fields
5. Make labels descriptive

Please use chart labels in the language of the user prompt.
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )

    content = response.choices[0].message.content.strip()

    # Clean triple backtick-wrapped JSON
    cleaned = re.sub(r"^```json\s*|\s*```$", "", content.strip(), flags=re.IGNORECASE)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print("[ERROR] Failed to parse JSON from model response:", e)
        return {}

def classify_intent_with_llm(user_prompt):
    """
    Determines the type of analysis requested using LLM.

    Args:
        user_prompt (str): User's original query

    Returns:
        str: One of ['visualization', 'anomaly_detection', 'prediction', 'forecasting', 'clustering']
    """
    prompt = f"""
You are an AI assistant for a no-code data analysis platform. 
Your job is to classify the user's request into one of these categories:

1. visualization - The user wants to generate a chart or visual
2. anomaly_detection - The user wants to find anomalies or outliers
3. prediction - The user wants to predict a value or outcome
4. forecasting - The user wants to forecast future trends or values
5. clustering - The user wants to group similar data points

User's Request: {user_prompt}

Respond with ONLY the intent name, no explanations.
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )

    intent = response.choices[0].message.content.strip().lower()

    # Fallback validation
    allowed_intents = ["visualization", "anomaly_detection", "prediction", "forecasting", "clustering"]
    if intent not in allowed_intents:
        intent = "visualization"  # Default fallback to visualization

    return intent

def summarize_anomalies_with_llm(anomalies, user_prompt):
    prompt = f"""
You are a data assistant.
Task: Summarize the anomalies found in this dataset based on the user's request.
User Request: {user_prompt}
Anomalies Data: {anomalies}

Provide a simple, user-friendly summary.
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

