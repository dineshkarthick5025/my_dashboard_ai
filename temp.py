from sqlalchemy import create_engine, text

# Your PostgreSQL connection URL
DB_URL = "postgresql://postgres:DbT%214485%24@95.177.179.236:5400/ai_analytics"

# Create engine
engine = create_engine(DB_URL)

# Execute rollback
with engine.connect() as conn:
    conn.execute(text("ROLLBACK"))
