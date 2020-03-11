from flask import Flask, render_template, request, redirect, url_for, make_response, session
from flask_mail import Mail, Message
import sqlite3
import random
import validators
from datetime import datetime
import string

conn = sqlite3.connect('URLshortnerDB.db', check_same_thread=False)
c = conn.cursor()
val =""


def randomid():
        tc = conn.cursor()
        uid = random.randint(100, 10000)
        sql = 'SELECT COUNT(*) FROM user where userid="%s"' % uid
        tc.execute(sql)
        sz1 = tc.fetchone()
        if str(sz1[0]) == "1":
            randomid()
        else:
            return uid


def getTimeandDate():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    return dt_string


def shorten():
    sc = conn.cursor()
    scode = ''.join(random.choices(string.ascii_uppercase + string.digits, k = 7)) 
    sql = 'SELECT COUNT(*) FROM link where short_url="%s"' % scode
    sc.execute(sql)
    sz2 = sc.fetchone()
    if str(sz2[0]) == "1":
        shorten()
    else:
        return scode


app = Flask(__name__)
app.secret_key = 'summaSecret'

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'your_Gmail_ID@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_mail_password_here'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)


@app.route('/', methods=['POST', 'GET'])
def home():
    userID = str(request.cookies.get('userID'))
    if request.method == 'POST':
        if userID != "0":
            return render_template('home.html', sval="Short URL")
        elif userID is None:
            return render_template('home.html', lval="Login")
        else:
            return render_template('home.html', lval="Login")
    else:
        if userID != "0":
            return render_template('home.html', sval="Short URL")
        elif userID is None:
            return render_template('home.html', lval="Login")
        else:
            return render_template('home.html', lval="Login")


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        id = str(randomid())
        name = str(request.form['name'])
        email = str(request.form['email'])
        password = str(request.form['password'])

        c.execute('SELECT COUNT(*) FROM user where email="%s"' % email)
        sz = c.fetchone()
        if str(sz[0]) == "1":
            return "User Already Exists!"
        else:
            c.execute(''' INSERT INTO user(userid, name, email, password ) VALUES(?,?,?,?)''',(id, name, email, password))
            conn.commit()
            return "User Registration Successful! "+id+" "+name+" "+email+" "+password

    else:
        return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        cl = conn.cursor()
        email = str(request.form['email'])
        password = str(request.form['password'])
        cl.execute('SELECT COUNT(*) FROM user where email="%s" AND password="%s"' % (email, password))
        s = cl.fetchone()
        if str(s[0]) == "1":
            resp = make_response(render_template('home.html', sval="Short URL"))
            cl.execute('SELECT userid FROM user where email="%s"' %email)
            uid = cl.fetchone()
            resp.set_cookie('userID', uid[0])
            session['userID'] = str(uid[0])
            return resp
        else:
            return render_template('login.html', invalid="--> Invalid Credentials!")
    else:
        return render_template('login.html')


@app.route('/send-mail', methods=['POST', 'GET'])
def contactus():
    if request.method == 'POST':
        name = str(request.form['Name'])
        email = str(request.form['Email'])
        subject = str(request.form['Subject'])
        comments = str(request.form['Comments'])
        comments = "Name: "+name+"\n"+"E-mail: "+email+"\n"+"Comments: "+comments

        msg = Message(subject, sender="your_email_id_that_you_have_given_above", recipients=['your_mail@gmail.com'], body=comments)
        mail.send(msg)
        #print("Dbg: Comments: "+comments)
        return render_template('infopage.html', infoMessage="Mail Sent Successfully!")


@app.route('/shortURL', methods=['POST', 'GET'])
def shorturl():
    userID = str(request.cookies.get('userID'))
    if request.method == 'POST':
        if userID != "0":
            original_url = str(request.form['ourl'])
            if validators.url(original_url) and original_url is not None:
                short_url = str(shorten())
                timeanddate = str(getTimeandDate())
                sc = conn.cursor()
                sc.execute(''' INSERT INTO link (userid, original_url, short_url, visits, date_created ) VALUES(?,?,?,?,?)''',(userID, original_url, short_url, "0", timeanddate))
                conn.commit()
                return render_template('shortner.html', process="URL Shrinked Successfully!", code = short_url)
            else:
                return render_template('shortner.html', process="Not a Valid URL!")
        else:
            return render_template('home.html', lval="Login")

    else:
        if userID != "0":
            return render_template('shortner.html')
        else:
            return render_template('home.html', lval="Login")


