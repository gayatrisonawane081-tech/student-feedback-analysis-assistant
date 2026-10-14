
from flask import Flask, render_template, request, redirect, url_for
from analyzer import analyze_feedback, analyze_all_feedback

app = Flask(__name__)

# Temporary storage: feedback resets when the server restarts.
feedback_data = []


def answer_follow_up(question):
    """Answer follow-up questions using the feedback collected so far."""
    if not feedback_data:
        return "Please submit some student feedback before asking questions."

    question_lower = question.lower()
    all_feedback = " ".join(feedback_data).lower()

    # Sentiment-related questions
    if any(word in question_lower for word in ["sentiment", "feeling", "mood"]):
        results = [analyze_feedback(item) for item in feedback_data]
        counts = {}

        for item in results:
            sentiment = item.get("sentiment", "Unknown")
            counts[sentiment] = counts.get(sentiment, 0) + 1

        if counts:
            dominant = max(counts, key=counts.get)
            return f"The most common sentiment is {dominant}, appearing in {counts[dominant]} feedback response(s)."

    # Questions about the number of responses
    if any(word in question_lower for word in ["how many", "number", "total", "count"]):
        return f"A total of {len(feedback_data)} student feedback response(s) have been submitted."

    # Topic-related questions
    if any(word in question_lower for word in ["topic", "issue", "problem", "discuss"]):
        keywords = {
            "teaching": ["teacher", "teaching", "faculty", "lecture"],
            "infrastructure": ["infrastructure", "classroom", "building", "facility"],
            "laboratory": ["lab", "laboratory", "practical", "equipment"],
            "examinations": ["exam", "examination", "test", "marks"],
            "placements": ["placement", "job", "career", "company"],
            "curriculum": ["syllabus", "curriculum", "subject", "course"],
        }

        found = [
            topic for topic, words in keywords.items()
            if any(word in all_feedback for word in words)
        ]

        if found:
            return "Topics mentioned in the feedback include: " + ", ".join(found) + "."
        return "No common topics were identified. Try collecting more detailed feedback."

    # Improvement-related questions
    if any(word in question_lower for word in ["improve", "suggestion", "recommend", "better"]):
        return (
            "Suggested improvements: review recurring student concerns, "
            "improve teaching support and practical facilities where needed, "
            "and collect follow-up feedback to measure progress."
        )

    # General summary
    if any(word in question_lower for word in ["summary", "summarize", "overall", "feedback"]):
        return (
            f"There are {len(feedback_data)} feedback response(s). "
            "Review the dashboard for sentiment statistics and analyze individual "
            "responses to identify specific concerns."
        )

    return (
        "I can answer questions about the overall sentiment, number of responses, "
        "feedback topics, improvement suggestions, or overall summary. "
        "Please try asking about one of these areas."
    )


@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    feedback = ""
    follow_up_question = ""
    follow_up_answer = ""

    if request.method == "POST":
        feedback = request.form.get("feedback", "").strip()

        if feedback:
            result = analyze_feedback(feedback)
            feedback_data.append(feedback)

    stats = analyze_all_feedback(feedback_data)

    return render_template(
        "index.html",
        result=result,
        feedback=feedback,
        session_total=stats["total"],
        session_percentages=stats["percentages"],
        follow_up_question=follow_up_question,
        follow_up_answer=follow_up_answer
    )


@app.route("/ask", methods=["POST"])
def ask():
    question = request.form.get("question", "").strip()
    answer = answer_follow_up(question)
    stats = analyze_all_feedback(feedback_data)

    return render_template(
        "index.html",
        result=None,
        feedback=feedback_data[-1] if feedback_data else "",
        session_total=stats["total"],
        session_percentages=stats["percentages"],
        follow_up_question=question,
        follow_up_answer=answer
    )


@app.route("/dashboard")
def dashboard():
    data = analyze_all_feedback(feedback_data)
    return render_template("dashboard.html", data=data)


@app.route("/clear", methods=["POST"])
def clear():
    feedback_data.clear()
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
