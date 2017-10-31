from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:lastoneforu2@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key ='z448lHdzt&aQ2C'


class Blog(db.Model):

    #instance variables of the Blog class
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    #Blog constructor with three parameters
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    #instance variables of the User class
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')


    #User constructor with two parameters
    def __init__(self, username, password):
        self.username = username
        self.password = password



@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog', 'display']
    if request.endpoint not in  allowed_routes and 'username'not in session:
        return redirect('/login')                


@app.route('/login', methods= ['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        #does the user exist
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')    

        if not user:
            flash('User does not exist', 'error')
            return render_template('login.html')

        if user.password != password:
                flash('Incorrect password submitted', 'error')
                return render_template('login.html')
    
    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        # validate user's info
        existing_user = User.query.filter_by(username=username).first()
        error_exist = False

        if username == '':
            error_exist = True
            flash('Please enter a name', 'error')
        else:
            username=username
            if len(username) < 3:
                error_exist = True
                flash('Please enter a name with at least 3 characters long', 'error')
            else:
                username=username
                if existing_user:
                    error_exist = True
                    flash('User already exists', 'error')
                else:
                    username=username          

        if password == '':
            error_exist = True
            flash('Please enter a password', 'error')
            password = ''
        else:
            password=password
            if len(password) < 3:
                error_exist = True
                flash('Password needs to be greater than 2 characters long', 'error')
                password = ''
            else:
                password=password

        if verify == '':
            error_exist = True
            flash('Please verify your password', 'error')
            verify = ''
        else:
            verify=verify                                        
            if verify != password:
                error_exist = True
                flash('Passwords DO NOT match', 'error')
                verify = ''
            else:
                verify=verify

        if error_exist:
            return render_template('signup.html')
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

    return render_template('signup.html')

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    del session['username']
    return redirect('/')


@app.route('/newpost', methods=['POST', 'GET'])
def entry ():

    if request.method == 'POST':
        title_name = request.form['title-blog']
        text = request.form['body'] 
        owner = User.query.filter_by(username=session['username']).first()

        #object instance create through the Blog constructor
        new_blog = Blog(title_name, text, owner)

        if new_blog.title == '':
            flash('Please enter a title for the blog', 'error')   

        if new_blog.body == '':
            flash('What would you like to say in your blog', 'error')   

        if not new_blog.title == '' and not new_blog.body == '':
            db.session.add(new_blog)
            db.session.commit()

            return redirect('/display?blog-id='+str(new_blog.id))
        else:
            return render_template('entry.html') 
        
        #get request
    return render_template('entry.html')


@app.route('/blog', methods = ['POST', 'GET'])
def list_blog ():

    owner = User.query.filter_by(username=session['username']).first()
    if request.args.get('owner'):
        user_id = request.args.get('owner')
        owner_blogs = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('blog_list.html', blogs=owner_blogs)

    blogs=Blog.query.all() 
    return render_template('blog_list.html', blogs=blogs)


@app.route('/display', methods = ['GET'])
def display():

    owner = User.query.filter_by(username=session['username']).first()
    blog_id = request.args.get('blog-id')
    blog = Blog.query.get(blog_id)
    return render_template('ind_blog.html', blog=blog)

@app.route('/')
def index():
    
    allusers = User.query.all()
    return render_template('index.html', allusers=allusers)
    

if __name__ == '__main__':
    app.run()