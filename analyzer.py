from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import Counter

model = SentimentIntensityAnalyzer()

TOPICS = {
    "Teaching": [
        "teacher", "teaching", "lecture", "explanation",
        "explain", "understand"
    ],
    "Course Content": [
        "syllabus", "course", "notes", "study material"
    ],
    "Infrastructure": [
        "classroom", "lab", "computer", "wifi",
        "internet", "projector", "facility"
    ],
    "Assessment": [
        "exam", "test", "marks", "assignment", "grading"
    ],
    "Student Support": [
        "support", "doubt", "help", "guidance"
    ]
}

SUGGESTIONS = {
    "Teaching": "Improve explanations and include practical examples.",
    "Course Content": "Review the syllabus and provide updated notes.",
    "Infrastructure": "Inspect laboratory equipment and internet facilities.",
    "Assessment": "Clarify marking criteria and provide timely feedback.",
    "Student Support": "Arrange doubt-solving sessions for students."
}


def analyze_feedback(feedback):
    feedback = feedback.strip()

    if not feedback:
        return {
            "sentiment": "Neutral",
            "score": 0,
            "topics": ["General"],
            "suggestions": ["Please enter feedback."]
        }

    score = model.polarity_scores(feedback)["compound"]

    if score >= 0.05:
        sentiment = "Positive"
    elif score <= -0.05:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    text = feedback.lower()

    topics = [
        topic for topic, keywords in TOPICS.items()
        if any(word in text for word in keywords)
    ]

    if not topics:
        topics = ["General"]

    if sentiment == "Negative":
        suggestions = [
            SUGGESTIONS[topic]
            for topic in topics if topic in SUGGESTIONS
        ]

        if not suggestions:
            suggestions = [
                "Review the comment to identify the specific issue."
            ]

    elif sentiment == "Positive":
        suggestions = [
            "Continue the practices students appreciate."
        ]

    else:
        suggestions = [
            "Collect more detailed feedback to understand the experience."
        ]

    return {
        "sentiment": sentiment,
        "score": round(score, 3),
        "topics": topics,
        "suggestions": suggestions
    }


def analyze_all_feedback(feedback_list):
    results = []

    for feedback in feedback_list:
        results.append({
            "feedback": feedback,
            **analyze_feedback(feedback)
        })

    counts = Counter(
        item["sentiment"] for item in results
    )

    total = len(results)

    percentages = {
        sentiment: round(counts.get(sentiment, 0) * 100 / total, 1)
        if total else 0
        for sentiment in ["Positive", "Negative", "Neutral"]
    }

    topic_counts = Counter(
        topic
        for item in results
        for topic in item["topics"]
    )

    return {
        "total": total,
        "counts": dict(counts),
        "percentages": percentages,
        "topic_counts": dict(topic_counts),
        "results": results
    }