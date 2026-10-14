from flask import Flask, render_template, request, redirect, url_for
from analyzer import analyze_feedback, analyze_all_feedback

app = Flask(__name__)

# Temporary storage; data resets when the server restarts.
feedback_data = []


@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    feedback = ""

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
        session_percentages=stats["percentages"]
    )
    return render_template(
            "index.html",
            result=result,
            feedback=feedback
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