import llm_utils
import json
import os
from dotenv import load_dotenv

load_dotenv()

mock_context = {
    "parentProfile": {"name": "Rajeev", "parentId": "parent123"},
    "schoolContext": {
        "website": {
            "hero": {"title": "Excellence in Education"},
            "about": {"message": "We empower students for the future."}
        },
        "events": [
            {"Subject": "Annual Sports Day", "StartTime": "2026-03-15T09:00:00Z"}
        ]
    },
    "knowledge_base": {
        "policies": {
            "uniform": "Navy blue blazers are mandatory."
        }
    },
    "children": [
        {
            "profile": {"studentName": "Peeyush", "class": "10", "section": "A"},
            "attendance": [{"status": "Present", "date": "2026-02-01"}, {"status": "Absent", "date": "2026-02-02"}],
            "marks": [
                {"subject": "Math", "marks": 85, "totalMarks": 100},
                {"subject": "Science", "marks": 78, "totalMarks": 100}
            ],
            "exams": [
                {"name": "Final Term", "startDate": "2026-03-01"}
            ]
        }
    ]
}

def test_bot():
    print("Testing 'How is my kid doing?'...")
    resp = llm_utils.generate_bot_response("How is my kid doing?", mock_context)
    print(f"Response:\n{resp}\n")

    print("Testing policy query: 'What is the uniform policy?'...")
    resp = llm_utils.generate_bot_response("What is the uniform policy?", mock_context)
    print(f"Response:\n{resp}\n")

    print("Testing task automation: 'Draft an email to the teacher about Peeyush's absence on Feb 2nd.'")
    resp = llm_utils.generate_bot_response("Draft an email to the teacher about Peeyush's absence on Feb 2nd.", mock_context)
    print(f"Response:\n{resp}\n")

if __name__ == "__main__":
    test_bot()
