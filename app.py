from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Regexp
from flask_sqlalchemy import SQLAlchemy
import os



basedir=os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)


app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
                                      'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)





class Student(db.Model):
    __tablename__ = 'students'
    num = db.Column(db.Integer, primary_key=True)
    SN = db.Column(db.String(20), unique=True)
    firstName = db.Column(db.String(64))
    lastName = db.Column(db.String(64))
    

class BathroomLog(db.Model):
    __tablename__ = 'bathroomlogs'
    num = db.Column(db.Integer, primary_key=True)
    SN = db.Column(db.String(20), unique=False)
    timestamp = db.Column(db.DateTime)
    status =db.Column(db.String(64))
    

class Attendance(db.Model):
    __tablename__ = 'attendance'
    num = db.Column(db.Integer, primary_key=True)
    SN = db.Column(db.String(20), unique=False)
    period = db.Column(db.Integer)
    status =db.Column(db.String(64))
    timestamp = db.Column(db.DateTime)


class ClubAttendance(db.Model):
    __tablename__ = 'clubattendance'
    num = db.Column(db.Integer, primary_key=True)
    SN = db.Column(db.String(64), db.ForeignKey("students.SN"))
    status = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime)
    

class AddStudentForm(FlaskForm):
    fname = StringField("What is you first name?", [DataRequired()])
    lname = StringField("What is you last name?", [DataRequired()])
    SN = StringField("What is your Student Number?", [Regexp( regex="[0][6][0-9]{8}" ,message="That's not a real Student Number")])
    submit = SubmitField('Submit')

class BathroomForm(FlaskForm):
    SN = StringField("Student Number:", [DataRequired()])
    submit = SubmitField('Submit')

class AttendanceForm(FlaskForm):
    SN = StringField("Student Number:", [DataRequired()])
    submit = SubmitField('Submit')

@app.route('/Bathroom', methods=['GET', 'POST'])
def Bathroom():
    form = BathroomForm()
    SN=None
    f = '%Y-%m-%d %H:%M:%S'
    print([log.__dict__ for log in BathroomLog.query.all()])
    if form.validate_on_submit():
        print("validated")
        SN = form.SN.data
        cur_student=BathroomLog.query.order_by(BathroomLog.num.desc()).filter_by(SN=SN).first()
        if cur_student is None or cur_student.status=="In":
            now = datetime.now()
            cur_student = BathroomLog(SN=SN,status="Out", timestamp=now )
            db.session.add(cur_student)
            db.session.commit()
            print("Left")
        else:
            now = datetime.now()
            cur_student = BathroomLog(SN=SN,status="In", timestamp=now )
            db.session.add(cur_student)
            db.session.commit()
            print("Returned")
        print("reloading")
        return redirect(url_for("Bathroom"))   
    else: 
        return render_template('Bathroom.html', form=form)

@app.route('/addStudent', methods=['GET', 'POST'])
def addStudent():
    form = AddStudentForm()
    fname=None
    if form.validate_on_submit():
        fname = form.fname.data
        lname = form.lname.data
        SN = form.SN.data
        new_student = Student(firstName = fname, lastName = lname, SN=SN)
        db.session.add(new_student)
        db.session.commit()

        return redirect(url_for("addStudent"))
    return render_template('addStudent.html', form=form, fname=fname)

@app.route('/showStudents', methods=['GET', 'POST'])
def showStudents():
    students = [s.__dict__ for s in Student.query.order_by(Student.lastName).all()]
    print(students)
    
    return render_template('showStudents.html', students=students)

@app.route('/showBathroomLog', methods=['GET', 'POST'])
def showBathroomLog():
    logdb = db.session.query(BathroomLog, Student).order_by(BathroomLog.num.desc()).filter(BathroomLog.SN == Student.SN).all()
    #[ (<BathroomLog 3>, <Student 2>), (<BathroomLog 2>, <Student 1>), (<BathroomLog 1>, <Student 1>)]
    print(type(logdb))
    log = [{**entry[0].__dict__,  **entry[1].__dict__}for entry in logdb]
    return render_template('showBathroomLog.html', log=log)

@app.route('/showAttendance', methods=['GET', 'POST'])
def showAttendance():
    now = datetime.now()
    howMuch="today"
    period = "1"
    AllAttendance = db.session.query(Attendance, Student).order_by(Attendance.timestamp, Student.lastName, Student.firstName).filter(Attendance.SN == Student.SN).all()
    fullLog=[{**entry[0].__dict__, **entry[1].__dict__} for entry in AllAttendance]
    todayByPeriodDB=db.session.query(Attendance, Student).order_by(Student.lastName, Student.firstName).filter(Attendance.SN == Student.SN, Attendance.period ==period).all()
    todayByPeriodDict=[{**entry[0].__dict__, **entry[1].__dict__} for entry in todayByPeriodDB]

    # todayP2
    # todayP3
    # todayP4
    print(fullLog)
    # log = [{**entry[0].__dict__,  **entry[1].__dict__}for entry in logdb]
    return render_template('showAttendance.html',  today=todayByPeriodDict, full=fullLog, now=now,  howMuch=howMuch)


@app.route('/Attendance', methods=['GET', 'POST'])
def attendance():
    form = AttendanceForm()
    if form.validate_on_submit():
        print("validated")
        SN = form.SN.data
        now = datetime.now()
        if(now.hour<9): period=1
        elif(now.hour<10): period=2
        elif(now.hour<12): period =3
        elif(now.hour<15): period= 4
        else: period=0
        cur_student = Attendance(SN=SN, period=period, status="present", timestamp=now)
        db.session.add(cur_student)
        db.session.commit()
        return redirect(url_for("attendance"))

    return render_template('Attendance.html', form=form)
