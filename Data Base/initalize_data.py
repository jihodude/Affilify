import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'Data', 'video_metadata.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

query = """

CREATE TABLE IF NOT EXISTS video (
    video_id TEXT PRIMARY KEY,  -- Unique identifier for videos
    url TEXT NOT NULL,          -- Video URL
    tags TEXT,                  -- Video Tags
    title TEXT,                 -- Video title
    description TEXT,           -- Video description
    category TEXT,              -- Youtube Category
    search_query TEXT,          -- Query used for search
    upload_date TEXT            -- Upload date of the video (ex: 2018-09-17T12:00:04Z)
); 

CREATE TABLE IF NOT EXISTS keywords (
    video_id TEXT NOT NULL,     -- Foreign key to reference the video table
    entities TEXT,              -- Extracted entities
    adjectives TEXT,            -- Extracted adjectives
    verbs TEXT,                 -- Extracted verbs
    nouns TEXT,                 -- Extracted nouns
    FOREIGN KEY (video_id) REFERENCES video(video_id) -- Link to video table
);

CREATE TABLE IF NOT EXISTS summary (
    video_id TEXT NOT NULL,     -- Foreign key to reference the video table
    summary TEXT,               -- Summarized content
    rating_score REAL,          -- Rating score
    suggested_content_type TEXT, -- Suggested content type
    FOREIGN KEY (video_id) REFERENCES video(video_id) -- Link to video table
);
        """


cursor.executescript(query)

conn.commit()

conn.close()
