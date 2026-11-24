from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
from pathlib import Path
import json

app = Flask(__name__)
app.secret_key = "voconova-local-development-key"


STREAMS = ["Science (PCM)", "Science (PCB)", "Commerce", "Arts / Humanities", "Other / Diploma"]
INTERESTS = ["Artificial Intelligence", "Data and numbers", "Art and design", "Websites and apps",
             "Cyber security", "Games", "Software and coding", "Cloud and networks",
             "Business and finance", "Marketing and media", "Understanding people and behaviour",
             "Healthcare and medicine", "Science and research", "Law and justice",
             "Teaching and education", "Writing and journalism", "Public service",
             "Building and architecture", "Travel and hospitality", "Sports and fitness"]
SUBJECTS = ["Mathematics", "Computer Science", "Art and Design", "English", "Physics",
            "Economics", "Business Studies", "Biology", "Chemistry", "History",
            "Political Science", "Accountancy", "Psychology", "Physical Education"]
SKILLS = ["Programming", "Analytical thinking", "Creativity", "Communication", "Problem solving",
          "Leadership", "Writing and storytelling", "Attention to detail", "Public speaking",
          "Research", "Empathy and caring", "Numerical ability", "Organising and planning",
          "Physical fitness"]
WORK_STYLES = ["Independent work", "Team work", "Working with people", "Leading and planning",
               "Fieldwork and outdoor work", "Lab and research work"]
PREFERENCES = ["Research and innovation", "Building products and apps", "Creative work",
               "Security and protection", "Helping businesses grow", "Stable and well-paid jobs",
               "Serving society", "Government jobs", "Starting my own business",
               "Travel and meeting people"]

WEIGHTS = {"stream": 10, "interest": 25, "subject": 20,
           "skill": 25, "style": 10, "preference": 10}

MIN_SCORE = 40

# Text file where every student's result is saved
REPORT_FILE = "results.txt"

