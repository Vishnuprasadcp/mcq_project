import flask_mail
from flask import *

from dbconnectionnew import *
from  mcq_gen import *

from flask_mail import *


from werkzeug.utils import secure_filename
import os
import random
app = Flask(__name__)
app.secret_key = "8394584658"




app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Use the server for your mail service
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'aimcqgen@gmail.com'  # Your email address
app.config['MAIL_PASSWORD'] = 'hjrm xpzn ewgi fjjn'  # Your email password
app.config['MAIL_DEFAULT_SENDER'] = ('MCQ generator', 'aimcqgen@gmail.com')

mail = Mail(app)



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

        qry = "SELECT * FROM `test_takers` WHERE lid=%s"
        res2 = selectone(qry, res['id'])
        session['name'] = res2['name']

        session['lid'] = res['id']
        return  redirect("/test_taker_home")

    elif res['type'] == "admin":
        session['lid'] = res['id']
        return  redirect("admin_home")

    elif res['type'] == "question_setter":

        qry = "SELECT * FROM `question_setters` WHERE lid=%s"
        res2 = selectone(qry, res['id'])
        session['name'] = res2['name']

        session['lid'] = res['id']
        return redirect("/question_setter_home")

    elif res['type'] == "moderator":
        session['lid'] = res['id']

        qry = "SELECT `moderators`.`subject` FROM `moderators` WHERE `lid`=%s"
        res1 = selectone(qry, session['lid'])
        session['subject'] = res1['subject']

        return redirect("/moderator_home")
    else:
        return '''<script>alert("Invalid");window.location="/"</script>'''


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


    qry = "SELECT `email` FROM `moderators` WHERE `lid`=%s"
    res = selectone(qry, id)

    def mail(email):
        try:
            gmail = smtplib.SMTP('smtp.gmail.com', 587)
            gmail.ehlo()
            gmail.starttls()
            gmail.login('aimcqgen@gmail.com', 'hjrm xpzn ewgi fjjn')
        except Exception as e:
            print("Couldn't setup email!!" + str(e))
        msg = MIMEText("You have been successfully accepted by admin")
        print(msg)
        msg['Subject'] = 'request to register'
        msg['To'] = email
        msg['From'] = 'aimcqgen@gmail.com'
        try:
            gmail.send_message(msg)
        except Exception as e:
            print("COULDN'T SEND EMAIL", str(e))
        return '''<script>alert("SEND"); window.location="/"</script>'''

    mail(res['email'])


    return '''<script>alert("successfully accepted");window.location="/Verify_Moderators"</script>'''


@app.route("/reject_moderators")
def reject_moderators():
    id = request.args.get('id')
    qry = 'UPDATE `login` SET `type`="rejected" WHERE `id`=%s'
    iud(qry, id)

    qry = "SELECT `email` FROM `moderators` WHERE `lid`=%s"
    res = selectone(qry, id)

    def mail(email):
        try:
            gmail = smtplib.SMTP('smtp.gmail.com', 587)
            gmail.ehlo()
            gmail.starttls()
            gmail.login('aimcqgen@gmail.com', 'hjrm xpzn ewgi fjjn')
        except Exception as e:
            print("Couldn't setup email!!" + str(e))
        msg = MIMEText("You have been rejected  by admin")
        print(msg)
        msg['Subject'] = 'request to register'
        msg['To'] = email
        msg['From'] = 'aimcqgen@gmail.com'
        try:
            gmail.send_message(msg)
        except Exception as e:
            print("COULDN'T SEND EMAIL", str(e))
        return '''<script>alert("SEND"); window.location="/"</script>'''

    mail(res['email'])

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

    try:
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
    except:
        return '''<script>alert("Email or phone already exists");window.location="/"</script>'''


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

    qry = "SELECT `email` FROM `question_setters` WHERE `lid`=%s"
    res = selectone(qry, id)

    def mail(email):
        try:
            gmail = smtplib.SMTP('smtp.gmail.com', 587)
            gmail.ehlo()
            gmail.starttls()
            gmail.login('aimcqgen@gmail.com', 'hjrm xpzn ewgi fjjn')
        except Exception as e:
            print("Couldn't setup email!!" + str(e))
        msg = MIMEText("You have been successfully approved as question setter")
        print(msg)
        msg['Subject'] = 'request to register'
        msg['To'] = email
        msg['From'] = 'aimcqgen@gmail.com'
        try:
            gmail.send_message(msg)
        except Exception as e:
            print("COULDN'T SEND EMAIL", str(e))
        return '''<script>alert("SEND"); window.location="/"</script>'''

    mail(res['email'])

    return '''<script>alert("successfully accepted");window.location="/verify_qs"</script>'''


