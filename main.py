from flask import Flask, render_template, request, url_for, session, redirect
from flask_mysqldb import MySQL
import re

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
app = Flask(__name__)

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = ""
app.config["MYSQL_DB"] = "test"

app.config['SECRET_KEY'] = 'hehe'

mysql = MySQL(app)
print("db connected",mysql)


@app.route('/')
def home():
    if 'name' in session:
        return render_template('home.html',title = 'home')
        
    else:   
        return redirect(url_for('login')) 
        
    
@app.route('/profile',methods=['GET', 'POST'])
def profile():
    if 'name' in session:
        if request.method == 'POST':
            oldpassword = request.form.get('currentpass')
            newpassword = request.form.get('newpass')
 
            try:
                cursor = mysql.connection.cursor()
            except:
                db_error = 1
                message = "Couldn't connect to the database"
                return render_template('login.html',title = 'Database Error',db_error = db_error,message=message)              
            else:
                sql = f"SELECT password from login WHERE password = '{oldpassword}'"
                cursor.execute(sql)
                correctpass = cursor.fetchone()
                print(correctpass)
                if correctpass:
                    sql = "UPDATE login SET password = %s WHERE password = %s"
                    value = (newpassword,oldpassword)
                    cursor.execute(sql,value)
                    mysql.connection.commit()
                    
                    passupdated = 1
                    message = "Password Updated!"
                    return render_template('profile.html',title = 'Password Updated',passupdated=passupdated,message=message)  

                else:
                    message = "current password is incorrect"   
                    incorrect_pass = 1
                    return render_template('profile.html',title = 'Current password invalid',incorrect_pass=incorrect_pass,message=message)   
                
            
        else:
            return render_template('profile.html',title = 'profile')  
        
    else:   
        return redirect(url_for('login'))     
    

@app.route('/login',methods=['GET', 'POST'])
def login():


    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            cursor = mysql.connection.cursor()
        except:
            db_error = 1
            message = "Couldn't connect to the database"
            return render_template('login.html',title = 'Database Error',db_error = db_error,message=message)  
        else:    

            try:
                
                cursor.execute('SELECT * FROM login WHERE email = %s AND password = %s', (email, password,))
                account = cursor.fetchone()
    
                if account:

                    session['email'] = email
                    cursor.execute('SELECT name FROM login WHERE email = %s AND password = %s', (email, password,))
                    username = cursor.fetchone()
                    if username:
                        username_formatted = username[-1]
                        
                        session['name'] = username_formatted
                        message = "User Loggedin"
                    #account variable needs to be passed to send successful alert    
                    return render_template('home.html',title = 'home',account=account,message=message)   
    
                else:
                    message ="Incorrect Email/Password"    
                    return render_template('login.html', title="Login",message = message) 
        
            except:
                message = "No accounts exist, please create a new account"
                return render_template('register.html', title="Register",message = message) 
    elif 'name' in session:
        return render_template('home.html',title = 'loggedin')  


    return render_template('login.html',title = 'login')

@app.route('/register',methods = ['POST','GET'])
def register():
    if request.method == 'POST':
       name = request.form.get('name') 
       email = request.form.get('email') 
       password = request.form.get('password')
       confpass = request.form.get('confirmpass')
       
       try:
        cursor = mysql.connection.cursor()
       except:
        db_error = 1
        message = "Couldn't connect to the database" 
        return render_template('register.html',title = 'Database Error',db_error = db_error,message=message)  
       else: 
       
        try:
            cursor.execute("CREATE TABLE login (user_id INT AUTO_INCREMENT PRIMARY KEY ,name VARCHAR(255), email VARCHAR(255), password VARCHAR(255))")
        finally:
            cursor.execute('SELECT * FROM login WHERE email = %s',(email,))
            account = cursor.fetchone()
            if account:
                message ="Email already used! Please use different email address"
                return render_template('register.html',message=message)

            # check if name is valid
            elif not re.match(r'[A-Za-z0-9]+', name):
                message = 'Enter Valid Name'
                return render_template('register.html',title = 'Enter Valid Name',name=name,message=message)        

            # check if email is valid
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                message = 'Enter Valid Email'
                return render_template('register.html',title = 'Enter Valid Email',email=email,message=message)

            #check if no data is provided
            elif not name or not email or not password or not confpass:  
                message = 'Please fill all the details!'
                return render_template('register.html',title = 'Enter Valid Name',name=name,email=email,password=password,confpass=confpass,message=message)

            #check if password and confirm password is correct
            elif (password != confpass):
                message = "password and confirmpassword field should match!"
                return render_template('register.html',title = 'pass should match',password=password,confpass=confpass,message=message)

            else:
                sql = "INSERT INTO login(name,email,password) VALUES(%s,%s,%s)"
                value = (name,email,password)
                cursor.execute(sql,value)
                mysql.connection.commit()
                cursor.close()
                registration_complete = 1
                message = "User Registration Successful !"
                return render_template('login.html',title = 'home',registration_complete=registration_complete, message=message)     

    else:
        return render_template('register.html',title = 'Register')  
        

@app.route('/logout',methods = ['POST','GET'])
def logout():
    # Remove session data, this will log the user out
   session.pop('name', None)
   sessionend = session.pop('email', None)
   message = "User Successfully logged out"
   return render_template('login.html',sessionend=sessionend,message=message) 


app.run(debug=True,port=80)