CAREERS = {
    "AI/ML Engineer": {
        "stream": ["Science (PCM)"],
        "interest": ["Artificial Intelligence", "Data and numbers"],
        "subject": ["Mathematics", "Computer Science"],
        "skill": ["Programming", "Analytical thinking", "Problem solving"],
        "style": ["Independent work", "Team work"],
        "preference": ["Research and innovation", "Building products and apps"],
        "degrees": ["B.Tech in CSE (AI/ML)", "M.Tech in Artificial Intelligence"],
        "skills_needed": ["Python", "Maths and statistics", "Machine learning"],
        "path": ["Learn Python and maths", "Study machine learning", "Build projects",
                 "Junior ML Engineer", "Senior AI/ML Engineer"],
    },
    "Data Scientist": {
        "stream": ["Science (PCM)", "Commerce"],
        "interest": ["Data and numbers", "Artificial Intelligence"],
        "subject": ["Mathematics", "Computer Science", "Economics"],
        "skill": ["Analytical thinking", "Communication", "Attention to detail", "Numerical ability"],
        "style": ["Independent work", "Team work"],
        "preference": ["Research and innovation"],
        "degrees": ["B.Tech in CSE", "B.Sc in Statistics or Data Science"],
        "skills_needed": ["Statistics", "Python and SQL", "Data visualisation"],
        "path": ["Learn Python and statistics", "Practise on datasets", "Data Analyst",
                 "Data Scientist", "Senior Data Scientist"],
    },
    "Software Engineer": {
        "stream": ["Science (PCM)", "Commerce"],
        "interest": ["Software and coding", "Websites and apps"],
        "subject": ["Computer Science", "Mathematics"],
        "skill": ["Programming", "Problem solving"],
        "style": ["Team work", "Independent work", "Leading and planning"],
        "preference": ["Building products and apps", "Stable and well-paid jobs"],
        "degrees": ["B.Tech in CSE or IT", "BCA then MCA"],
        "skills_needed": ["A language like Python or Java", "Data structures", "Git and testing"],
        "path": ["Learn programming basics", "Master data structures", "Build projects",
                 "Junior Software Engineer", "Senior Engineer or Tech Lead"],
    },
    "Web Developer": {
        "stream": ["Science (PCM)", "Commerce", "Arts / Humanities", "Other / Diploma",
                   "Science (PCB)"],
        "interest": ["Websites and apps", "Art and design", "Software and coding"],
        "subject": ["Computer Science", "Art and Design"],
        "skill": ["Programming", "Creativity"],
        "style": ["Team work", "Independent work"],
        "preference": ["Building products and apps"],
        "degrees": ["B.Tech in CSE or IT", "BCA"],
        "skills_needed": ["HTML, CSS, JavaScript", "A framework like React", "Git"],
        "path": ["Learn HTML, CSS, JavaScript", "Learn a framework", "Build a portfolio site",
                 "Junior Web Developer", "Full-Stack Developer"],
    },
    "Cybersecurity Analyst": {
        "stream": ["Science (PCM)"],
        "interest": ["Cyber security", "Cloud and networks"],
        "subject": ["Computer Science", "Mathematics"],
        "skill": ["Problem solving", "Analytical thinking", "Attention to detail"],
        "style": ["Independent work"],
        "preference": ["Security and protection"],
        "degrees": ["B.Tech in CSE (Cyber Security)", "M.Tech in Information Security"],
        "skills_needed": ["Networking and Linux", "Cryptography basics", "Ethical hacking tools"],
        "path": ["Learn networking and Linux", "Study cryptography", "Practise on TryHackMe",
                 "Get Security+ certified", "Security Engineer"],
    },
    "Game Developer": {
        "stream": ["Science (PCM)", "Arts / Humanities", "Other / Diploma", "Science (PCB)"],
        "interest": ["Games", "Art and design", "Software and coding"],
        "subject": ["Computer Science", "Physics", "Art and Design"],
        "skill": ["Programming", "Creativity"],
        "style": ["Team work"],
        "preference": ["Creative work", "Building products and apps"],
        "degrees": ["B.Tech in CSE", "B.Sc in Game Design"],
        "skills_needed": ["C# with Unity or C++", "Game maths and physics", "Storytelling"],
        "path": ["Learn C# and Unity", "Build small 2D games", "Join a game jam",
                 "Junior Game Developer", "Lead Game Developer"],
    },
    "UI/UX Designer": {
        "stream": ["Science (PCM)", "Commerce", "Arts / Humanities", "Other / Diploma",
                   "Science (PCB)"],
        "interest": ["Art and design", "Websites and apps"],
        "subject": ["Art and Design", "English"],
        "skill": ["Creativity", "Communication"],
        "style": ["Team work", "Working with people"],
        "preference": ["Creative work"],
        "degrees": ["B.Des in UX Design", "BA in Design"],
        "skills_needed": ["Design principles", "Figma", "User research"],
        "path": ["Learn design basics", "Practise with Figma", "Build a portfolio",
                 "Junior Designer", "Senior Designer"],
    },
    "Cloud Engineer": {
        "stream": ["Science (PCM)"],
        "interest": ["Cloud and networks", "Software and coding"],
        "subject": ["Computer Science", "Physics"],
        "skill": ["Problem solving", "Attention to detail"],
        "style": ["Team work", "Independent work"],
        "preference": ["Stable and well-paid jobs", "Building products and apps"],
        "degrees": ["B.Tech in CSE or IT", "Cloud certification (AWS, Azure)"],
        "skills_needed": ["Linux and networking", "A cloud platform", "Scripting"],
        "path": ["Learn Linux and networking", "Learn AWS or Azure basics",
                 "Get a cloud certification", "Junior Cloud Engineer",
                 "DevOps or Cloud Architect"],
    },
    "Business Analyst": {
        "stream": ["Commerce", "Science (PCM)", "Arts / Humanities", "Science (PCB)"],
        "interest": ["Business and finance", "Data and numbers"],
        "subject": ["Economics", "Business Studies", "Mathematics", "Accountancy"],
        "skill": ["Analytical thinking", "Communication", "Leadership", "Numerical ability"],
        "style": ["Working with people", "Leading and planning", "Team work"],
        "preference": ["Helping businesses grow", "Stable and well-paid jobs"],
        "degrees": ["BBA or B.Com", "MBA in Business Analytics"],
        "skills_needed": ["Excel and SQL", "Data storytelling", "Communication"],
        "path": ["Learn Excel and SQL", "Study business basics", "Intern as Analyst",
                 "Business Analyst", "Product or Strategy Manager"],
    },
    "Digital Marketer": {
        "stream": ["Commerce", "Arts / Humanities", "Science (PCM)", "Other / Diploma",
                   "Science (PCB)"],
        "interest": ["Marketing and media", "Art and design", "Business and finance"],
        "subject": ["English", "Business Studies", "Art and Design"],
        "skill": ["Creativity", "Communication", "Writing and storytelling"],
        "style": ["Team work", "Working with people", "Leading and planning"],
        "preference": ["Creative work", "Helping businesses grow"],
        "degrees": ["BBA in Marketing", "BA in Mass Communication"],
        "skills_needed": ["Social media and SEO", "Content writing", "Analytics tools"],
        "path": ["Learn SEO and social media", "Create content", "Run small campaigns",
                 "Marketing Executive", "Marketing Manager"],
    },
    "Doctor": {
        "stream": ["Science (PCB)"],
        "interest": ["Healthcare and medicine", "Science and research"],
        "subject": ["Biology", "Chemistry"],
        "skill": ["Empathy and caring", "Problem solving", "Attention to detail"],
        "style": ["Working with people", "Team work"],
        "preference": ["Serving society", "Stable and well-paid jobs"],
        "degrees": ["MBBS", "MD or MS after MBBS"],
        "skills_needed": ["Biology and anatomy", "Patience and empathy", "Quick decision making"],
        "path": ["Clear NEET", "Complete MBBS", "Internship", "Postgraduate specialisation",
                 "Doctor or Specialist"],
    },
    "Psychologist": {
        "stream": ["Arts / Humanities", "Science (PCB)", "Commerce"],
        "interest": ["Understanding people and behaviour", "Healthcare and medicine"],
        "subject": ["Psychology", "Biology", "English"],
        "skill": ["Empathy and caring", "Communication", "Research"],
        "style": ["Working with people", "Independent work"],
        "preference": ["Serving society"],
        "degrees": ["BA or BSc in Psychology", "MA or MSc in Clinical Psychology"],
        "skills_needed": ["Listening and counselling", "Research methods", "Ethics"],
        "path": ["Study psychology", "Complete a masters", "Supervised internship",
                 "Licensed Psychologist", "Clinical, child or counselling specialist"],
    },
    "Biotech Researcher": {
        "stream": ["Science (PCB)", "Science (PCM)"],
        "interest": ["Science and research", "Healthcare and medicine"],
        "subject": ["Biology", "Chemistry"],
        "skill": ["Research", "Analytical thinking", "Attention to detail"],
        "style": ["Lab and research work", "Independent work"],
        "preference": ["Research and innovation"],
        "degrees": ["BSc or B.Tech in Biotechnology", "MSc then PhD"],
        "skills_needed": ["Lab techniques", "Data analysis", "Scientific writing"],
        "path": ["Study biotechnology", "Do lab internships", "Complete a masters",
                 "Research Associate", "Scientist"],
    },
    "Chartered Accountant": {
        "stream": ["Commerce"],
        "interest": ["Business and finance", "Data and numbers"],
        "subject": ["Accountancy", "Economics", "Business Studies", "Mathematics"],
        "skill": ["Numerical ability", "Attention to detail", "Analytical thinking"],
        "style": ["Independent work", "Team work"],
        "preference": ["Stable and well-paid jobs", "Helping businesses grow"],
        "degrees": ["CA from ICAI", "B.Com along with CA"],
        "skills_needed": ["Accounting and taxation", "Auditing", "Excel"],
        "path": ["Register for CA Foundation", "Clear Intermediate", "Articleship training",
                 "Clear Final", "Practising CA or Finance Head"],
    },
    "Lawyer": {
        "stream": ["Arts / Humanities", "Commerce"],
        "interest": ["Law and justice", "Public service"],
        "subject": ["Political Science", "English", "History"],
        "skill": ["Public speaking", "Research", "Communication", "Analytical thinking"],
        "style": ["Independent work", "Working with people"],
        "preference": ["Serving society", "Stable and well-paid jobs"],
        "degrees": ["BA LLB or BBA LLB", "LLM"],
        "skills_needed": ["Legal research", "Argument and speaking", "Writing"],
        "path": ["Clear CLAT or similar exam", "Complete a law degree", "Intern with a lawyer",
                 "Enrol with the Bar Council", "Advocate or Legal Advisor"],
    },
    "Teacher or Professor": {
        "stream": ["Science (PCM)", "Science (PCB)", "Commerce", "Arts / Humanities",
                   "Other / Diploma"],
        "interest": ["Teaching and education"],
        "subject": ["English", "Mathematics", "History", "Biology"],
        "skill": ["Communication", "Public speaking", "Empathy and caring",
                  "Organising and planning"],
        "style": ["Working with people", "Leading and planning"],
        "preference": ["Serving society", "Government jobs", "Stable and well-paid jobs"],
        "degrees": ["B.Ed after graduation", "MA or MSc then NET for lecturers"],
        "skills_needed": ["Subject knowledge", "Clear explanation", "Patience"],
        "path": ["Complete graduation", "Do B.Ed", "Clear CTET or NET", "Teacher or Lecturer",
                 "Head of Department or Principal"],
    },
    "Journalist": {
        "stream": ["Arts / Humanities", "Commerce", "Other / Diploma"],
        "interest": ["Writing and journalism", "Marketing and media"],
        "subject": ["English", "History", "Political Science"],
        "skill": ["Writing and storytelling", "Communication", "Research"],
        "style": ["Independent work", "Fieldwork and outdoor work"],
        "preference": ["Creative work", "Serving society", "Travel and meeting people"],
        "degrees": ["BA in Journalism and Mass Communication", "PG Diploma in Journalism"],
        "skills_needed": ["Reporting", "Writing and editing", "Digital media"],
        "path": ["Practise writing", "Study mass communication", "Intern at a news outlet",
                 "Reporter or Content Writer", "Editor"],
    },
    "Civil Services Officer": {
        "stream": ["Arts / Humanities", "Commerce", "Science (PCM)", "Science (PCB)"],
        "interest": ["Public service", "Law and justice"],
        "subject": ["Political Science", "History", "Economics"],
        "skill": ["Leadership", "Analytical thinking", "Communication",
                  "Organising and planning"],
        "style": ["Leading and planning", "Fieldwork and outdoor work"],
        "preference": ["Serving society", "Government jobs"],
        "degrees": ["Any graduation degree", "MA in Public Administration"],
        "skills_needed": ["General knowledge", "Decision making", "Writing"],
        "path": ["Complete graduation", "Prepare for UPSC", "Clear Prelims, Mains and Interview",
                 "Training at the academy", "IAS, IPS or IFS Officer"],
    },
    "Architect": {
        "stream": ["Science (PCM)"],
        "interest": ["Building and architecture", "Art and design"],
        "subject": ["Mathematics", "Art and Design", "Physics"],
        "skill": ["Creativity", "Numerical ability", "Attention to detail"],
        "style": ["Independent work", "Team work"],
        "preference": ["Creative work", "Building products and apps"],
        "degrees": ["B.Arch after NATA", "M.Arch"],
        "skills_needed": ["Design drawing", "AutoCAD and 3D tools", "Building basics"],
        "path": ["Clear NATA", "Complete B.Arch", "Intern at a firm", "Junior Architect",
                 "Licensed Architect"],
    },
    "Hotel and Tourism Manager": {
        "stream": ["Commerce", "Arts / Humanities", "Other / Diploma", "Science (PCM)"],
        "interest": ["Travel and hospitality", "Business and finance"],
        "subject": ["English", "Business Studies"],
        "skill": ["Communication", "Leadership", "Organising and planning"],
        "style": ["Working with people", "Leading and planning"],
        "preference": ["Travel and meeting people", "Helping businesses grow"],
        "degrees": ["BHM in Hotel Management", "BBA in Tourism"],
        "skills_needed": ["Customer service", "Event and team management", "Communication"],
        "path": ["Study hotel management", "Intern at a hotel", "Front Office Executive",
                 "Department Manager", "General Manager"],
    },
    "Fitness Coach": {
        "stream": ["Other / Diploma", "Science (PCB)", "Arts / Humanities", "Commerce"],
        "interest": ["Sports and fitness", "Healthcare and medicine"],
        "subject": ["Physical Education", "Biology"],
        "skill": ["Physical fitness", "Empathy and caring", "Leadership"],
        "style": ["Working with people", "Fieldwork and outdoor work"],
        "preference": ["Starting my own business", "Travel and meeting people",
                       "Serving society"],
        "degrees": ["BPEd or BSc in Sports Science", "Fitness trainer certification"],
        "skills_needed": ["Exercise and nutrition basics", "Motivating others", "First aid"],
        "path": ["Study sports science", "Get certified", "Assistant Trainer", "Certified Coach",
                 "Own gym or academy"],
    },
    "Fashion or Graphic Designer": {
        "stream": ["Arts / Humanities", "Other / Diploma", "Commerce", "Science (PCM)"],
        "interest": ["Art and design", "Marketing and media"],
        "subject": ["Art and Design", "English"],
        "skill": ["Creativity", "Attention to detail"],
        "style": ["Independent work", "Team work"],
        "preference": ["Creative work", "Starting my own business"],
        "degrees": ["B.Des in Fashion or Communication Design", "Diploma in Graphic Design"],
        "skills_needed": ["Design software", "Colour and typography", "Portfolio building"],
        "path": ["Learn design basics", "Master design software", "Build a portfolio",
                 "Junior Designer", "Senior Designer or own studio"],
    },
}

