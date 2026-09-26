from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
import random
import io
import os
import secrets

from werkzeug.security import generate_password_hash, check_password_hash

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from xml.sax.saxutils import escape


# ==========================================
# FLASK APPLICATION
# ==========================================

app = Flask(__name__)

# Secure session secret
# You can later set COLLEGE_SECRET_KEY as an environment variable.
app.secret_key = os.environ.get(
    "COLLEGE_SECRET_KEY",
    secrets.token_hex(32)
)

DATABASE = "database.db"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_db_connection():

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    return connection


# ==========================================
# CREATE DATABASE
# ==========================================

def create_database():

    connection = get_db_connection()

    # --------------------------------------
    # APPLICATIONS TABLE
    # --------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS applications (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            application_number TEXT UNIQUE,

            student_name TEXT NOT NULL,

            dob TEXT NOT NULL,

            gender TEXT NOT NULL,

            mobile TEXT NOT NULL,

            email TEXT NOT NULL,

            address TEXT NOT NULL,

            district TEXT NOT NULL,

            state TEXT NOT NULL,

            pincode TEXT NOT NULL,

            school TEXT NOT NULL,

            tenth REAL NOT NULL,

            twelfth REAL NOT NULL,

            group_name TEXT NOT NULL,

            course TEXT NOT NULL,

            parent_name TEXT NOT NULL,

            parent_mobile TEXT NOT NULL,

            status TEXT DEFAULT 'Submitted'

        )
    """)


    # --------------------------------------
    # ADMIN USERS TABLE
    # --------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS admin_users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL

        )
    """)


    # --------------------------------------
    # CREATE DEFAULT ADMIN
    # --------------------------------------

    admin = connection.execute(
        """
        SELECT *
        FROM admin_users
        WHERE username = ?
        """,
        ("admin",)
    ).fetchone()


    # Create admin only if it does not already exist
    if admin is None:

        hashed_password = generate_password_hash("admin123")

        connection.execute(
            """
            INSERT INTO admin_users (
                username,
                password
            )
            VALUES (?, ?)
            """,
            (
                "admin",
                hashed_password
            )
        )


    connection.commit()

    connection.close()


# ==========================================
# GENERATE APPLICATION NUMBER
# ==========================================

def generate_application_number():

    number = random.randint(10000, 99999)

    return "APP2026" + str(number)


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():

    return render_template("index.html")


# ==========================================
# SUBMIT ADMISSION APPLICATION
# ==========================================

