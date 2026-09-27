from flask import Flask, render_template, request, redirect, session, send_file

import sqlite3
import random
import io
import os
import secrets

import psycopg2
from psycopg2.extras import RealDictCursor

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
app.secret_key = os.environ.get(
    "COLLEGE_SECRET_KEY",
    secrets.token_hex(32)
)


# ==========================================
# DATABASE SETTINGS
# ==========================================

# Local SQLite database
DATABASE = "database.db"

# Render PostgreSQL database
DATABASE_URL = os.environ.get("DATABASE_URL")


# ==========================================
# DATABASE CONNECTION CLASS
# ==========================================

class DatabaseConnection:

    def __init__(self):

        # If DATABASE_URL exists, use PostgreSQL.
        # Otherwise, use SQLite.

        self.is_postgres = bool(DATABASE_URL)

        if self.is_postgres:

            db_url = DATABASE_URL

            # Some PostgreSQL URLs may start with postgres://
            # psycopg2 expects postgresql://

            if db_url.startswith("postgres://"):

                db_url = (
                    "postgresql://"
                    + db_url[len("postgres://"):]
                )

            self.connection = psycopg2.connect(
                db_url
            )

        else:

            self.connection = sqlite3.connect(
                DATABASE
            )

            self.connection.row_factory = sqlite3.Row


    # --------------------------------------
    # EXECUTE SQL QUERY
    # --------------------------------------

    def execute(
        self,
        query,
        parameters=()
    ):

        if self.is_postgres:

            # SQLite uses ?
            # PostgreSQL uses %s

            query = query.replace(
                "?",
                "%s"
            )

            cursor = self.connection.cursor(
                cursor_factory=RealDictCursor
            )

            cursor.execute(
                query,
                parameters
            )

            return cursor

        else:

            return self.connection.execute(
                query,
                parameters
            )


    # --------------------------------------
    # COMMIT
    # --------------------------------------

    def commit(self):

        self.connection.commit()


    # --------------------------------------
    # CLOSE
    # --------------------------------------

    def close(self):

        self.connection.close()


# ==========================================
# GET DATABASE CONNECTION
# ==========================================

def get_db_connection():

    return DatabaseConnection()


# ==========================================
# CREATE DATABASE
# ==========================================

def create_database():

    connection = get_db_connection()


    # ======================================
    # POSTGRESQL DATABASE
    # ======================================

    if connection.is_postgres:

        # ----------------------------------
        # APPLICATIONS TABLE
        # ----------------------------------

        connection.execute("""
            CREATE TABLE IF NOT EXISTS applications (

                id SERIAL PRIMARY KEY,

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

                tenth DOUBLE PRECISION NOT NULL,

                twelfth DOUBLE PRECISION NOT NULL,

                group_name TEXT NOT NULL,

                course TEXT NOT NULL,

                parent_name TEXT NOT NULL,

                parent_mobile TEXT NOT NULL,

                status TEXT DEFAULT 'Submitted'

            )
        """)


        # ----------------------------------
        # ADMIN USERS TABLE
        # ----------------------------------

        connection.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (

                id SERIAL PRIMARY KEY,

                username TEXT UNIQUE NOT NULL,

                password TEXT NOT NULL

            )
        """)


    # ======================================
    # SQLITE DATABASE
    # ======================================

    else:

        # ----------------------------------
        # APPLICATIONS TABLE
        # ----------------------------------

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


        # ----------------------------------
        # ADMIN USERS TABLE
        # ----------------------------------

        connection.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                username TEXT UNIQUE NOT NULL,

                password TEXT NOT NULL

            )
        """)


    # ======================================
    # CREATE DEFAULT ADMIN
    # ======================================

    admin = connection.execute(
        """
        SELECT *
        FROM admin_users
        WHERE username = ?
        """,
        ("admin",)
    ).fetchone()


    # Create admin only if it does not exist

    if admin is None:

        hashed_password = generate_password_hash(
            "admin123"
        )

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

    while True:

        number = random.randint(
            10000,
            99999
        )

        application_number = (
            "APP2026"
            + str(number)
        )

        connection = get_db_connection()

        existing = connection.execute(
            """
            SELECT id
            FROM applications
            WHERE application_number = ?
            """,
            (application_number,)
        ).fetchone()

        connection.close()

        if existing is None:

            return application_number


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ==========================================
# SUBMIT ADMISSION APPLICATION
# ==========================================

@app.route(
    "/submit",
    methods=["POST"]
)
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

    application_number = (
        generate_application_number()
    )


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

        VALUES (
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
        )

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

        float(tenth),

        float(twelfth),

        group_name,

        course,

        parent_name,

        parent_mobile

    ))


    connection.commit()

    connection.close()


    # ======================================
    # SUCCESS PAGE
    # ======================================

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

    return render_template(
        "status.html"
    )