REPORT_FILE = Path(__file__).with_name("results.txt")
DATA_FILE = Path(__file__).with_name("assessments.json")


def get_matches(profile, career, category):
    """Chosen options of one category that suit this career."""
    matched = []
    for option in profile[category]:
        if option in career[category]:
            matched.append(option)
    return matched


def calculate_score(profile, career):
    """Match score out of 100 using the original category weights."""
    score = 0
    for category in WEIGHTS:
        matches = len(get_matches(profile, career, category))
        score = score + WEIGHTS[category] * matches / len(profile[category])
    return round(score, 1)


def sort_results(results):
    """Original Bubble Sort: highest score first. Items are [career, score]."""
    n = len(results)
    for i in range(n - 1):
        for j in range(n - 1 - i):
            if results[j][1] < results[j + 1][1]:
                temp = results[j]
                results[j] = results[j + 1]
                results[j + 1] = temp
    return results


def score_all_careers(profile):
    """Score every career and return [career, score] sorted best first."""
    results = []
    for name in CAREERS:
        results.append([name, calculate_score(profile, CAREERS[name])])
    return sort_results(results)


#SAVING ASSESSMENTs
def read_assessments():
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return []


def save_assessment(name, profile, results):
    records = read_assessments()
    matches = []
    for i in range(3):
        if results[i][1] >= MIN_SCORE:
            matches.append({"name": results[i][0], "score": results[i][1]})
    records.insert(0, {
        "name": name,
        "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "profile": profile,
        "matches": matches
    })
    DATA_FILE.write_text(json.dumps(records, indent=2), encoding="utf-8")

    with REPORT_FILE.open("a", encoding="utf-8") as file:
        file.write("Name: " + name + "\n")
        for category in WEIGHTS:
            file.write("  " + category + ": " + ", ".join(profile[category]) + "\n")
        file.write("Matches:\n")
        for i in range(3):
            if results[i][1] >= MIN_SCORE:
                file.write("  " + str(i + 1) + ". " + results[i][0] +
                           " (" + str(results[i][1]) + "%)\n")
        file.write("-" * 40 + "\n")


