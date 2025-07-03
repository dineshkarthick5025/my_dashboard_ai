from fastapi import APIRouter, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.dependencies import get_current_user, get_db
from app.generatefuncs import generate_sql_from_prompt
from app.generatefuncs import generate_echarts_config
from app.session_connection import session_conn_manager
from app.models.query_history import QueryHistory
from app.models.user import User
import re
from app.generatefuncs import classify_intent_with_llm, summarize_anomalies_with_llm, generate_sql_from_prompt_for_prophet, generate_forecast_config

router = APIRouter()

def get_predefined_echarts_config(chart_type: str) -> dict:
    if chart_type == "pie":
        return {
            "title": "Product Distribution",
            "seriesData": [
                {"name": "Product A", "value": 35},
                {"name": "Product B", "value": 25},
                {"name": "Product C", "value": 40}
            ]
        }
    elif chart_type == "line":
        return {
            "title": "Monthly Sales Trend",
            "xAxisData": ["Jan", "Feb", "Mar", "Apr"],
            "seriesData": [
                {"name": "Total Sales", "type": "line", "data": [12, 19, 8, 15]}
            ]
        }
    elif chart_type == "bar":
        return {
            "title": "Top 5 Products Sold",
            "xAxisData": ["Product A", "Product B", "Product C", "Product D", "Product E"],
            "seriesData": [
                {"name": "Total Sold", "type": "bar", "data": [14, 13, 12, 11, 10]}
            ]
        }
    else:
        return {}

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


def detect_anomalies(data):
    """
    Detects anomalies in the provided dataset using Isolation Forest.

    Args:
        data (list of dicts): Transformed SQL result

    Returns:
        list of dicts: Rows flagged as anomalies
    """
    import pandas as pd
    from sklearn.ensemble import IsolationForest

    df = pd.DataFrame(data)
    
    # Only use numeric columns for anomaly detection
    numeric_df = df.select_dtypes(include=["float64", "int64"])
    if numeric_df.empty:
        return []

    model = IsolationForest(contamination=0.05, random_state=42)
    df['anomaly'] = model.fit_predict(numeric_df)

    # Return rows where anomaly == -1
    anomalies = df[df['anomaly'] == -1].drop(columns='anomaly').to_dict(orient='records')
    return anomalies


def run_prediction(data, user_prompt):
    """
    Runs a basic prediction task using AutoML or pre-defined logic.

    Args:
        data (list of dicts): Transformed SQL result
        user_prompt (str): User's prediction request

    Returns:
        list of dicts: Predicted results
    """
    import pandas as pd
    from pycaret.classification import predict_model, load_model

    df = pd.DataFrame(data)
    
    # You can improve this by parsing target from the prompt using LLM
    model = load_model("default_classifier_model")  # Replace with actual model

    predictions = predict_model(model, data=df)
    
    return predictions.to_dict(orient='records')


from prophet import Prophet
import pandas as pd

def run_forecasting(data, user_prompt):
    """
    Runs Prophet forecasting on provided data.

    Args:
        data (list of dict): List with 'ds' and 'y' keys.
        user_prompt (str): Optional user prompt for logging/debugging.

    Returns:
        dict: Contains historical and forecasted data for line chart.
    """
    try:
        df = pd.DataFrame(data)
        df['ds'] = pd.to_datetime(df['ds'])
        
        model = Prophet()
        model.fit(df)

        # Forecast 30 future periods (you can customize this)
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)

        # Prepare historical data
        historical_data = df[['ds', 'y']].rename(columns={'ds': 'date', 'y': 'value'})
        historical_data['type'] = 'historical'

        # Prepare forecasted data
        forecast_data = forecast[['ds', 'yhat']].rename(columns={'ds': 'date', 'yhat': 'value'})
        forecast_data = forecast_data[forecast_data['date'] > df['ds'].max()]
        forecast_data['type'] = 'forecast'

        # Combine for chart
        combined_data = pd.concat([historical_data, forecast_data])

        chart_data = combined_data.to_dict(orient='records')

        #print(f"✅ [DEBUG] Forecasting successful: {(chart_data)} records generated")
        return chart_data
    
    
    except Exception as e:
        print(f"❌ [ERROR] Forecasting failed: {e}")
        return {
            "error": "Forecasting failed",
            "details": str(e)
        }



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

def run_clustering(data):
    """
    Performs K-Means clustering on the dataset.

    Args:
        data (list of dicts): Transformed SQL result

    Returns:
        dict: Cluster labels with counts and optional sample data
    """
    import pandas as pd
    from sklearn.cluster import KMeans

    df = pd.DataFrame(data)
    
    numeric_df = df.select_dtypes(include=["float64", "int64"])
    if numeric_df.empty:
        return {"error": "No numeric columns found for clustering"}

    kmeans = KMeans(n_clusters=3, random_state=42)
    df['cluster'] = kmeans.fit_predict(numeric_df)

    # Summary of cluster counts
    cluster_counts = df['cluster'].value_counts().to_dict()

    # Optional: Sample rows per cluster
    sample_per_cluster = {
        int(cluster): df[df['cluster'] == cluster].sample(min(3, len(df[df['cluster'] == cluster]))).to_dict(orient='records')
        for cluster in df['cluster'].unique()
    }

    return {
        "cluster_counts": cluster_counts,
        "sample_per_cluster": sample_per_cluster
    }


























# --- Helper: Transform SQL result to LLM-friendly JSON ---
def transform_sql_result_to_llm_json(columns, rows):
    return {
        "columns": columns,
        "rows": [dict(zip(columns, row)) for row in rows]
    }

