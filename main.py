from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from groq import Groq
from questions import QUESTION_BANK
import json
import os

app = FastAPI()
groq_client = Groq(api_key=os.environ.get("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
"))

class AnswerRequest(BaseModel):
    role: str
    question: str
    answer: str

def get_ai_feedback(role, question, answer):
    prompt = "You are an expert interviewer for the role of " + role + ". The candidate was asked: " + question + ". Their answer was: " + answer + ". Respond ONLY in JSON: {\"score\": 0, \"strengths\": \"\", \"weaknesses\": \"\", \"ideal_answer\": \"\", \"follow_up\": \"\"}"
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.choices[0].message.content.strip()
    clean = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(clean)

@app.get("/roles")
def get_roles():
    return {"roles": list(QUESTION_BANK.keys())}

@app.get("/questions/{role}")
def get_questions(role: str):
    return {"questions": QUESTION_BANK.get(role, [])}

@app.get("/ai-questions/{role}")
def ai_questions(role: str):
    prompt = "Generate 5 unique interview questions for the role of " + role + ". Return ONLY a JSON array of 5 strings, no extra text."
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    raw = response.choices[0].message.content.strip()
    clean = raw.replace("```json", "").replace("```", "").strip()
    return {"questions": json.loads(clean)}

@app.post("/feedback")
def feedback(req: AnswerRequest):
    result = get_ai_feedback(req.role, req.question, req.answer)
    return result

app.mount("/", StaticFiles(directory="static", html=True), name="static")