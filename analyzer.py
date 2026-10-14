
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from collections import Counter

model = SentimentIntensityAnalyzer()

SENTIMENTS = [
    "Very Positive",
    "Positive",
    "Neutral",
    "Negative",
    "Very Negative"
]

TOPICS = {
    "Teaching": [
        "teacher", "teaching", "lecture", "explanation",
        "explain", "understand", "professor", "faculty"
    ],
    "Course Content": [
        "syllabus", "course", "notes", "study material",
        "curriculum", "subject"
    ],
    "Infrastructure": [
        "classroom", "lab", "computer", "wifi",
        "internet", "projector", "facility", "building"
    ],
    "Assessment": [
        "exam", "test", "marks", "assignment",
        "grading", "question paper", "result"
    ],
    "Student Support": [
        "support", "doubt", "help", "guidance",
        "counselling", "counseling"
    ],
    "Placements": [
        "placement", "job", "career", "company",
        "interview", "internship", "recruitment"
    ],
    "Practical Learning": [
        "practical", "project", "workshop",
        "hands-on", "experiment", "coding"
    ]
}

SUGGESTIONS = {
    "Teaching": "Improve explanations and include practical examples.",
    "Course Content": "Review the syllabus and provide updated study material.",
    "Infrastructure": "Inspect laboratory equipment, classrooms, and internet facilities.",
    "Assessment": "Clarify marking criteria and provide timely feedback.",
    "Student Support": "Arrange regular doubt-solving and mentoring sessions.",
    "Placements": "Organize placement training, mock interviews, and career guidance.",
    "Practical Learning": "Include more hands-on activities, projects, and practical sessions."
}


def analyze_feedback(feedback):
    feedback = feedback.strip()

    if not feedback:
        return {
            "sentiment": "Neutral",
            "score": 0.0,
            "topics": ["General"],
            "suggestions": ["Please enter feedback."]
        }

    score = model.polarity_scores(feedback)["compound"]

    # Five-level sentiment classification
    if score >= 0.50:
        sentiment = "Very Positive"
    elif score >= 0.05:
        sentiment = "Positive"
    elif score > -0.05:
        sentiment = "Neutral"
    elif score > -0.50:
        sentiment = "Negative"
    else:
        sentiment = "Very Negative"

    text = feedback.lower()

    # Identify topics mentioned in the feedback
    topics = [
        topic
        for topic, keywords in TOPICS.items()
        if any(word in text for word in keywords)
    ]

    if not topics:
        topics = ["General"]

    # Generate improvement suggestions
    if sentiment in ["Negative", "Very Negative"]:
        suggestions = [
            SUGGESTIONS[topic]
            for topic in topics
            if topic in SUGGESTIONS
        ]

        if not suggestions:
            suggestions = [
                "Review this feedback carefully and identify the specific issue."
            ]

    elif sentiment in ["Positive", "Very Positive"]:
        suggestions = [
            "Continue the practices students appreciate and maintain quality."
        ]

        suggestions.extend([
            SUGGESTIONS[topic]
            for topic in topics
            if topic in SUGGESTIONS
        ])

    else:
        suggestions = [
            "Collect more detailed feedback to understand students' experiences."
        ]

        suggestions.extend([
            SUGGESTIONS[topic]
            for topic in topics
            if topic in SUGGESTIONS
        ])

    return {
        "sentiment": sentiment,
        "score": round(score, 3),
        "topics": topics,
        "suggestions": list(dict.fromkeys(suggestions))
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

    # Always provide all five categories, including zero counts
    all_counts = {
        sentiment: counts.get(sentiment, 0)
        for sentiment in SENTIMENTS
    }

    percentages = {
        sentiment: round(
            all_counts[sentiment] * 100 / total, 1
        ) if total else 0
        for sentiment in SENTIMENTS
    }

    topic_counts = Counter(
        topic
        for item in results
        for topic in item["topics"]
    )

    return {
        "total": total,
        "counts": all_counts,
        "percentages": percentages,
        "topic_counts": dict(topic_counts),
        "results": results
    }
