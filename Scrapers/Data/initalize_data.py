import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'Data', 'video_metadata.db')

conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

query = """

CREATE TABLE IF NOT EXISTS video (
    video_id TEXT PRIMARY KEY,  -- Unique identifier for videos
    url TEXT NOT NULL,          -- Video URL
    title TEXT,                 -- Video title
    description TEXT,           -- Video description
    category_id INTEGER,        -- Category of the video
    upload_date TEXT            -- Upload date of the video
);

CREATE TABLE IF NOT EXISTS keywords (
    id TEXT PRIMARY KEY,        -- Unique identifier for this table (can match video_id)
    video_id TEXT NOT NULL,     -- Foreign key to reference the video table
    entities TEXT,              -- Extracted entities
    adjectives TEXT,            -- Extracted adjectives
    verbs TEXT,                 -- Extracted verbs
    nouns TEXT,                 -- Extracted nouns
    FOREIGN KEY (video_id) REFERENCES video(video_id) -- Link to video table
);

CREATE TABLE IF NOT EXISTS sentiments (
    id TEXT PRIMARY KEY,        -- Unique identifier (can match video_id)
    video_id TEXT NOT NULL,     -- Foreign key to reference the video table
    polarity REAL,              -- Sentiment polarity (e.g., -1 to 1)
    semantic TEXT,              -- Sentiment semantic description (positive, neutral, negative)
    FOREIGN KEY (video_id) REFERENCES video(video_id) -- Link to video table
);

CREATE TABLE IF NOT EXISTS summary (
    id TEXT PRIMARY KEY,        -- Unique identifier (can match video_id)
    video_id TEXT NOT NULL,     -- Foreign key to reference the video table
    summary TEXT,               -- Summarized content
    rating_score REAL,          -- Rating score
    content_type_recommendation TEXT, -- Suggested content type
    FOREIGN KEY (video_id) REFERENCES video(video_id) -- Link to video table
);
        """

# Execute the query
cursor.executescript(query)  # Use executescript for multiple statements

# Commit the changes
conn.commit()

# Verify if tables are created
cursor.execute("SELECT * FROM video;")
print("Tables in the database:", cursor.fetchall())

# Close the connection when done
conn.close()