@app.context_processor
def inject_globals():
    return {"career_count": len(CAREERS)}


@app.route("/")
def dashboard():
    records = read_assessments()
    recent = records[:4]
    all_matches = []
    for record in records:
        for match in record.get("matches", []):
            all_matches.append(match)
    top_career = None
    for match in all_matches:
        if top_career is None or match["score"] > top_career["score"]:
            top_career = match
    return render_template("dashboard.html", records=records, recent=recent,
                           top_career=top_career, career_count=len(CAREERS),
                           assessment_count=len(records), streams=STREAMS)


@app.route("/assessment")
def assessment():
    return render_template("index.html", streams=STREAMS, interests=INTERESTS,
                           subjects=SUBJECTS, skills=SKILLS, work_styles=WORK_STYLES,
                           preferences=PREFERENCES, min_score=MIN_SCORE)


@app.route("/recommend", methods=["POST"])
def recommend():
    name = request.form.get("name", "").strip()
    if name == "":
        name = "Anonymous"

    profile = {}
    profile["stream"] = [request.form.get("stream", "")]
    profile["interest"] = request.form.getlist("interest")
    profile["subject"] = request.form.getlist("subject")
    profile["skill"] = request.form.getlist("skill")
    profile["style"] = request.form.getlist("style")
    profile["preference"] = request.form.getlist("preference")

    if not profile["stream"][0] or any(not profile[key] for key in WEIGHTS if key != "stream"):
        flash("Please complete every section before generating your career matches.")
        return redirect(url_for("assessment"))

