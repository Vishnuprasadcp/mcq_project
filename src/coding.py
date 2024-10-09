
from flask import *

from src.dbconnectionnew import *
from  src.mcq_gen import *

from werkzeug.utils import secure_filename
import os
import random
app = Flask(__name__)
app.secret_key = "8394584658"


question_list = []


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
        session['lid'] = res['id']
        return  redirect("/test_taker_home")
    elif res['type'] == "admin":
        session['lid'] = res['id']
        return  redirect("admin_home")
    elif res['type'] == "question_setter":
        session['lid'] = res['id']
        return redirect("/question_setter_home")
    elif res['type'] == "moderator":
        session['lid'] = res['id']

        qry = "SELECT `moderators`.`subject` FROM `moderators` WHERE `lid`=%s"
        res1 = selectone(qry, session['lid'])
        session['subject'] = res1['subject']

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
        qry = 'UPDATE `login` SET `type`="moderator" WHERE `id`=%s'
        iud(qry, id)
        return '''<script>alert("successfully unblocked");window.location="/manage_users"</script>'''
    elif type == "Question Setters":
        qry = 'UPDATE `login` SET `type`="question_setter" WHERE `id`=%s'
        iud(qry, id)
        return '''<script>alert("successfully unblocked");window.location="/manage_users"</script>'''
    else:
        qry = 'UPDATE `login` SET `type`="test_taker" WHERE `id`=%s'
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

        qry = "insert into login values(null, %s, %s, 'pending')"
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

        qry = "INSERT INTO test_takers VALUES(null,%s, %s, %s, %s, %s)"
        iud(qry, (id, name, age, email, mobile))
        return '''<script>alert("Success");window.location="/"</script>'''


@app.route("/test_taker_home")
def test_taker_home():
    return render_template("TestTaker/TT_index.html")


@app.route("/moderator_home")
def moderator_home():
    return render_template("moderators/moderator_index.html")


@app.route("/verify_question")
def verify_question():
    qry = "SELECT `question_setters`.`name`,`email`,`questions`.* FROM `questions` JOIN `question_setters` ON `questions`.`qs_id`=`question_setters`.`lid` WHERE `questions`.`status`='pending' AND `question_setters`.`subject`=%s"
    res = selectall2(qry, session['subject'])
    return render_template("moderators/verify_question.html", val=res)


@app.route("/accept_question")
def accept_qustion():
    id = request.args.get('id')
    qry = 'UPDATE `questions` SET `status`="accepted" WHERE `qid`=%s'
    iud(qry, id)
    return '''<script>alert("accepted");window.location="/verify_question"</script>'''


@app.route("/reject_question")
def reject_qustion():
    id = request.args.get('id')
    qry = 'UPDATE `questions` SET `status`="rejected" WHERE `qid`=%s'
    iud(qry, id)
    return '''<script>alert("rejected");window.location="/verify_question"</script>'''


@app.route("/verify_qs")
def verify_qs():
    qry = 'SELECT * FROM `question_setters` JOIN `login` ON `question_setters`.lid = `login`.id WHERE `type`="pending" AND `question_setters`.subject = %s'
    res = selectall2(qry, session['subject'])
    return render_template("moderators/verify_qs.html", val=res)


@app.route("/accept_qs")
def accept_qs():
    id = request.args.get('id')
    qry = 'UPDATE `login` SET `type`="question_setter" WHERE `id`=%s'
    iud(qry, id)
    return '''<script>alert("successfully accepted");window.location="/verify_qs"</script>'''


@app.route("/reject_qs")
def reject_qs():
    id = request.args.get('id')
    qry = 'UPDATE `login` SET `type`="rejected" WHERE `id`=%s'
    iud(qry, id)
    return '''<script>alert("successfully rejected");window.location="/verify_qs"</script>'''

@app.route("/error_report")
def error_report():
    return render_template("moderators/Error_report.html")


@app.route("/question_setter_home")
def question_setter_home():
    return render_template("Question_setter/qs_index.html")


@app.route("/question_setter_activity")
def question_setter_activity():
    return render_template("Question_setter/qs_activity.html")


@app.route("/question_insert", methods=['post'])
def question_insert():
    question = request.form['question']
    option1 = request.form['option1']
    option2 = request.form['option2']
    option3 = request.form['option3']
    option4 = request.form['option4']
    solution = request.form['solution']

    qry = "INSERT INTO `questions` VALUES(NULL,%s,%s,%s,%s,%s,%s,%s,curdate(),'pending')"
    iud(qry, (session['lid'],question,option1,option2,option3,option4,solution))

    return '''<script>alert("Added");window.location="question_setter_home"</script>'''


