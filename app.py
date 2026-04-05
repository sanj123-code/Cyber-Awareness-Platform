from flask import Flask, render_template, request, session
import google.generativeai as genai
import os

# ---------------- CONFIG ----------------
api_key = os.getenv("AIzaSyCc48woG70NkfTD9uSWKAxnsrGlS1325FA")
print("API KEY:", api_key)  # 🔥 debug (check in Render logs)

genai.configure(api_key=api_key)

# ✅ Use stable model
model = genai.GenerativeModel("gemini-pro")

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- AI URL CHECK ----------------
def analyze_url_ai(url):
    try:
        prompt = f"Check if this URL is phishing or safe and explain briefly: {url}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print("AI ERROR:", e)
        return f"❌ AI ERROR: {str(e)}"


# ---------------- RULE BASED FALLBACK ----------------
def rule_based_check(url):
    score = 0

    if len(url) > 75:
        score += 2
    if not url.startswith("https://"):
        score += 2
    if "@" in url:
        score += 3
    if url.count('.') > 3:
        score += 2

    keywords = ["login", "verify", "bank", "secure", "account"]
    for word in keywords:
        if word in url.lower():
            score += 2

    if score >= 6:
        return "Dangerous ❌"
    elif score >= 3:
        return "Suspicious ⚠️"
    else:
        return "Safe ✅"


# ---------------- HOME ----------------
@app.route("/", methods=["GET", "POST"])
def home():
    result = ""

    if request.method == "POST":
        url = request.form["url"]

        ai_result = analyze_url_ai(url)

        # 🔥 If AI gives error → fallback
        if ai_result and "❌ AI ERROR" not in ai_result:
            result = "🤖 AI Analysis:\n\n" + ai_result
        else:
            fallback = rule_based_check(url)
            result = f"⚠️ AI failed, using fallback:\n\n{fallback}"

    return render_template("index.html", result=result)


# ---------------- TRAINING DATA ----------------
questions = [
    {"q": "Email asks to verify bank account urgently.", "correct": "ignore", "explanation": "Banks don’t ask info via email."},
    {"q": "Caller asks for OTP.", "correct": "ignore", "explanation": "Never share OTP."},
    {"q": "Lottery message with link.", "correct": "ignore", "explanation": "Likely scam."},
    {"q": "Email from amaz0n.com.", "correct": "ignore", "explanation": "Fake domain."},
    {"q": "Free Netflix WhatsApp link.", "correct": "ignore", "explanation": "Common scam."}
]

# ---------------- TRAINING ----------------
@app.route("/training", methods=["GET", "POST"])
def training():
    if "score" not in session:
        session["score"] = 0

    if "question_index" not in session:
        session["question_index"] = 0

    q = questions[session["question_index"]]

    result = None
    explanation = None

    if request.method == "POST":
        action = request.form.get("action")

        # NEXT QUESTION
        if action == "next":
            session["question_index"] += 1
            if session["question_index"] >= len(questions):
                session["question_index"] = 0

            q = questions[session["question_index"]]
            return render_template("training.html", question=q["q"], score=session["score"])

        # ANSWER
        answer = request.form.get("answer")

        if answer == q["correct"]:
            session["score"] += 10
            result = "✅ Correct!"
        else:
            session["score"] -= 5
            result = "❌ Wrong!"

        explanation = q["explanation"]

    return render_template(
        "training.html",
        question=q["q"],
        result=result,
        explanation=explanation,
        score=session["score"]
    )


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    score = session.get("score", 0)
    return render_template("dashboard.html", score=score)


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)