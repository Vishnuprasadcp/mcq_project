from flask import *

from src.dbconnectionnew import *

from werkzeug.utils import secure_filename
import os

app = Flask(__name__)


@app.route("/")
def login():
    return render_template("auth/login.html")


@app.route("/login_code", methods=['post'])
def login_code():
    username = request.form['email']
    password = request.form['password']

    qry = 'select * from login where username=%s and password=%s'
    res = selectone(qry,(username, password))

    if res is None:
        return '''<script>alert("Invalid username or password");window.location="/"</script>'''
    elif res['type'] == "test_taker":
        return  redirect("/TestTaker/test_taker_home")
    elif res['type'] == "question_setter":
        return redirect("/question_setter_home")
    elif res['type'] == "moderator":
        return redirect("/moderator_home")

@app.route("/admin_home")
def admin_home():
    return render_template("admin/admin_home.html")

@app.route("/Verify_Moderators")
def Verify_Moderators():

    return render_template("admin/Verify_Moderators.html")


@app.route("/accept_moderators")
def accept_moderators():
    return

@app.route("/reject_moderators")
def reject_moderators():
    return

@app.route("/mod_manage")
def mod_manage():
    return render_template("admin/mod manage.html")


@app.route("/view_mod_blocked")
def view_mod_blocked():
    return render_template("admin/mod manage.html")


@app.route("/register")
def register():
    return render_template("auth/register.html")


@app.route("/register_code", methods=['post'])
def register_code():
    name = request.form['name']
    age = request.form['age']
    email = request.form['email']
    mobile = request.form['mobile']
    password = request.form['password']
    role = request.form['role']

    if role == "Moderator":
        print("====",request.form)
        subject = request.form['subject']
        qualification = request.form['qualification']
        university = request.form['university']
        certificate = request.files['qualification_certificate']

        cert_name = secure_filename(certificate.filename)
        certificate.save(os.path.join('static/uploads', cert_name))

        qry = "insert into login values(null, %s, %s, 'moderator')"
        id = iud(qry, (email, password))

        qry = "insert into moderators VALUES(null,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        iud(qry, (id, name, age, email, mobile, subject, qualification, university, cert_name))

        return '''<script>alert("Success");window.location="/"</script>'''

    elif role == "Question Setter":
        print("====",request.form)
        subject = request.form['subject_qs']
        qualification = request.form['qualification_qs']

        qry = "insert into login values(null, %s, %s, 'question_setter')"
        id = iud(qry, (email, password))

        if qualification == "No Certificate":
            qry = "INSERT INTO question_setters VALUES(null, %s, %s,%s,%s,%s,%s,%s,null,null)"
            iud(qry, (id, name, age, email, mobile, subject, qualification))
            return '''<script>alert("Success");window.location="/"</script>'''

        else:
            university = request.form['university_qs']
            certificate = request.files['qualification_certificate_qs']

            cert_name = secure_filename(certificate.filename)
            certificate.save(os.path.join('static/uploads', cert_name))

            qry = "INSERT INTO question_setters VALUES(null, %s, %s,%s,%s,%s,%s,%s,%s,%s)"
            iud(qry, (id, name, age, email, mobile, subject, qualification, university, cert_name))
            return '''<script>alert("Success");window.location="/"</script>'''


    else:
        qry = "insert into login values(null, %s, %s, 'test_taker')"
        id = iud(qry, (email, password))

        qry = "INSERT INTO users VALUES(null,%s, %s, %s, %s, %s)"
        iud(qry, (id, name, age, email, mobile))
        return '''<script>alert("Success");window.location="/"</script>'''


# @app.route("/test_taker_register_code", methods=['post'])
# def test_taker_register_code():
#
#     name = request.form['name']
#     age = request.form['age']
#     email = request.form['email']
#     mobile = request.form['mobile']
#     password = request.form['password']
#
#     qry = "INSERT INTO `login` VALUES(null,%s,%s,'testtaker')"
#     id = iud(qry, (email, password))
#
#     qry = 'INSERT INTO `users` VALUES(null,%s,%s,%s,%s,%s)'
#     iud(qry,(id,name,age,email,mobile))
#
#     return '''<script>alert("Success");window.location="/"</script>'''





@app.route("/TestTaker/test_taker_home")
def test_taker_home():
    return render_template("TestTaker/test_taker_home.html")


@app.route("/moderator_home")
def moderator_home():
    return render_template("moderators/mod_home.html")


@app.route("/question_setter_home")
def question_setter_home():
    return render_template("Question_setter/qs_home.html")


@app.route("/question_insert", methods=['post'])
def question_insert():
    question = request.form['question']
    option1 = request.form['option1']
    option2 = request.form['option2']
    option3 = request.form['option3']
    option4 = request.form['option4']

    qry = "INSERT INTO `questions` VALUES(NULL,%s,%s,%s,%s,%s)"
    iud(qry, (question,option1,option2,option3,option4))

    return '''<script>alert("Added");window.location="question_setter_home"</script>'''


app.run(debug = True)