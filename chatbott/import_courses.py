import pandas as pd
import mysql.connector

# Load Excel
df = pd.read_excel("courses.xlsx")

# Connect MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="innovel_db"
)

cursor = conn.cursor()

for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO courses 
        (course_name, category, duration_hours, fees, offer_fees, offer_fees_duration, syllabus_highlight)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        row["course_name"],
        row["category"],
        row["duration_hours"],
        row["fees"],
        row["offer_fees"] if pd.notna(row["offer_fees"]) else None,
        row["offer_fees_duration"] if pd.notna(row["offer_fees_duration"]) else None,
        row["syllabus_highlight"]
    ))

conn.commit()
cursor.close()
conn.close()

print("Data Imported Successfully 🚀")