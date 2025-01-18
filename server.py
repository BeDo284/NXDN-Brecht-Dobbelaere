from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user

from data import *
from forms import *
from models import *

# Setup server
load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@login_manager.user_loader
def load_user(user_id):
    return User.objects(id=user_id).first()


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    # POST-request
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password, admin=form.admin.data)
        user.save()
        return redirect(url_for('login'))
    # GET-request
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # POST-request
    if form.validate_on_submit():
        user = User.objects(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('index'))
    # GET-request
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/logs', methods=['GET', 'POST'])
def data_default():
    form = FilterForm()
    page = int(request.args.get('page', 1))
    per_page = 50  # Number of logs per page

    logs_query = Log.objects.none()

    if request.method == 'POST':
        filters = apply_filters(form)
        logs_query = get_filtered_logs(filters=filters)

        if 'export' in request.form:
            export_csv(logs_query)

    total_logs = logs_query.count()  # Total number of matching logs
    logs = logs_query.skip((page - 1) * per_page).limit(per_page)  # Apply pagination

    return render_template(
        'data.html',
        form_data=form,
        logs=logs,
        page=page,
        per_page=per_page,
        total_logs=total_logs
    )


def apply_filters(form):
    """Build filters from the form data."""
    filters = {}
    if form.start_date.data:
        filters['date__gte'] = form.start_date.data
    if form.end_date.data:
        filters['date__lte'] = form.end_date.data
    if form.calling_id.data:
        filters['calling_id'] = form.calling_id.data
    if form.called_id.data:
        filters['called_id'] = form.called_id.data
    if form.site.data and form.site.data != 'all':
        filters['site'] = form.site.data
    return filters


@app.route('/upload', methods=['GET', 'POST'])
def upload_new_data():
    if request.method == 'GET':
        return render_template('upload.html')

    file = request.files['file']

    if file and file.filename.endswith('.csv') and file.filename.startswith('CommunicationLog'):
        response, status = get_new_data(file)
        category = "success" if status == 200 else "warning"
        flash(response, category)
        return redirect(url_for('upload_new_data'))
    else:
        flash("Invalid file type. Please upload a CSV file.", "error")
        return redirect(url_for('upload_new_data'))


@app.route('/unused_ids')
def unused_ids():
    result = get_unused_ids()
    return render_template("missing_ids.html", missing_ids=result)


if __name__ == '__main__':
    app.run(debug=True)