@app.route("/view_my_qstn")
def view_my_qstn():
    qry = "SELECT * FROM `questions` WHERE `qs_id`=%s"
    res = selectall2(qry, session['lid'])
    return render_template("Question_setter/view_my_qstn.html", val=res)

@app.route("/mod_contact")
def mod_contact():
    qry = "SELECT * FROM `questions` WHERE `qs_id`=%s"
    res = selectall2(qry, session['lid'])
    return render_template("Question_setter/mod_contact.html", val=res)



@app.route("/attend_exam")
def attend_exam():
    qry = "SELECT DISTINCT(`subject`) FROM `question_setters` "
    res = selectall(qry)
    return render_template("TestTaker/exam1.html", val=res)


@app.route("/attend_exam2", methods=['post'])
def attend_exam2():
    subject = request.form['select']
    session['subject'] = subject
    qry = "SELECT `question_setters`.`lid` from question_setters WHERE `subject`=%s"
    res = selectall2(qry, subject)

    total = 0

    for i in res:
        qry = "SELECT COUNT(*) AS count FROM `questions` WHERE `qs_id`=%s"
        count = selectall2(qry,i['lid'])
        print(i,"==")
        print(count)

        total = total + int(count[0]['count'])
    return render_template("TestTaker/exam2.html", val=res, tot=total)


@app.route("/attend_exam3", methods=['post'])
def attend_exam3():
    no = request.form['textfield']

    session['no'] = no

    # questions = []
    #
    # qry = "SELECT `question_setters`.`lid` from question_setters WHERE `subject`=%s"
    # res = selectall2(qry, session['subject'])
    #
    # for i in res:
    #     qry = "SELECT * FROM `questions` WHERE `qs_id`=%s"
    #     res = selectall2(qry, i['lid'])
    #     questions.append(res)
    # print(questions)

    qry = "SELECT `questions`.* FROM `questions` JOIN `question_setters` ON `questions`.`qs_id` = `question_setters`.`lid` WHERE `question_setters`.`subject` = %s LIMIT %s"
    res = selectall2(qry, (session['subject'], int(no)))
    print(res)

    question_list = []

    opt=[]
    for i in res:
        options=[i['answer'],i['option1'],i['option2'],i['option3']]
        random.shuffle(options)
        opt.append(options)

    for i in res:
        question_list.append(i['qid'])

        print(question_list,"================")

    session['question_list'] = question_list

    return render_template("TestTaker/attend_exam.html", val=res,option=opt)



@app.route("/attend_exam4", methods=['post'])
def attend_exam4():

    if len(request.form) == 0:
        return '''<script>alert("Please Attend All the questions");window.location="/attend_exam"</script>'''

    option_list = []

    question_list = session.get('question_list', [])

    mark = 0

    for i in range(1,int(session['no'])+1):

        option_list.append(request.form['answer'+str(i)])
        qry = "INSERT INTO `exam` VALUES(NULL,%s,%s,%s,CURDATE())"
        iud(qry, (session['lid'], question_list[i-1], request.form['answer'+str(i)] ))

        qry = "SELECT * FROM `questions` WHERE `qid`=%s"
        res = selectone(qry, question_list[i-1])
        if res['answer'] == request.form['answer'+str(i)]:
            mark = mark+1

    print(option_list)
    print(question_list,"======")

    qry = "SELECT * FROM `questions` WHERE `qid`=%s OR `qid` =%s OR `qid`=%s"
    res = selectall2(qry, tuple(question_list))

    return render_template("TestTaker/Result.html", val = mark, options = option_list, qstns = res)


@app.route("/view_verified_questions")
def view_verified_questions():
    qry = "SELECT * FROM `questions` JOIN `question_setters` ON `questions`.`qs_id` = `question_setters`.`lid` JOIN `moderators` ON `question_setters`.`subject` = `moderators`.`subject` WHERE `status`='accepted' AND `moderators`.`lid`=%s"
    res = selectall2(qry, session['lid'])

    return render_template("moderators/verified_question.html", val=res)


@app.route("/view_verified_questions_setters")
def view_verified_questions_setters():
    qry = "SELECT * FROM `question_setters` JOIN `login` ON `question_setters`.lid=`login`.id JOIN `moderators` ON `question_setters`.`subject` = `moderators`.`subject` WHERE `type`='question_setter' AND `moderators`.`lid`=%s"
    res = selectall2(qry, session['lid'])

    return render_template("moderators/view_question_setters.html", val=res)


app.run(debug = True)