@app.route('/myurl')
def myurl():
    userID = str(request.cookies.get('userID'))
    if userID != "0":
        ml = conn.cursor()
        cursor = ml.execute('SELECT date_created, original_url, short_url, visits FROM link where userid="%s"'%userID)
        items = cursor.fetchall()
        return render_template('myURLstats.html', items=items)
    else:
        return render_template('home.html', lval="Login")


@app.route('/s/<url>')
def RedirecttoOriginalURL(url):
        rc = conn.cursor()
        rc.execute('SELECT COUNT(*) FROM link where short_url="%s"' % url)
        sz4 = rc.fetchone()
        if str(sz4[0]) == "1":
            rc.execute('SELECT original_url, visits FROM link where short_url="%s"' %url)
            sz5 = rc.fetchone()
            oriURL = str(sz5[0])
            visits = int(sz5[1])
            visits = visits + 1
            rc.execute('Update link set visits = "%d" where short_url = "%s"' % (visits, url))
            conn.commit()
            return redirect(oriURL)
        else:
            return render_template('NotFound.html')


@app.route('/404')
def pagenotfound():
    return render_template('NotFound.html')


@app.route('/logout')
def logout():
    re = make_response(render_template('home.html', lval="Login"))
    re.set_cookie('userID', "0")
    session.pop('userID', None)
    return re


@app.route('/showTables')
def db():
    id = str(request.cookies.get('userID'))
    c.execute('SELECT * FROM user')
    rows = c.fetchall()
    for row in rows:
        return str(rows)


@app.route('/forgot')
def forgot():
    return render_template('forgot.html')


@app.route('/createDB')
def createDB():
    c.execute('''CREATE TABLE user ( userid VARCHAR(15) PRIMARY KEY,
                    name VARCHAR(30),
                    email VARCHAR(50) UNIQUE,
                    password VARCHAR(30) )''')

    c.execute('''CREATE TABLE link ( userid VARCHAR(15),
                   original_url VARCHAR(500),
                   short_url VARCHAR(250)
                   UNIQUE, visits VARCHAR(30),
                   date_created VARCHAR(30),
                   FOREIGN KEY (userid) REFERENCES user(userid))''')

    conn.commit()
    return "Database Created Successfully!"


@app.route('/insertDemo')
def insertDB():
    #c.execute('''INSERT INTO user ("123456789", "Prabhu", "prabhuacse@gmail.com", "prabhu/123")''')
    try:
        c.execute(''' INSERT INTO user(userid, name, email, password ) VALUES(?,?,?,?)''',("123", "Prabhu", "prabhuacse@gmail.com", "prabhu/1234"))
        conn.commit()
        return "Inserted Successfully!"

    except:
        return "Error: Data Already Exists!"


@app.route('/debugERROR')
def debugERROR():
    # email = "techbufftami@gmail.com"
    # c.execute('SELECT COUNT(*) FROM user where email="%s"' % email)
    # sz = c.fetchone()
    # if str(sz[0]) == "1":
    #     return "User Already Exists"
    # else:
    #     return "False"
    dc = conn.cursor()
    sql = 'SELECT original_url, visits FROM link where short_url="GYCPK8V"' 
    dc.execute(sql)
    sz7 = dc.fetchone()
    return str(sz7[1])


if __name__ == '__main__':
    app.run(debug=True)


#
# 
# CREATE TABLE nuser (
#userid VARCHAR(15) PRIMARY KEY,
#name VARCHAR(30),
#email VARCHAR(50) UNIQUE,
#password VARCHAR(30)
#);
# 
# 
# 
# 
# 
# 
# 
# #