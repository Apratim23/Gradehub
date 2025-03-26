from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'pass123'
app.config['MYSQL_DB'] = 'gradehub'

mysql = MySQL(app)

 # Route for base template
@app.route('/')
def home():
    if 'loggedin' in session:
        return redirect(url_for('dashboard'))
    else:
        return render_template('base.html')


# Route for login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            return redirect(url_for('dashboard'))
        else:
            return 'Incorrect username/password!'
    return render_template('login.html')

# Route for registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO users VALUES(NULL, %s, %s, %s)', (username, email, password))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('login'))
    return render_template('register.html')


# Route for dashboard
@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM grades WHERE user_id = %s', (session['id'],))
        grades = cursor.fetchall()
        return render_template('dashboard.html', grades=grades)
    return redirect(url_for('login'))

# Route for editing profile
@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'loggedin' in session:
        if request.method == 'POST':
            email = request.form.get('email')
            cursor = mysql.connection.cursor()
            cursor.execute('UPDATE users SET email = %s WHERE id = %s', (email, session['id']))
            mysql.connection.commit()
            cursor.close()
            return 'Profile updated!'
        return render_template('edit_profile.html')
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/enter_grades', methods=['GET', 'POST'])
def enter_grades():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        if request.method == 'POST':
            user_id = request.form.get('user_id')
            subject = request.form.get('subject')
            grade = request.form.get('grade')

            # Check if user_id is valid
            cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))
            user = cursor.fetchone()
            if user:
                cursor.execute('INSERT INTO grades VALUES(NULL, %s, %s, %s)', (user_id, subject, grade))
                mysql.connection.commit()
                cursor.close()
                return 'Grade entered successfully!'
            else:
                return 'User does not exist. Please register the user first.'
        return render_template('enter_grades.html', users=users)
    return redirect(url_for('login'))




if __name__ == '__main__':
    app.run(debug=True)