# ==========================================
# CHECK APPLICATION STATUS
# ==========================================

@app.route(
    "/check-status",
    methods=["POST"]
)
def check_status():

    application_number = request.form[
        "application_number"
    ]


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

    return render_template(
        "admin_login.html"
    )


# ==========================================
# SECURE ADMIN LOGIN
# ==========================================

@app.route(
    "/admin/login",
    methods=["POST"]
)
def admin_login_process():

    username = request.form[
        "username"
    ].strip()

    password = request.form[
        "password"
    ]


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


    # Check username and password

    if admin and check_password_hash(
        admin["password"],
        password
    ):

        session.clear()

        session["admin_logged_in"] = True

        session["admin_username"] = (
            admin["username"]
        )

        return redirect(
            "/admin/dashboard"
        )


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

    if not session.get(
        "admin_logged_in"
    ):

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


    # ======================================
    # SEARCH
    # ======================================

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


    # ======================================
    # COURSE FILTER
    # ======================================

    if course:

        query += """
            AND course = ?
        """

        parameters.append(
            course
        )


    # ======================================
    # STATUS FILTER
    # ======================================

    if status:

        query += """
            AND status = ?
        """

        parameters.append(
            status
        )


    # Latest applications first

    query += """
        ORDER BY id DESC
    """


    applications = connection.execute(
        query,
        parameters
    ).fetchall()


    # ======================================
    # GET COURSES
    # ======================================

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

    if not session.get(
        "admin_logged_in"
    ):

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

    if not session.get(
        "admin_logged_in"
    ):

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

        return (
            "Application not found.",
            404
        )


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

    if not session.get(
        "admin_logged_in"
    ):

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

        return (
            "Application not found.",
            404
        )


    # ======================================
    # CREATE PDF IN MEMORY
    # ======================================

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


    # ======================================
    # TITLE
    # ======================================

    elements.append(
        Paragraph(
            "COLLEGE ADMISSION APPLICATION",
            title_style
        )
    )


    elements.append(
        Spacer(1, 20)
    )


    # ======================================
    # APPLICATION NUMBER
    # ======================================

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


    # ======================================
    # STUDENT INFORMATION
    # ======================================

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


    # ======================================
    # EDUCATIONAL INFORMATION
    # ======================================

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


    # ======================================
    # PARENT INFORMATION
    # ======================================

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


    # ======================================
    # BUILD PDF
    # ======================================

    document.build(
        elements
    )


    pdf_buffer.seek(0)


    # ======================================
    # DOWNLOAD PDF
    # ======================================

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
# CREATE DATABASE ON STARTUP
# ==========================================

# IMPORTANT:
# This must run outside the __main__ block
# because Render uses Gunicorn.
#
# Gunicorn imports app.py instead of running
# "python app.py".
#
# Therefore this creates the PostgreSQL
# tables automatically on Render.

create_database()

