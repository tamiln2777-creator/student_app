from flask import Flask, render_template, request, abort
import os, json, glob

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

def list_sets_for_subject(subject_prefix):
    pattern = os.path.join(DATA_DIR, f"{subject_prefix}*.json")
    files = sorted(glob.glob(pattern))
    return [os.path.splitext(os.path.basename(f))[0] for f in files]

def load_questions(set_basename):
    path = os.path.join(DATA_DIR, f"{set_basename}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    questions = []
    for i, q in enumerate(data, start=1):
        questions.append({
            "id": i,
            "question": q.get("question", ""),
            "options": q.get("options", []),
            "answer": q.get("answer", "")
        })
    return questions

@app.route("/")
def index():
    return render_template("index.html", page="home")

@app.route("/subject/<subject>")
def show_sets(subject):
    subject = subject.lower()
    if subject == "english":
        sets = list_sets_for_subject("english_synonyms_set")
        display_sets = [f"Synonyms Set {i+1}" for i in range(len(sets))]
    elif subject == "maths":
        sets = list_sets_for_subject("maths_set")
        display_sets = [f"Maths Set {i+1}" for i in range(len(sets))]
    else:
        abort(404)

    combined_sets = list(zip(sets, display_sets))
    return render_template("index.html", page="sets", subject=subject.capitalize(), combined_sets=combined_sets)

@app.route("/quiz/<setname>", methods=["GET", "POST"])
def quiz(setname):
    questions = load_questions(setname)
    if not questions:
        abort(404)

    if request.method == "POST":
        user_answers = {f"q_{q['id']}": request.form.get(f"q_{q['id']}") for q in questions}
        correct = 0
        details = []

        for q in questions:
            user_ans = user_answers.get(f"q_{q['id']}")
            is_correct = (user_ans == q["answer"])
            if is_correct:
                correct += 1
            details.append({
                "id": q["id"],
                "question": q["question"],
                "options": q["options"],
                "user_answer": user_ans,
                "correct_answer": q["answer"],
                "is_correct": is_correct
            })

        total = len(questions)
        return render_template("index.html", page="result", setname=setname, total=total, score=correct, details=details)
    else:
        return render_template("index.html", page="quiz", setname=setname, questions=questions)

if __name__ == "__main__":
    app.run(debug=True)
