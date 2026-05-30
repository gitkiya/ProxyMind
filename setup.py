from connect_db import connect_db

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE EXTENSION IF NOT EXISTS vector;
                   
        CREATE TABLE IF NOT EXISTS proxymind_memories (
            id SERIAL PRIMARY KEY,
            user_id VARCHAR,
            session_id VARCHAR,
            content TEXT,
            embedding vector(384),
            memory_type VARCHAR,
            timestamp TIMESTAMPTZ DEFAULT NOW()
        );
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("Tables created successfully!")

create_tables()