@app.route("/course/<course_name>")
def course_details(course_name):

    courses = {

    "data-science": {
        "name": "B.Sc Data Science",
        "duration": "3 Years",
        "overview": "B.Sc Data Science provides students with a foundation in programming, statistics, data analysis, databases, data visualization and emerging data-driven technologies. The programme develops analytical thinking and practical skills for working with data.",
        "eligibility": "Candidates who have passed Higher Secondary / 10+2 or an equivalent examination with the required subjects and marks prescribed by the University and College are eligible to apply.",
        "subjects": [
            "Programming with Python",
            "Statistics",
            "Database Management Systems",
            "Data Structures",
            "Data Visualization",
            "Machine Learning",
            "Artificial Intelligence",
            "Big Data Fundamentals",
            "Web Technologies",
            "Data Analytics"
        ],
        "benefits": [
            "Develop strong programming and analytical skills.",
            "Learn to collect, process and interpret data.",
            "Gain practical knowledge of Python and databases.",
            "Develop data visualization skills.",
            "Understand the fundamentals of machine learning and artificial intelligence.",
            "Work on practical data-oriented projects."
        ],
        "careers": [
            "Data Analyst",
            "Junior Data Scientist",
            "Business Analyst",
            "Data Visualization Analyst",
            "Database Analyst",
            "Data Associate"
        ]
    },

    "computer-science": {
        "name": "B.Sc Computer Science",
        "duration": "3 Years",
        "overview": "B.Sc Computer Science provides students with fundamental and advanced knowledge of programming, algorithms, databases, computer networks, software development and modern computing technologies.",
        "eligibility": "Candidates who have passed Higher Secondary / 10+2 or an equivalent examination with the required qualification and subjects prescribed by the University and College are eligible to apply.",
        "subjects": [
            "Programming in C",
            "Object-Oriented Programming",
            "Data Structures",
            "Database Management Systems",
            "Computer Networks",
            "Operating Systems",
            "Computer Architecture",
            "Web Technologies",
            "Software Engineering",
            "Python Programming"
        ],
        "benefits": [
            "Develop strong programming and problem-solving abilities.",
            "Understand algorithms and data structures.",
            "Gain practical knowledge of databases and networks.",
            "Learn software and web development concepts.",
            "Develop skills in modern programming languages.",
            "Build practical projects and applications."
        ],
        "careers": [
            "Software Developer",
            "Web Developer",
            "System Analyst",
            "Database Administrator",
            "Application Developer",
            "Technical Support Executive"
        ]
    },

    "bca": {
        "name": "BCA",
        "duration": "3 Years",
        "overview": "Bachelor of Computer Applications focuses on computer applications, programming, software development, databases, web technologies and information technology. The programme combines theoretical knowledge with practical application development.",
        "eligibility": "Candidates who have passed Higher Secondary / 10+2 or an equivalent examination with the qualification prescribed by the University and College are eligible to apply.",
        "subjects": [
            "Programming Fundamentals",
            "C Programming",
            "Python Programming",
            "Data Structures",
            "Database Management Systems",
            "Web Development",
            "Computer Networks",
            "Operating Systems",
            "Software Engineering",
            "Mobile Application Concepts"
        ],
        "benefits": [
            "Develop practical programming skills.",
            "Learn application and web development.",
            "Understand database management.",
            "Gain knowledge of software development processes.",
            "Develop computer application skills.",
            "Work on practical software projects."
        ],
        "careers": [
            "Software Developer",
            "Web Developer",
            "Application Developer",
            "Database Administrator",
            "IT Support Executive",
            "System Administrator"
        ]
    },

    "zoology": {
        "name": "Zoology",
        "duration": "3 Years",
        "overview": "The Zoology programme provides knowledge about animals, their structure, physiology, behaviour, evolution, ecology and biodiversity. Students develop scientific observation and laboratory skills through practical learning.",
        "eligibility": "Candidates who have completed Higher Secondary / 10+2 with the required science subjects and qualification prescribed by the University and College are eligible to apply.",
        "subjects": [
            "Animal Diversity",
            "Cell Biology",
            "Animal Physiology",
            "Genetics",
            "Developmental Biology",
            "Evolution",
            "Ecology",
            "Environmental Biology",
            "Biochemistry",
            "Molecular Biology"
        ],
        "benefits": [
            "Develop knowledge of animal biology and biodiversity.",
            "Understand animal structure and physiology.",
            "Develop laboratory and observation skills.",
            "Learn ecological and environmental concepts.",
            "Gain practical experience in biological studies.",
            "Build a foundation for higher studies and research."
        ],
        "careers": [
            "Research Assistant",
            "Laboratory Assistant",
            "Wildlife Conservation Assistant",
            "Environmental Assistant",
            "Biology Educator",
            "Laboratory Technician"
        ]
    },

    "bcom": {
        "name": "B.Com",
        "duration": "3 Years",
        "overview": "B.Com provides students with knowledge of accounting, commerce, finance, business management, taxation and business practices. The programme develops financial understanding and professional business skills.",
        "eligibility": "Candidates who have passed Higher Secondary / 10+2 or an equivalent examination with the required qualification prescribed by the University and College are eligible to apply.",
        "subjects": [
            "Financial Accounting",
            "Business Economics",
            "Business Management",
            "Corporate Accounting",
            "Cost Accounting",
            "Income Tax",
            "Business Law",
            "Marketing Management",
            "Banking and Financial Services",
            "Entrepreneurship"
        ],
        "benefits": [
            "Develop accounting and financial skills.",
            "Understand business and commercial activities.",
            "Gain knowledge of taxation and business law.",
            "Develop financial management skills.",
            "Improve business communication.",
            "Build a foundation for professional commerce careers."
        ],
        "careers": [
            "Accountant",
            "Accounts Executive",
            "Finance Assistant",
            "Banking Executive",
            "Business Executive",
            "Tax Assistant"
        ]
    },

    "bcom-ca": {
        "name": "B.Com CA",
        "duration": "3 Years",
        "overview": "B.Com Computer Applications combines commerce education with computer applications. The programme provides knowledge of accounting, finance, business operations and computer-based applications used in modern organisations.",
        "eligibility": "Candidates who have passed Higher Secondary / 10+2 or an equivalent examination with the qualification prescribed by the University and College are eligible to apply.",
        "subjects": [
            "Financial Accounting",
            "Corporate Accounting",
            "Business Economics",
            "Computer Fundamentals",
            "Programming Fundamentals",
            "Database Management",
            "Computer Applications in Business",
            "Business Law",
            "Income Tax",
            "Financial Management"
        ],
        "benefits": [
            "Combine commerce knowledge with computer skills.",
            "Develop accounting and financial abilities.",
            "Learn business-oriented computer applications.",
            "Gain database and software skills.",
            "Understand modern accounting environments.",
            "Develop analytical and numerical abilities."
        ],
        "careers": [
            "Accountant",
            "Accounts Executive",
            "Finance Assistant",
            "Computer Operator",
            "Business Executive",
            "Office Administrator"
        ]
    },

    "mathematics": {
        "name": "B.Sc Mathematics",
        "duration": "3 Years",
        "overview": "B.Sc Mathematics develops logical reasoning, analytical thinking and mathematical problem-solving abilities. The programme provides a strong foundation in pure and applied mathematical concepts.",
        "eligibility": "Candidates who have completed Higher Secondary / 10+2 with Mathematics and the qualification prescribed by the University and College are eligible to apply.",
        "subjects": [
            "Algebra",
            "Calculus",
            "Differential Equations",
            "Integral Calculus",
            "Analytical Geometry",
            "Statistics",
            "Number Theory",
            "Discrete Mathematics",
            "Operations Research",
            "Mathematical Methods"
        ],
        "benefits": [
            "Develop logical and analytical thinking.",
            "Strengthen mathematical problem-solving skills.",
            "Develop quantitative reasoning abilities.",
            "Understand mathematical modelling.",
            "Build a foundation for higher studies.",
            "Apply mathematical concepts to practical problems."
        ],
        "careers": [
            "Mathematics Educator",
            "Data Analyst",
            "Statistical Assistant",
            "Research Assistant",
            "Banking Executive",
            "Operations Research Assistant"
        ]
    },

    "english": {
        "name": "B.A English",
        "duration": "3 Years",
        "overview": "B.A English develops language proficiency, communication, literature, writing, critical thinking and creative expression. The programme helps students develop effective written and verbal communication skills.",
        "eligibility": "Candidates who have passed Higher Secondary / 10+2 or an equivalent examination with the qualification prescribed by the University and College are eligible to apply.",
        "subjects": [
            "English Literature",
            "British Literature",
            "Indian Writing in English",
            "American Literature",
            "Literary Criticism",
            "English Grammar",
            "Communication Skills",
            "Creative Writing",
            "Language and Linguistics",
            "Professional Communication"
        ],
        "benefits": [
            "Improve English language proficiency.",
            "Develop professional writing skills.",
            "Strengthen public speaking and presentation abilities.",
            "Develop critical and creative thinking.",
            "Gain knowledge of literature and literary studies.",
            "Improve communication skills for professional environments."
        ],
        "careers": [
            "Content Writer",
            "English Teacher",
            "Editor",
            "Copywriter",
            "Proofreader",
            "Communication Executive"
        ]
    },

    "chemistry": {
        "name": "B.Sc Chemistry",
        "duration": "3 Years",
        "overview": "B.Sc Chemistry provides students with knowledge of chemical principles, laboratory techniques, chemical reactions, materials and analytical methods. The programme combines theoretical learning with practical laboratory experience.",
        "eligibility": "Candidates who have completed Higher Secondary / 10+2 with the required science subjects and qualification prescribed by the University and College are eligible to apply.",
        "subjects": [
            "Inorganic Chemistry",
            "Organic Chemistry",
            "Physical Chemistry",
            "Analytical Chemistry",
            "Biochemistry",
            "Environmental Chemistry",
            "Polymer Chemistry",
            "Spectroscopy",
            "Chemical Kinetics",
            "Laboratory Techniques"
        ],
        "benefits": [
            "Develop practical laboratory skills.",
            "Understand chemical reactions and principles.",
            "Learn analytical and organic chemistry.",
            "Develop scientific observation skills.",
            "Gain experience with laboratory techniques.",
            "Build a foundation for higher studies and research."
        ],
        "careers": [
            "Laboratory Assistant",
            "Quality Control Assistant",
            "Research Assistant",
            "Chemical Laboratory Technician",
            "Production Assistant",
            "Quality Assurance Assistant"
        ]
    }
}

    course = courses.get(course_name)

    if not course:
        return "Course not found", 404

    return render_template("course_details.html", course=course)
# ==========================================
# START FLASK APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(

        host="127.0.0.1",

        port=5050,

        debug=False,

        threaded=False

    )