@app.route("/reject_qs")
def reject_qs():
    id = request.args.get('id')
    qry = 'UPDATE `login` SET `type`="rejected" WHERE `id`=%s'
    iud(qry, id)

    qry = "SELECT `email` FROM `question_setters` WHERE `lid`=%s"
    res = selectone(qry, id)

    def mail(email):
        try:
            gmail = smtplib.SMTP('smtp.gmail.com', 587)
            gmail.ehlo()
            gmail.starttls()
            gmail.login('aimcqgen@gmail.com', 'hjrm xpzn ewgi fjjn')
        except Exception as e:
            print("Couldn't setup email!!" + str(e))
        msg = MIMEText("You have been rejected")
        print(msg)
        msg['Subject'] = 'request to register'
        msg['To'] = email
        msg['From'] = 'aimcqgen@gmail.com'
        try:
            gmail.send_message(msg)
        except Exception as e:
            print("COULDN'T SEND EMAIL", str(e))
        return '''<script>alert("SEND"); window.location="/"</script>'''

    mail(res['email'])

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


@app.route("/generatQuestion", methods=['POST'])
def generatQuestion():


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
        qry = "SELECT COUNT(*) AS count FROM `questions` WHERE `qs_id`=%s AND `status`=%s"
        count = selectall2(qry, (i['lid'], 'accepted'))  # Pass parameters as a tuple
        print(i, "==")
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

    qry = "SELECT `questions`.* FROM `questions` JOIN `question_setters` ON `questions`.`qs_id` = `question_setters`.`lid` WHERE `question_setters`.`subject` = %s  and `status`=%s LIMIT %s"
    res = selectall2(qry, (session['subject'],  'accepted', int(no)))
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
    # Corrected the quotes and added the missing closing parenthesis for the tuple in iud
    qry = "INSERT INTO `exams_attended`(tt_id,attended_date) VALUES(%s, CURDATE())"
    iud(qry, (session['lid'],))

    # Step 2: Get the last inserted row from exams_attended
    qry = "SELECT * FROM `exams_attended` ORDER BY `eid` DESC LIMIT 1"  # Replace `id` with your primary key
    last_inserted_row = selectone(qry, ())
    for i in range(1,int(session['no'])+1):

        # option_list.append(request.form['answer'+str(i)])
        # qry = "INSERT INTO `exam_records` VALUES(NULL,%s,%s,%s,CURDATE())"
        # iud(qry, (session['lid'], question_list[i-1], request.form['answer'+str(i)] ))
        option_list.append(request.form['answer' + str(i)])

        # Check if a result was returned
        if last_inserted_row:
            print("Last inserted row:", last_inserted_row)

            # Now you can use the eid from the last inserted row
            eid = last_inserted_row['eid']  # Assuming 'eid' is a column in your table
            print("Last inserted exam ID (eid):", eid)

            # Now you can use eid for further operations, such as inserting into exam_records
            qry = "INSERT INTO `exam_records` VALUES (%s, %s, %s)"
            iud(qry, (eid, question_list[i - 1], request.form['answer' + str(i)]))
        else:
            print("No records found in exams_attended.")

        qry = "SELECT * FROM `questions` WHERE `qid`=%s"
        res = selectone(qry, question_list[i-1])
        if res['answer'] == request.form['answer'+str(i)]:
            mark = mark+1

    print(option_list)
    print(question_list, "======")

    # Dynamically create placeholders based on the number of items in question_list
    placeholders = ' OR '.join(['`qid`=%s'] * len(question_list))

    # Update the query to use the correct number of placeholders
    qry = f"SELECT * FROM `questions` WHERE {placeholders}"

    # Execute the query with the tuple of question_list
    res = selectall2(qry, tuple(question_list))

    return render_template("TestTaker/Result.html", val = mark, options = option_list, qstns = res)


@app.route("/question_report")
def question_report():
    qid = request.args.get('id')
    session['report_qstn_id'] = qid
    return render_template("TestTaker/report_question.html")