#sorting
    raw_results = score_all_careers(profile)
    suitable = []
    for item in raw_results:
        if item[1] >= MIN_SCORE and len(suitable) < 3:
            suitable.append({
                "name": item[0],
                "score": item[1],
                "career": CAREERS[item[0]]
            })

    if suitable:
        save_assessment(name, profile, raw_results)

    top_score = raw_results[0][1] if raw_results else 0
    return render_template("results.html", name=name, profile=profile,
                           results=suitable, top_score=top_score,
                           min_score=MIN_SCORE, weights=WEIGHTS,
                           no_match=not bool(suitable))


@app.route("/careers")
def careers():
    query = request.args.get("q", "").strip().lower()
    category = request.args.get("category", "")
    items = []
    for name, data in CAREERS.items():
        searchable = " ".join([name] + data["degrees"] + data["skills_needed"] + data["interest"])
        if query and query not in searchable.lower():
            continue
        if category and category not in data["interest"]:
            continue
        items.append({"name": name, "data": data})
    return render_template("careers.html", careers=items, query=query,
                           interests=INTERESTS, category=category)


@app.route("/career/<path:name>")
def career_detail(name):
    data = CAREERS.get(name)
    if not data:
        return redirect(url_for("careers"))
    return render_template("career_detail.html", name=name, career=data)


@app.route("/saved")
def saved():
    return render_template("saved.html", records=read_assessments())


@app.route("/about")
def about():
    return render_template("about.html", weights=WEIGHTS, career_count=len(CAREERS))

if __name__ == "__main__":
    app.run(debug=True)
