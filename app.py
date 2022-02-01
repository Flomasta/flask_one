from datetime import datetime
from flask import Flask, request, render_template, redirect
import os

# simple mail transfer protocol
import smtplib

# database
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# database
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///src/friends.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# create db model
class Friends(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<Name %r>" % self.id


SITE_NAME = 'Flo Flask'
subscribers = []


@app.route('/')
def index():
    title = SITE_NAME
    return render_template('index.html', title=title)


@app.route('/about/')
def about():
    title = 'About ' + SITE_NAME
    names = ['John', 'Mary', 'Wes', 'Sally']
    return render_template('about.html', names=names, title=title)


@app.route('/contact/')
def contact():
    title = 'Contact ' + SITE_NAME
    return render_template('contact.html', title=title)


@app.route('/subscribe')
def subscribe():
    title = 'Subscribe to my Email Newsletter '
    return render_template('subscribe.html', title=title)


@app.route('/friends', methods=['POST', 'GET'])
def friends():
    title = 'Friends ' + SITE_NAME
    friend_name = request.form.get('name')
    new_friend = Friends(name=friend_name)
    if request.method == 'POST':
        try:
            db.session.add(new_friend)
            db.session.commit()
            return redirect('/friends')
        except:
            return 'There was an error'
    else:
        friends = Friends.query.order_by(Friends.date_created)
        return render_template('friends.html', title=title, friends=friends)


@app.route('/form', methods=['POST'])
def form():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    pp = os.environ.get('pass_for_flask_project')
    message = 'You have been subscribed to my email newsletter!'
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('flovrik@gmail.com', os.environ.get('pass_for_flask_project'))
    server.sendmail('flovrik@gmail.com', email, message)

    if not first_name or not last_name or not email:
        error_statement = 'All form fields required'
        return render_template('subscribe.html',
                               error_statement=error_statement,
                               first_name=first_name,
                               last_name=last_name,
                               email=email)

    subscribers.append(f"{first_name} {last_name} | {email}")
    title = 'Thank you!'
    return render_template('form.html', subscribers=subscribers, title=title)


@app.route('/updates/<int:id>', methods=['POST', 'GET'])
def updates(id):
    title = 'Update friend'
    friend_to_update = Friends.query.get_or_404(id)
    if request.method == 'POST':
        friend_to_update.name = request.form['name']
        try:
            db.session.commit()
            return redirect('/friends')
        except:
            return 'There was a problem'
    else:
        return render_template('updates.html', title=title, friend_to_update=friend_to_update)


@app.route('/delete/<int:id>', methods=['POST', 'GET'])
def delete(id):
    friend_to_delete = Friends.query.get_or_404(id)
    try:
        db.session.delete(friend_to_delete)
        db.session.commit()
        return redirect('/friends')
    except:
        return 'A problem deliting'


if __name__ == '__main__':
    app.run()
