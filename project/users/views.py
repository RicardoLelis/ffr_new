# project/users/views.py
 
 
#################
#### imports ####
#################
from threading import Thread
from flask import render_template, Blueprint, request, redirect, url_for, flash, abort
from project import app, db, mail
from project.models import User
from .forms import RegistrationForm, LoginForm, EmailForm, PasswordForm
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, current_user, login_required, logout_user
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime

################
#### config ####
################

users_blueprint  = Blueprint('users', __name__)

#################
#### helpers ####
#################

def send_async_email(msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, recipients, html_body):
    msg = Message(subject, recipients=recipients)
    msg.html = html_body
    thr = Thread(target=send_async_email, args = [msg])
    thr.start()

def send_confirmation_email(user_email):
    confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
 
    confirm_url = url_for(
        'users.confirm_email',
        token=confirm_serializer.dumps(user_email, salt='email-confirmation-salt'),
        _external=True)
 
    html = render_template(
        'email_confirmation.html',
        confirm_url=confirm_url)
 
    send_email('Confirm Your Email Address', [user_email], html)

def send_password_reset_email(user_email):
    password_reset_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    password_reset_url = url_for(
        'users.reset_with_token',
        token = password_reset_serializer.dumps(user_email, salt='password-reset-salt'),
        _external=True)

    html = render_template(
        'email_password_reset.html',
        password_reset_url=password_reset_url)

    send_email('Password Reset Requested', [user_email], html)


################
#### routes ####
################

@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is not None and user.is_correct_password(form.password.data):
                user.authenticated = True
                user.last_logged_in = user.current_logged_in
                user.current_logged_in = datetime.now()
                db.session.add(user)
                db.session.commit()
                login_user(user)
                flash('Thanks for logging in, {}'.format(current_user.email))
                return redirect(url_for('recipes.index'))
            else:
                flash('ERROR! Incorrect login credentials.', 'error')
    return render_template('login.html', form=form)



@users_blueprint.route('/logout')
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    flash('Goodbye!', 'info')
    return redirect(url_for('users.login'))


@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                new_user = User(form.email.data, form.password.data)
                new_user.authenticated = True
                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
 
                send_confirmation_email(new_user.email)
                flash('Thanks for registering!  Please check your email to confirm your email address.', 'success')
                return redirect(url_for('recipes.index'))
            except IntegrityError:
                db.session.rollback()
                flash('ERROR! Email ({}) already exists.'.format(form.email.data), 'error')
    return render_template('register.html', form=form)


@users_blueprint.route('/confirm/<token>')
def confirm_email(token):
    try:
        confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = confirm_serializer.loads(token, salt='email-confirmation-salt', max_age=3600)
    except:
        flash('The confirmation link is invalid or has expired.', 'error')
        return redirect(url_for('users.login'))

    user = User.query.filter_by(email=email).first()

    if user.email_confirmed:
        flash('Account already confirmed. Please login.', 'info')
    else:
        user.email_confirmed = True
        user.email_confirmed_on = datetime.now()
        db.session.add(user)
        db.session.commit()
        flash('Thank you for confirming your email address!', 'success')
 
    return redirect(url_for('recipes.index'))

@users_blueprint.route('/reset', methods=["GET", "POST"])
def reset():
    form = EmailForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first_or_404()
        except:
            flash('Invalid email address!', 'error')
            return render_template('password_reset_email.html', form=form)

        if user.email_confirmed:
            send_password_reset_email(user.email)
            flash('Please check your email for a password reset link.', 'success')
        else:
            flash('Your email address must be confirmed before attempting a password reset.', 'error')
        return redirect(url_for('users.login'))

    return render_template('password_reset_email.html', form=form)


@users_blueprint.route('/reset/<token>', methods=["GET", "POST"])
def reset_with_token(token):
    try:
        password_reset_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = password_reset_serializer.loads(token, salt='password-reset-salt', max_age=3600)
    except:
        flash('The password reset link is invalid or has expired.', 'error')
        return redirect(url_for('users.login'))

    form = PasswordForm()

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=email).first_or_404()
        except:
            flash('Invalid email address!', 'error')
            return redirect(url_for('users.login'))

        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('users.login'))

    return render_template('reset_password_with_token.html', form=form, token=token)

@users_blueprint.route('/user_profile')
@login_required
def user_profile():
    return render_template('user_profile.html')


@users_blueprint.route('/email_change', methods=["GET", "POST"])
@login_required
def user_email_change():
    form = EmailForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                user_check = User.query.filter_by(email=form.email.data).first()
                if user_check is None:
                    user = current_user
                    user.email = form.email.data
                    user.email_confirmed = False
                    user.email_confirmed_on = None
                    user.email_confirmation_sent_on = datetime.now()
                    db.session.add(user)
                    db.session.commit()
                    send_confirmation_email(user.email)
                    flash('Email changed!  Please confirm your new email address (link sent to new email).', 'success')
                    return redirect(url_for('users.user_profile'))
                else:
                    flash('Sorry, that email already exists!', 'error')
            except IntegrityError:
                flash('Error! That email already exists!', 'error')
    return render_template('email_change.html', form=form)


@users_blueprint.route('/password_change', methods=["GET", "POST"])
@login_required
def user_password_change():
    form = PasswordForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = current_user
            user.password = form.password.data
            db.session.add(user)
            db.session.commit()
            flash('Password has been updated!', 'success')
            return redirect(url_for('users.user_profile'))
    
    return render_template('password_change.html', form=form)

@users_blueprint.route('/resend_confirmation')
@login_required
def resend_email_confirmation():
    try:
        send_confirmation_email(current_user.email)
        flash('Email sent to confirm your email address. Please check your email!', 'success')
    except IntegrityError:
        flash('Error! Unable to send email confirmation to confirm your email address.', 'error')
    
    return redirect(url_for('users.user_profile'))

@users_blueprint.route('/admin_view_users')
@login_required
def admin_view_users():
    if current_user.role != 'admin':
        abort(403)
    else:
        users = User.query.order_by(User.id).all()
        return render_template('admin_view_users.html', users=users)
    return redirect(url_for('index'))

############################
#### custom error pages ####
############################

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),  404

@app.errorhandler(403)
def page_not_found(e):
    return render_template('403.html'),  403

@app.errorhandler(410)
def page_not_found(e):
    return render_template('410.html'),  410