@app.route("/submit", methods=["POST"])
def submit_application():

    student_name = request.form["studentName"]

    dob = request.form["dob"]

    gender = request.form["gender"]

    mobile = request.form["mobile"]

    email = request.form["email"]

    address = request.form["address"]

    district = request.form["district"]

    state = request.form["state"]

    pincode = request.form["pincode"]

    school = request.form["school"]

    tenth = request.form["tenth"]

    twelfth = request.form["twelfth"]

    group_name = request.form["group"]

    course = request.form["course"]

    parent_name = request.form["parentName"]

    parent_mobile = request.form["parentMobile"]


    # Generate application number
    application_number = generate_application_number()


    # Connect to database
    connection = get_db_connection()


    # Insert application
    connection.execute("""
        INSERT INTO applications (

            application_number,

            student_name,

            dob,

            gender,

            mobile,

            email,

            address,

            district,

            state,

            pincode,

            school,

            tenth,

            twelfth,

            group_name,

            course,

            parent_name,

            parent_mobile

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

    """, (

        application_number,

        student_name,

        dob,

        gender,

        mobile,

        email,

        address,

        district,

        state,

        pincode,

        school,

        tenth,

        twelfth,

        group_name,

        course,

        parent_name,

        parent_mobile

    ))


    connection.commit()

    connection.close()


    # --------------------------------------
    # SUCCESS PAGE
    # --------------------------------------

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <title>Application Submitted</title>

        <style>

            body {{
                font-family: Arial, sans-serif;
                background: #f2f6ff;
                text-align: center;
                padding: 80px 20px;
            }}

            .box {{
                background: white;
                padding: 40px;
                max-width: 600px;
                margin: auto;
                border-radius: 10px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            }}

            h1 {{
                color: green;
            }}

            .application-number {{
                font-size: 25px;
                font-weight: bold;
                color: #0066cc;
                margin: 20px 0;
            }}

            a {{
                display: inline-block;
                margin-top: 20px;
                padding: 12px 25px;
                background: #0066cc;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }}

            a:hover {{
                background: #004c99;
            }}

        </style>

    </head>


    <body>

        <div class="box">

            <h1>
                Application Submitted Successfully!
            </h1>

            <p>
                Thank you for applying.
            </p>

            <p>
                Your Application Number is:
            </p>

            <div class="application-number">
                {application_number}
            </div>

            <p>
                Please save this application number
                for future status checking.
            </p>

            <a href="/">
                Back to Home
            </a>

        </div>

    </body>

    </html>
    """


# ==========================================
# APPLICATION STATUS PAGE
# ==========================================

@app.route("/status")
def status():

    return render_template("status.html")


# ==========================================
# CHECK APPLICATION STATUS
# ==========================================

@app.route("/check-status", methods=["POST"])
def check_status():

    application_number = request.form["application_number"]


    connection = get_db_connection()


    application = connection.execute(
        """
        SELECT *
        FROM applications
        WHERE application_number = ?
        """,
        (application_number,)
    ).fetchone()


    connection.close()


    if application:

        return render_template(
            "status.html",
            application=application
        )

    else:

        return render_template(
            "status.html",
            error="Application number not found."
        )


# ==========================================
# ADMIN LOGIN PAGE
# ==========================================

@app.route("/admin")
def admin_login():

    return render_template("admin_login.html")


# ==========================================
# SECURE ADMIN LOGIN
# ==========================================

@app.route("/admin/login", methods=["POST"])
def admin_login_process():

    username = request.form["username"].strip()

    password = request.form["password"]


    # Connect to database
    connection = get_db_connection()


    # Find admin username
    admin = connection.execute(
        """
        SELECT *
        FROM admin_users
        WHERE username = ?
        """,
        (username,)
    ).fetchone()


    connection.close()


    # Check username and hashed password
    if admin and check_password_hash(
        admin["password"],
        password
    ):

        session.clear()

        session["admin_logged_in"] = True

        session["admin_username"] = admin["username"]

        return redirect("/admin/dashboard")


    else:

        return render_template(
            "admin_login.html",
            error="Invalid username or password."
        )


# ==========================================
# ADMIN DASHBOARD
# ==========================================

@app.route("/admin/dashboard")
def admin_dashboard():

    # Check admin login
    if not session.get("admin_logged_in"):

        return redirect("/admin")


    # Search value
    search = request.args.get(
        "search",
        ""
    ).strip()


    # Course filter
    course = request.args.get(
        "course",
        ""
    ).strip()


    # Status filter
    status = request.args.get(
        "status",
        ""
    ).strip()


    connection = get_db_connection()


    # Base query
    query = """
        SELECT *
        FROM applications
        WHERE 1=1
    """


    parameters = []


    # --------------------------------------
    # SEARCH
    # --------------------------------------

    if search:

        query += """
            AND (
                application_number LIKE ?
                OR student_name LIKE ?
            )
        """

        parameters.append(
            "%" + search + "%"
        )

        parameters.append(
            "%" + search + "%"
        )


    # --------------------------------------
    # COURSE FILTER
    # --------------------------------------

    if course:

        query += """
            AND course = ?
        """

        parameters.append(course)


    # --------------------------------------
    # STATUS FILTER
    # --------------------------------------

    if status:

        query += """
            AND status = ?
        """

        parameters.append(status)


    # Latest applications first
    query += """
        ORDER BY id DESC
    """


    applications = connection.execute(
        query,
        parameters
    ).fetchall()


    # --------------------------------------
    # GET COURSES
    # --------------------------------------

    courses = connection.execute(
        """
        SELECT DISTINCT course
        FROM applications
        ORDER BY course
        """
    ).fetchall()


    connection.close()


    return render_template(
        "admin_dashboard.html",

        applications=applications,

        courses=courses,

        search=search,

        selected_course=course,

        selected_status=status
    )


# ==========================================
# UPDATE APPLICATION STATUS
# ==========================================

@app.route(
    "/admin/update-status",
    methods=["POST"]
)
def update_status():

    # Check admin login
    if not session.get("admin_logged_in"):

        return redirect("/admin")


    application_number = request.form[
        "application_number"
    ]


    new_status = request.form[
        "status"
    ]


    # Allowed status values
    allowed_statuses = [
        "Submitted",
        "Approved",
        "Rejected"
    ]


    # Security check
    if new_status not in allowed_statuses:

        return redirect(
            "/admin/dashboard"
        )


    connection = get_db_connection()


    connection.execute(
        """
        UPDATE applications
        SET status = ?
        WHERE application_number = ?
        """,
        (
            new_status,
            application_number
        )
    )


    connection.commit()

    connection.close()


    return redirect(
        "/admin/dashboard"
    )


# ==========================================
# VIEW APPLICATION DETAILS
# ==========================================

@app.route(
    "/admin/application/<application_number>"
)
def application_details(
    application_number
):

    # Check admin login
    if not session.get("admin_logged_in"):

        return redirect("/admin")


    connection = get_db_connection()


    application = connection.execute(
        """
        SELECT *
        FROM applications
        WHERE application_number = ?
        """,
        (application_number,)
    ).fetchone()


    connection.close()


    if application is None:

        return "Application not found.", 404


    return render_template(
        "application_details.html",
        application=application
    )


# ==========================================
# DOWNLOAD APPLICATION AS PDF
# ==========================================

@app.route(
    "/admin/application/<application_number>/download"
)
def download_application(
    application_number
):

    # Check admin login
    if not session.get("admin_logged_in"):

        return redirect("/admin")


    # Get application
    connection = get_db_connection()


    application = connection.execute(
        """
        SELECT *
        FROM applications
        WHERE application_number = ?
        """,
        (application_number,)
    ).fetchone()


    connection.close()


    # Application not found
    if application is None:

        return "Application not found.", 404


    # --------------------------------------
    # CREATE PDF IN MEMORY
    # --------------------------------------

    pdf_buffer = io.BytesIO()


    document = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )


    styles = getSampleStyleSheet()


    title_style = styles["Title"]

    heading_style = styles["Heading2"]

    normal_style = styles["Normal"]


    elements = []


    # --------------------------------------
    # TITLE
    # --------------------------------------

    elements.append(
        Paragraph(
            "COLLEGE ADMISSION APPLICATION",
            title_style
        )
    )


    elements.append(
        Spacer(1, 20)
    )


    # --------------------------------------
    # APPLICATION NUMBER
    # --------------------------------------

    elements.append(
        Paragraph(
            "<b>Application Number:</b> "
            + escape(
                str(
                    application[
                        "application_number"
                    ]
                )
            ),
            normal_style
        )
    )


    elements.append(
        Paragraph(
            "<b>Application Status:</b> "
            + escape(
                str(
                    application[
                        "status"
                    ]
                )
            ),
            normal_style
        )
    )


    elements.append(
        Spacer(1, 20)
    )


    # --------------------------------------
    # STUDENT INFORMATION
    # --------------------------------------

    elements.append(
        Paragraph(
            "Student Information",
            heading_style
        )
    )


    student_data = [

        [
            "Student Name",
            application["student_name"]
        ],

        [
            "Date of Birth",
            application["dob"]
        ],

        [
            "Gender",
            application["gender"]
        ],

        [
            "Mobile",
            application["mobile"]
        ],

        [
            "Email",
            application["email"]
        ],

        [
            "Address",
            application["address"]
        ],

        [
            "District",
            application["district"]
        ],

        [
            "State",
            application["state"]
        ],

        [
            "Pincode",
            application["pincode"]
        ]

    ]


    # Escape values for ReportLab
    student_data = [

        [
            escape(str(row[0])),
            escape(str(row[1]))
        ]

        for row in student_data

    ]


    student_table = Table(
        student_data,
        colWidths=[150, 350]
    )


    student_table.setStyle(
        TableStyle([

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.lightgrey
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),

            (
                "PADDING",
                (0, 0),
                (-1, -1),
                7
            )

        ])
    )


    elements.append(
        student_table
    )


    elements.append(
        Spacer(1, 20)
    )


    # --------------------------------------
    # EDUCATIONAL INFORMATION
    # --------------------------------------

    elements.append(
        Paragraph(
            "Educational Information",
            heading_style
        )
    )


    education_data = [

        [
            "School",
            application["school"]
        ],

        [
            "10th Mark",
            application["tenth"]
        ],

        [
            "12th Mark",
            application["twelfth"]
        ],

        [
            "Group",
            application["group_name"]
        ],

        [
            "Course",
            application["course"]
        ]

    ]


    education_data = [

        [
            escape(str(row[0])),
            escape(str(row[1]))
        ]

        for row in education_data

    ]


    education_table = Table(
        education_data,
        colWidths=[150, 350]
    )


    education_table.setStyle(
        TableStyle([

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.lightgrey
            ),

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "TOP"
            ),

            (
                "PADDING",
                (0, 0),
                (-1, -1),
                7
            )

        ])
    )


    elements.append(
        education_table
    )


    elements.append(
        Spacer(1, 20)
    )


    # --------------------------------------
    # PARENT INFORMATION
    # --------------------------------------

    elements.append(
        Paragraph(
            "Parent / Guardian Information",
            heading_style
        )
    )


    parent_data = [

        [
            "Parent Name",
            application["parent_name"]
        ],

        [
            "Parent Mobile",
            application["parent_mobile"]
        ]

    ]


    parent_data = [

        [
            escape(str(row[0])),
            escape(str(row[1]))
        ]

        for row in parent_data

    ]


    parent_table = Table(
        parent_data,
        colWidths=[150, 350]
    )


    parent_table.setStyle(
        TableStyle([

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.grey
            ),

            (
                "BACKGROUND",
                (0, 0),
                (0, -1),
                colors.lightgrey
            ),

            (
                "PADDING",
                (0, 0),
                (-1, -1),
                7
            )

        ])
    )


    elements.append(
        parent_table
    )


    elements.append(
        Spacer(1, 30)
    )


    elements.append(
        Paragraph(
            "Generated from the College Admission Management System.",
            normal_style
        )
    )


    # --------------------------------------
    # BUILD PDF
    # --------------------------------------

    document.build(elements)


    pdf_buffer.seek(0)


    # --------------------------------------
    # DOWNLOAD PDF
    # --------------------------------------

    return send_file(

        pdf_buffer,

        as_attachment=True,

        download_name=(
            application_number
            + "_Application.pdf"
        ),

        mimetype="application/pdf"

    )


# ==========================================
# ADMIN LOGOUT
# ==========================================

@app.route("/admin/logout")
def admin_logout():

    session.clear()

    return redirect("/admin")


# ==========================================
# START FLASK APPLICATION
# ==========================================

if __name__ == "__main__":

    # Create database and tables
    create_database()


    # Start Flask
    app.run(

        host="127.0.0.1",

        port=5050,

        debug=False,

        threaded=False

    )
