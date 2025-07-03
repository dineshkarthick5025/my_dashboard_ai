import re
from app.models.query_history import QueryHistory

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


def detect_chart_type(prompt: str) -> str:
    prompt = prompt.lower()
    if re.search(r"\bline\b|\btrend\b|\bover time\b", prompt):
        return "line"
    elif re.search(r"\bbar\b|\bcompare\b", prompt):
        return "bar"
    elif re.search(r"\bpies?\b|\bdistribution\b|\bpercentage\b", prompt):
        return "pie"
    else:
        return "bar"  # Default fallback
    
def detect_output_format(prompt: str) -> str:
    """
    Detects if the user wants 'visual', 'text', or 'both' output based on the prompt.
    """
    prompt = prompt.lower()
    
    if re.search(r"\bgraph\b|\bchart\b|\bvisual(ization)?\b|\bplot\b", prompt):
        return "visual"
    elif re.search(r"\btable\b|\blist\b|\btext\b|\bsummary\b", prompt):
        return "text"
    elif re.search(r"\bboth\b|\bvisual and text\b", prompt):
        return "both"
    else:
        return "text"  # Default to text if unclear


def save_query_history(db, user, prompt, generated_query, status, llm_config):
    """
    Saves query details to the QueryHistory table.

    Args:
        db (Session): Database session
        user (User): Current user object
        prompt (str): User's original prompt
        generated_query (str): Generated SQL query
        status (str): 'success' or 'failed'
        llm_config (dict or None): Config or result payload, can be None for failures
    """
    db.add(QueryHistory(
        user_id=user.id,
        prompt=prompt,
        generated_query=generated_query,
        status=status,
        llm_config=llm_config
    ))
    db.commit()


def transform_sql_result_to_llm_json(columns, rows):
    return {
        "columns": columns,
        "rows": [dict(zip(columns, row)) for row in rows]
    }