# --- Helper: Extract chart type from prompt if not given ---
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

# --- Main Route ---
from app.models import QueryHistory

@router.post("/dashboard/generate")
async def generate_dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    data = await request.json()
    prompt = data.get("prompt", "")
    db_id = data.get("db_id", "")

    session_id = request.cookies.get("session_id")
    if not session_id:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    cached = session_conn_manager.get_connection(session_id, db_id)
    if not cached:
        return JSONResponse(status_code=400, content={"error": "Connection not found in cache"})

    conn = cached["connection"]
    schema = cached["schema"]
    db_type = db_id.split(" - ")[0].strip().lower()

    # 🔥 NEW STEP: Let LLM classify the user's intent
    intent = classify_intent_with_llm(prompt)  # e.g., "visualization", "anomaly_detection", etc.

    cursor = conn.cursor()
    
    # For most intents, SQL is still needed
    if intent=="visualization":
        sql_query = generate_sql_from_prompt(prompt, schema, db_type)
        print(f"📝 [DEBUG] Generated SQL: {sql_query}")
        try:
            cursor.execute(sql_query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            transformed_data = transform_sql_result_to_llm_json(columns, rows)
            print(f"✅ [DEBUG] Transformed Data: {transformed_data}")
        except Exception as e:
            print(f"❌ [ERROR] SQL Execution Failed: {e}")
            save_query_history(db, current_user, prompt, sql_query, "failed", None)
            return JSONResponse(status_code=500, content={"error": "SQL execution failed"})
        
    elif intent == "forecasting":
        sql_query_forcast = generate_sql_from_prompt_for_prophet(prompt, schema, db_type)
        print(f"📝 [DEBUG] Generated SQL for forecasting: {sql_query_forcast}")
        try:
            cursor.execute(sql_query_forcast)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            
            # Convert rows to list of dicts for easy processing
            data = [dict(zip(columns, row)) for row in rows]

            # Prophet expects two columns: 'ds' for datetime and 'y' for target value
            # Assuming your SQL query already returns columns with these names
            prophet_data = [{"ds": row["ds"], "y": row["y"]} for row in data]

            print(f"✅ [DEBUG] Data for Prophet: {prophet_data}")

        except Exception as e:
            print(f"❌ [ERROR] SQL Execution for forecasting Failed: {e}")
            save_query_history(db, current_user, prompt, sql_query_forcast, "failed", None)
            return JSONResponse(status_code=500, content={"error": "SQL execution for forecasting failed"})


    # 🔥 NEW STEP: Based on intent, apply respective logic
    status = "success"
    result_payload = {}

    if intent == "visualization":
        chart_type = data.get("chart_type") or detect_chart_type(prompt)
        echarts_config = generate_echarts_config(prompt, transformed_data, chart_type)
        result_payload = {
            "chart_type": chart_type,
            "echarts_config": echarts_config
        }

    elif intent == "forecasting":
        forecast_result = run_forecasting(prophet_data, prompt)
        output_format = detect_output_format(prompt)
        print(f"✅ [DEBUG] Forecast Result: {forecast_result}")
        chart_type = "line"  # Forecasts are typically shown as line charts
        echarts_config = generate_forecast_config(prompt, forecast_result, chart_type)
        
        result_payload = {
            "chart_type": chart_type,
            "echarts_config": echarts_config
        }


    else:
        return JSONResponse(status_code=400, content={"error": "Unrecognized intent"})
    
    sql_query = sql_query if intent == "visualization" else sql_query_forcast

    # Save successful query
    save_query_history(db, current_user, prompt, sql_query, status, result_payload)

    print(f"✅ [DEBUG] Result Payload: {result_payload}")
    return {
        "status": status,
        "intent": intent,
        **result_payload
    }


"""@router.post("/dashboard/generate")
async def generate_dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    data = await request.json()
    prompt = data.get("prompt", "")
    db_id = data.get("db_id", "")
    chart_type = data.get("chart_type") or detect_chart_type(prompt)

    session_id = request.cookies.get("session_id")
    if not session_id:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    cached = session_conn_manager.get_connection(session_id, db_id)
    if not cached:
        return JSONResponse(status_code=400, content={"error": "Connection not found in cache"})

    conn = cached["connection"]
    schema = cached["schema"]
    db_type = db_id.split(" - ")[0].strip().lower()

    sql_query = generate_sql_from_prompt(prompt, schema, db_type)
    print(f"📝 [DEBUG] Generated SQL: {sql_query}")

    cursor = conn.cursor()
    status = "success"
    echarts_config = {}
    try:
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        transformed_data = transform_sql_result_to_llm_json(columns, rows)
        echarts_config = generate_echarts_config(prompt, transformed_data, chart_type)
        print(f"✅ [DEBUG] LLM Config: {echarts_config}")

    except Exception as e:
        print(f"❌ [ERROR] SQL Execution Failed: {e}")
        status = "failed"

        # Save failed query attempt
        db.add(QueryHistory(
            user_id=current_user.id,
            prompt=prompt,
            generated_query=sql_query,
            status=status,
            llm_config=None
        ))
        db.commit()

        return JSONResponse(status_code=500, content={"error": "SQL execution failed"})

    # Save successful query
    db.add(QueryHistory(
        user_id=current_user.id,
        prompt=prompt,
        generated_query=sql_query,
        status=status,
        llm_config=echarts_config
    ))
    db.commit()

    return {
        "status": "success",
        "chart_type": chart_type,
        "echarts_config": echarts_config
    }"""

