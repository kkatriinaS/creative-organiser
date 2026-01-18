from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="x",
        database="creative_organiser"
    )

app = Flask(__name__)

PROJECT_TYPES = [
    "Branding",
    "Illustration",
    "Web Design",
    "UI/UX",
    "Logo",
    "Social media post",
    "Poster",
    "Other"
]

STATUSES = [
    "Idea",
    "In progress",
    "Awaiting feedback",
    "Done"
]



@app.route("/")
def dashboard():
    search = request.args.get("search", "")
    sort = request.args.get("sort", "name")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    query = "SELECT * FROM projects_database"
    params = []

    if search:
        query += " WHERE name LIKE %s"
        params.append(f"%{search}%")

    if sort == "deadline":
        query += " ORDER BY deadline"
    else:
        query += " ORDER BY name"

    cursor.execute(query, params)
    projects = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("dashboard.html", projects=projects, search=search, sort=sort)




@app.route("/new", methods=["GET", "POST"])
def new_project():
    if request.method == "POST":
        db = get_db_connection()
        cursor = db.cursor()

        status = request.form["status"]
        project_type = request.form["type"]


        
        cursor.execute("""
            INSERT INTO projects_database (name, type, status, deadline, notes, links)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            request.form["name"],
            project_type,
            status,
            request.form["deadline"] or None,
            request.form["notes"],
            request.form["links"]
        ))

        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for("dashboard"))

    return render_template(
        "new_project.html",
        types=PROJECT_TYPES,
        statuses=STATUSES
    )







@app.route("/board")
def board():
    statuses = ["Idea", "In progress", "Awaiting feedback", "Done"]
    columns = {status: [] for status in statuses}

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM projects_database")
    projects = cursor.fetchall()

    for project in projects:
        columns[project["status"]].append(project)

    cursor.close()
    db.close()

    return render_template("board.html", columns=columns)

@app.route("/project/<int:project_id>")
def project_detail(project_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM projects_database WHERE id = %s",
        (project_id,)
    )
    project = cursor.fetchone()

    cursor.close()
    db.close()

    if not project:
        return "Project not found", 404

    return render_template("project_detail.html", project=project)

@app.route("/edit/<int:project_id>", methods=["GET", "POST"])
def edit_project(project_id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        cursor.execute("""
            UPDATE projects_database
            SET name = %s,
                type = %s,
                status = %s,
                deadline = %s,
                notes = %s,
                links = %s
            WHERE id = %s
        """, (
            request.form["name"],
            request.form["type"],
            request.form["status"],
            request.form["deadline"] or None,
            request.form["notes"],
            request.form["links"],
            project_id
        ))

        db.commit()
        cursor.close()
        db.close()

        return redirect(url_for("project_detail", project_id=project_id))

    
    cursor.execute(
        "SELECT * FROM projects_database WHERE id = %s",
        (project_id,)
    )
    project = cursor.fetchone()

    cursor.close()
    db.close()

    if not project:
        return "Project not found", 404

    return render_template(
        "edit_project.html",
        project=project,
        types=PROJECT_TYPES,
        statuses=STATUSES
    )

    



if __name__ == "__main__":

    app.run(debug=True)
