import sqlite3
import os

db_path = os.path.join(os.getcwd(), 'Data', 'video_metadata.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()









conn.close()
