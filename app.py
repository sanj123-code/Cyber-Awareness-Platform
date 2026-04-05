from flask import Flask, render_template, request, session, redirect
import google.generativeai as genai
import os
import random

# ---------------- CONFIG ----------------
api_key = os.getenv("AIzaSyAIUbZJvt75BWaPbgRnHuiFG1BkFw7Xjt8")
genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-pro")

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- AI URL CHECK ----------------
def analyze_url_ai(url):
    try:
        prompt = f"Check if this URL is phishing or safe and explain briefly: {url}"
        response = model.generate_content(prompt)
        return response.text
    except:
        return None

# ---------------- FALLBACK ----------------
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

        if ai_result:
            result = "🤖 AI-powered Analysis:\n\n" + ai_result
        else:
            result = "🧠 Smart Detection Result:\n\n" + rule_based_check(url)

    return render_template("index.html", result=result)

# ---------------- QUESTIONS ----------------
questions = [

# SPAM
{"q": "Email asks to verify your bank account urgently.", "correct": "spam", "explanation": "Urgency + sensitive info = phishing."},
{"q": "Message says you won a lottery and must click a link.", "correct": "spam", "explanation": "Unexpected rewards are scams."},
{"q": "Email from support@amaz0n.com asking login.", "correct": "spam", "explanation": "Fake domain."},
{"q": "WhatsApp link offering free Netflix.", "correct": "spam", "explanation": "Free offers = phishing."},
{"q": "Caller asks for OTP.", "correct": "spam", "explanation": "Never share OTP."},
{"q": "SMS: KYC pending, click immediately.", "correct": "spam", "explanation": "Urgent SMS scams."},
{"q": "Account will be blocked unless you act now.", "correct": "spam", "explanation": "Fear tactic."},
{"q": "Unknown number sends suspicious link.", "correct": "spam", "explanation": "Unknown links unsafe."},
{"q": "Job offer asking for payment.", "correct": "spam", "explanation": "Jobs don’t ask money."},
{"q": "Instagram DM asking verification.", "correct": "spam", "explanation": "Fake verification scam."},

# NOT SPAM
{"q": "College email about exam schedule.", "correct": "not_spam", "explanation": "Official communication."},
{"q": "Bank app notification inside official app.", "correct": "not_spam", "explanation": "Secure source."},
{"q": "Amazon order confirmation email.", "correct": "not_spam", "explanation": "Expected action."},
{"q": "Professor message about assignment.", "correct": "not_spam", "explanation": "Known sender."},
{"q": "OTP after you requested login.", "correct": "not_spam", "explanation": "User initiated."},
{"q": "Google login alert email.", "correct": "not_spam", "explanation": "Security alert."},
{"q": "Friend message about meeting.", "correct": "not_spam", "explanation": "Normal conversation."},
{"q": "Payment receipt email.", "correct": "not_spam", "explanation": "Expected receipt."},
{"q": "LinkedIn job update.", "correct": "not_spam", "explanation": "Relevant update."},
{"q": "Food delivery notification.", "correct": "not_spam", "explanation": "Expected service."}
]

# ---------------- TRAINING ----------------
@app.route("/training", methods=["GET", "POST"])
def training():

    session.setdefault("score", 0)
    session.setdefault("question_index", 0)
    session.setdefault("answered", False)

    if "shuffled_questions" not in session or not session["shuffled_questions"]:
        shuffled = questions.copy()
        random.shuffle(shuffled)
        session["shuffled_questions"] = shuffled

    shuffled = session["shuffled_questions"]

    if session["question_index"] >= len(shuffled):
        session["question_index"] = 0

    q = shuffled[session["question_index"]]

    result = None
    explanation = None

    if request.method == "POST":
        action = request.form.get("action")

        if action == "next":
            session["question_index"] += 1
            session["answered"] = False
            return redirect("/training")

        if not session["answered"]:
            answer = request.form.get("answer")

            if answer == q.get("correct"):
                session["score"] += 10
                result = "✅ Correct!"
            else:
                session["score"] -= 5
                result = "❌ Wrong!"

            explanation = q.get("explanation", "")
            session["answered"] = True

    return render_template(
        "training.html",
        question=q.get("q", ""),
        result=result,
        explanation=explanation,
        score=session["score"],
        answered=session["answered"]
    )
# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    score = session.get("score", 0)
    return render_template("dashboard.html", score=score)

# ---------------- RESET ----------------
@app.route("/reset")
def reset():
    session.clear()
    return redirect("/")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)