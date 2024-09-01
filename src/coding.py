from flask import *

from src.dbconnectionnew import *

from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "8394584658"

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
    elif res['type'] == "admin":
        session['lid'] = res['id']
        return  redirect("admin_home")
    elif res['type'] == "question_setter":
        session['lid'] = res['id']
        return redirect("/question_setter_home")
    elif res['type'] == "moderator":
        session['lid'] = res['id']
        return redirect("/moderator_home")

@app.route("/admin_home")
def admin_home():
    return render_template("admin/admin_index.html")

@app.route("/Verify_Moderators")
def Verify_Moderators():
    qry = 'SELECT * FROM `moderators` JOIN `login` ON `moderators`.lid = `login`.id WHERE `type`="pending"'
    res = selectall(qry)
    return render_template("admin/Verify_Moderators.html", val=res)


@app.route("/accept_moderators")
def accept_moderators():
    id = request.args.get('id')
    qry = 'UPDATE `login` SET `type`="moderator" WHERE `id`=%s'
    iud(qry, id)
    return '''<script>alert("successfully accepted");window.location="/Verify_Moderators"</script>'''

@app.route("/reject_moderators")
def reject_moderators():
    id = request.args.get('id')
    qry = 'UPDATE `login` SET `type`="rejected" WHERE `id`=%s'
    iud(qry, id)
    return '''<script>alert("rejected");window.location="/Verify_Moderators"</script>'''

@app.route("/manage_users")
def manage_users():
    return render_template("admin/manage_users.html")


@app.route("/view_users_details", methods=['post'])
def view_users_details():
    type = request.form['select']

    if type == "Moderator":
        qry = "SELECT * FROM `moderators` JOIN `login` ON `moderators`.`lid`=`login`.`id`"
        res = selectall(qry)
        return render_template("admin/manage_users.html", val=res)
    elif type == "Question Setters":
        qry = "SELECT * FROM `question_setters` JOIN `login` ON `question_setters`.`lid`=`login`.`id`"
        res = selectall(qry)
        return render_template("admin/manage_users.html", val=res)
    else:
        qry = "SELECT * FROM `test_takers` JOIN `login` ON `test_takers`.`lid`=`login`.`id`"
        res = selectall(qry)
        return render_template("admin/manage_users.html", val=res)


@app.route("/unblock_users")
def unblock_users():
    id = request.args.get('id')
    type  = request.args.get('type')
    if type == "Moderator":
        qry = 'UPDATE `login` SET `type`="unblocked" WHERE `id`=%s'
        iud(qry, id)
        return '''<script>alert("successfully unblocked");window.location="/manage_users"</script>'''
    elif type == "Question Setters":
        qry = 'UPDATE `login` SET `type`="unblocked" WHERE `id`=%s'
        iud(qry, id)
        return '''<script>alert("successfully unblocked");window.location="/manage_users"</script>'''
    else:
        qry = 'UPDATE `login` SET `type`="unblocked" WHERE `id`=%s'
        iud(qry, id)
        return '''<script>alert("successfully unblocked");window.location="/manage_users"</script>'''

@app.route("/block_user")
def block_user():
    id = request.args.get('id')
    qry = 'UPDATE `login` SET `type`="blocked" WHERE `id`=%s'
    iud(qry, id)
    return '''<script>alert("successfully blocked");window.location="/manage_users"</script>'''


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

        qry = "insert into login values(null, %s, %s, 'pending')"
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