@app.route("/report_question", methods=['post'])
def report_question():

    reason = request.form['textfield']

    qry = "INSERT INTO `question_report` VALUES(NULL, %s, %s, %s, CURDATE(), 'pending')"
    iud(qry, (session['lid'], session['report_qstn_id'], reason))

    return '''<script>alert("Successfully reported");window.location="test_taker_home"</script>'''



@app.route("/view_reported_questions")
def view_reported_questions():
    qry = "SELECT `questions`.*,`test_takers`.name, `question_report`.`reason`, `question_report`.id as rid FROM `questions` JOIN `question_setters` ON `questions`.`qs_id`=`question_setters`.`lid` JOIN `question_report` ON `questions`.qid = `question_report`.`qstn_id` JOIN `test_takers` ON `question_report`.lid=`test_takers`.lid JOIN `moderators` ON `question_setters`.`subject`=`moderators`.`subject` WHERE `moderators`.`lid`=%s"
    res = selectall2(qry, session['lid'])

    return render_template("moderators/Error_report.html", val=res)



@app.route("/delete_report_question")
def delete_report_question():
    id = request.args.get('id')
    rid = request.args.get('rid')
    qry = "DELETE FROM `questions` WHERE `qid`=%s"
    iud(qry, id)

    qry = 'UPDATE `question_report` SET `status`="Removed" WHERE `id`=%s'
    iud(qry, rid)

    return '''<script>alert("Removed");window.location="view_reported_questions"</script>'''


@app.route("/edit_reported_question")
def edit_reported_question():

    id = request.args.get('id')
    session['report_qstn_id'] = id
    qry = "SELECT * FROM `questions` WHERE qid=%s"
    res = selectone(qry, id)

    return render_template("moderators/edit_question.html", val=res)


@app.route("/update_question", methods=['post'])
def update_question():

    question = request.form['textfield']
    option1 = request.form['textfield2']
    option2 = request.form['textfield3']
    option3 = request.form['textfield4']
    answer = request.form['textfield5']
    solution = request.form['textfield6']

    qry = "UPDATE `questions` SET `question`=%s, `option1`=%s, `option2`=%s, `option3`=%s, `answer`=%s, `solution`=%s WHERE `qid`=%s"
    iud(qry, (question, option1, option2, option3,answer, solution, session['report_qstn_id']))


    return '''<script>alert("Updated");window.location="view_reported_questions"</script>'''


@app.route("/test_log", methods=['GET', 'POST'])
def test_log():
    selected_date = None
    results = []

    if request.method == 'POST':
        selected_date = request.form['exam_date']

        # Fetch exam records for the selected date
        qry = "SELECT * FROM `exams_attended` WHERE attended_date = %s AND tt_id=%s"
        results = selectall2(qry, (selected_date, session['lid']))

        # Calculate the score for each exam record
        for result in results:
            eid = result['eid']
            # Fetch the score for the current exam
            qry = """
                SELECT COUNT(*) AS correct_count 
                FROM `exam_records` e 
                JOIN `questions` q ON e.qid = q.qid 
                WHERE e.selected_answer = q.answer AND e.eid = %s
            """
            score = selectone(qry, (eid,))
            result['score'] = score['correct_count'] if score else 0  # Add score to result

    # Fetch distinct exam dates for the dropdown
    qry = "SELECT DISTINCT attended_date FROM `exams_attended` WHERE tt_id=%s"
    exam_dates = selectall2(qry, (session['lid'],))

    return render_template("TestTaker/test_log.html", exam_dates=exam_dates, results=results, selected_date=selected_date)


@app.route("/view_exam_details/<int:eid>")
def view_exam_details(eid):
    # Calculate score by counting correct answers
    qry = """
        SELECT COUNT(*) AS correct_count 
        FROM `exam_records` e 
        JOIN `questions` q ON e.qid = q.qid 
        WHERE e.selected_answer = q.answer AND e.eid = %s
    """
    score_data = selectone(qry, (eid,))
    score = score_data['correct_count'] if score_data else 0

    # Fetch the exam questions and answers for the specific exam ID
    qry = """
        SELECT q.question, q.option1, q.option2, q.option3, q.answer, e.selected_answer 
        FROM `exam_records` e 
        JOIN `questions` q ON e.qid = q.qid 
        WHERE e.eid = %s
    """
    exam_details = selectall2(qry, (eid,))

    # Get total number of questions
    total_questions = len(exam_details)

    # Render the result page
    return render_template("TestTaker/view_exam_details.html", qstns=exam_details, val=score,
                           total_questions=total_questions)



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