from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import mysql.connector
import requests
import os

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "../frontend")

app.mount("/frontend", StaticFiles(directory=FRONTEND_DIR), name="frontend")

@app.get("/")
def load_frontend():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


def get_all_courses():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="innovel_db"
    )

    cursor = conn.cursor(dictionary=True, buffered=True)
    cursor.execute("SELECT * FROM courses")
    courses = cursor.fetchall()

    cursor.close()
    conn.close()

    return courses


@app.get("/course/{name}")
def course_details(name: str):

    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="innovel_db"
    )

    cursor = conn.cursor(dictionary=True, buffered=True)
    cursor.execute(
        "SELECT * FROM courses WHERE course_name LIKE %s",
        (f"%{name}%",)
    )

    course = cursor.fetchone()
    cursor.close()
    conn.close()

    if not course:
        return {"message": "Course not found"}

    final_fee = course["offer_fees"] if course["offer_fees"] else course["fees"]

    return {
        "course": course["course_name"],
        "duration": f"{course['duration_hours']} hours",
        "fees": final_fee,
        "syllabus": course["syllabus_highlight"]
    }


def ask_ollama(prompt):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.8,
                "num_predict": 180
            }
        }
    )

    return response.json()["response"]



@app.get("/chat/{message}")
def innovel_ai(message: str):

    courses = get_all_courses()
    message_lower = message.lower()

    matched_course = None

    # 🔎 Detect specific course mention
    for course in courses:
        if course["course_name"].lower() in message_lower:
            matched_course = course
            break

    # 🔎 Detect database-type keywords
    db_keywords = ["fee", "fees", "duration", "syllabus", "topics", "price", "cost"]
    is_db_question = any(word in message_lower for word in db_keywords)

    # CASE 1
    if is_db_question and not matched_course:
        return {
            "reply": "Please specify which course you are asking about (e.g., Python, Full Stack, AI/ML). I will provide exact details for that course."
        }

    # CASE 2
    if matched_course:

        final_fee = matched_course["offer_fees"] if matched_course["offer_fees"] else matched_course["fees"]

        course_context = f"""
Course Name: {matched_course['course_name']}
Duration: {matched_course['duration_hours']} hours
Fees: ₹{final_fee}
Highlights: {matched_course['syllabus_highlight']}
"""

        prompt = f"""
You are Innovel Institute Official AI Assistant.

Answer ONLY from the provided course data.

Keep the answer short, clear, and professional.
Maximum 120 words.
Use bullet points if needed.

After answering, politely encourage the user to join Innovel
and mention that we provide practical training and career support.

Course Data:
{course_context}

User Question:
{message}
"""

        ai_reply = ask_ollama(prompt)
        return {"reply": ai_reply}

    # CASE 3
    else:

        prompt = f"""
You are Innovel Institute Official AI Assistant.

User is asking a general question (not specific to course database).

Answer in SHORT and CLEAR format.
Maximum 100 words.
No long paragraphs.
No essay style.
Be crisp and professional.

If relevant, connect the answer to how Innovel courses
can help the student build career skills.

User Question:
{message}
"""

        ai_reply = ask_ollama(prompt)

        return {"reply": ai_reply}
