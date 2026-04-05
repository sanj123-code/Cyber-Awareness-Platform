from flask import Flask, render_template, request, session
import google.generativeai as genai

# 🔥 PASTE YOUR API KEY HERE
genai.configure(api_key="AIzaSyAJP7WCJupBp-qOMAtukx3NR_WlwCBuGDE")

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
        return "⚠️ AI failed to analyze URL"

# ---------------- HOME ----------------
@app.route("/", methods=["GET", "POST"])
def home():
    result = ""

    if request.method == "POST":
        url = request.form["url"]
        result = analyze_url_ai(url)

    return render_template("index.html", result=result)

# ---------------- TRAINING DATA ----------------
questions = [

# ---------------- PHISHING EMAIL ----------------
{"q": "You receive an email from your bank asking you to verify your account urgently.", "correct": "ignore", "explanation": "Banks never ask for sensitive info via email."},

{"q": "An email from 'support@amaz0n.com' asks you to login.", "correct": "ignore", "explanation": "Fake domains are common phishing tricks."},

{"q": "You get an email saying your account will be suspended unless you click a link.", "correct": "ignore", "explanation": "Urgency is used to panic users."},

{"q": "You receive an attachment labeled 'Invoice.pdf' from an unknown sender.", "correct": "ignore", "explanation": "Attachments can contain malware."},

{"q": "An email claims you won a prize and asks for personal details.", "correct": "ignore", "explanation": "Unexpected rewards are scams."},

{"q": "Email says 'Reset your password now' but the link looks strange.", "correct": "ignore", "explanation": "Always check URL before clicking."},

# ---------------- SOCIAL ENGINEERING CALLS ----------------
{"q": "A caller says they are from your bank and asks for OTP.", "correct": "ignore", "explanation": "Never share OTP with anyone."},

{"q": "Someone calls claiming to be tech support and asks for remote access.", "correct": "ignore", "explanation": "Legit companies don’t ask for remote control unexpectedly."},

{"q": "A person says your SIM will be blocked unless you provide details.", "correct": "ignore", "explanation": "Scammers create urgency to trick users."},

# ---------------- SMS / WHATSAPP SCAMS ----------------
{"q": "You receive SMS: 'Your KYC is pending, click here immediately'.", "correct": "ignore", "explanation": "Banks don’t send such links via SMS."},

{"q": "WhatsApp message says 'Free Netflix subscription, click link'.", "correct": "ignore", "explanation": "Free offers are common scams."},

{"q": "Message from unknown number says you won lottery.", "correct": "ignore", "explanation": "Lottery scams are very common."},

{"q": "Friend sends a suspicious link without context.", "correct": "ignore", "explanation": "Their account may be hacked."},

# ---------------- FAKE WEBSITES ----------------
{"q": "You visit a website with URL 'paypa1.com' asking login.", "correct": "ignore", "explanation": "Fake domains mimic real ones."},

{"q": "Website asks for card details without HTTPS.", "correct": "ignore", "explanation": "Secure sites use HTTPS."},

{"q": "A login page looks real but URL has extra characters.", "correct": "ignore", "explanation": "Always verify domain carefully."},

# ---------------- JOB / MONEY SCAMS ----------------
{"q": "You get a job offer asking for payment to process application.", "correct": "ignore", "explanation": "Legit jobs don’t ask for money."},

{"q": "Someone promises double money investment quickly.", "correct": "ignore", "explanation": "Too good to be true = scam."},

{"q": "Message says you can earn money by simple tasks.", "correct": "ignore", "explanation": "Task scams are very common."},

# ---------------- SOCIAL MEDIA SCAMS ----------------
{"q": "Instagram DM says 'Click link to verify your account'.", "correct": "ignore", "explanation": "Social platforms don’t send such links."},

{"q": "Facebook message from friend asks for urgent money.", "correct": "ignore", "explanation": "Their account may be compromised."},

{"q": "You get a fake giveaway link from influencer.", "correct": "ignore", "explanation": "Fake giveaways are common phishing tricks."},

# ---------------- GENERAL AWARENESS ----------------
{"q": "You see a link shortened with bit.ly asking login.", "correct": "ignore", "explanation": "Short links hide real destination."},

{"q": "Popup says 'Your phone is infected, install app now'.", "correct": "ignore", "explanation": "Fake alerts are scams."},

{"q": "You are asked to download unknown APK file.", "correct": "ignore", "explanation": "APK files can contain malware."},

{"q": "Someone asks personal info via email.", "correct": "ignore", "explanation": "Never share personal info casually."},

{"q": "A website asks for OTP unexpectedly.", "correct": "ignore", "explanation": "OTP should never be shared."},

{"q": "You get email with poor grammar and urgent request.", "correct": "ignore", "explanation": "Many phishing emails have mistakes."}

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

        # 👉 NEXT BUTTON
        if action == "next":
            session["question_index"] += 1
            if session["question_index"] >= len(questions):
                session["question_index"] = 0

            q = questions[session["question_index"]]
            return render_template("training.html", question=q["q"], score=session["score"])

        # 👉 ANSWER BUTTON
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
    app.run(debug=True)