# 1. Import Library
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import random
import string
import os

# 2. Create a Flask App
app = Flask(__name__)

# 3. SQLAlchemy Configuration and pass the application into SQLAlchemy class
basedir = os.path.abspath(os.path.dirname(__file__))
path = 'sqlite:///' + os.path.join(basedir, 'data.sqllite')
app.config['SQLALCHEMY_DATABASE_URI'] = path
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False


db = SQLAlchemy(app)
Migrate(app,db)

# 4. Define a Model and Table
class Database(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.String())
    shorted_url = db.Column(db.String(15))

    def __init__(self, long_url, shorted_url):
        self.long_url = long_url
        self.shorted_url = shorted_url
    def __repr__(self) -> str:
        return f"{self.long_url} - {self.shorted_url}"


        
@app.before_first_request
def create_tables():
  
  db.create_all()



# 5. Create a Shorten URL Characters
def shorten_url():
    characters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    while True:
        rand_char = random.choices(characters, k=5)
        rand_char = "".join(rand_char)
        short_url = Database.query.filter_by(shorted_url=rand_char).first()
        if not short_url:
            return rand_char

# 6. Create end points
@app.route('/', methods=['POST', 'GET'])
def main():
    if request.method == "POST":
        url_received = request.form["url_link"]
        found_url = Database.query.filter_by(long_url=url_received).first()

        if found_url:
            return redirect(url_for("display_short_url", url=found_url.shorted_url))
        
        else:
            short_url = shorten_url()
            new_url = Database(url_received, short_url)
            db.session.add(new_url)
            db.session.commit()
            return redirect(url_for("display_short_url", url=short_url))
    else:
        return render_template('URL_page.html')

@app.route('/<short_url>')
def redirect_to_main_website(short_url):
    original_url = Database.query.filter_by(shorted_url=short_url).first()
    if original_url:
        return redirect(original_url.long_url)
    else:
        return f'<h1>Url doesnt exist</h1>'

@app.route('/display/<url>')
def display_short_url(url):
    return render_template('URL_page.html', short_url_display=url)

@app.route('/history')
def history():
    return render_template('check_URL_history.html', vals= Database.query.all())



@app.route('/delete/<int:id>')
def delete(id):
    url = Database.query.filter_by(id=id).first()
    db.session.delete(url)
    db.session.commit()
    return redirect("/history")

# 7. Run the App
if __name__ == '__main__':
     app.run(debug=True)
    