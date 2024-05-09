"""
    Routes
    ~~~~~~
"""
import sqlite3
from datetime import datetime, timezone

import io
import os
from werkzeug.utils import secure_filename

from flask import current_app, send_file, jsonify
from flask import Blueprint
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_login import current_user
from flask_login import login_required
from flask_login import login_user
from flask_login import logout_user

from wiki.core import Processor
from wiki.web.forms import EditorForm, RegisterForm, EditProfileForm
from wiki.web.forms import LoginForm
from wiki.web.forms import SearchForm
from wiki.web.forms import URLForm
from wiki.web import current_wiki
from wiki.web import current_users
from wiki.web.user import protect


bp = Blueprint('wiki', __name__)


@bp.route('/')
@protect
def home():
    page = current_wiki.get('home')
    if page:
        return display('home')
    return render_template('home.html')


@bp.route('/index/')
@protect
def index():
    pages = current_wiki.index()
    return render_template('index.html', pages=pages)


@bp.route('/<path:url>/')
@protect
def display(url):
    page = current_wiki.get_or_404(url)
    return render_template('page.html', page=page)


@bp.route('/create/', methods=['GET', 'POST'])
@protect
def create():
    form = URLForm()
    if form.validate_on_submit():
        return redirect(url_for(
            'wiki.edit', url=form.clean_url(form.url.data)))
    return render_template('create.html', form=form)


@bp.route('/edit/<path:url>/', methods=['GET', 'POST'])
@protect
def edit(url):
    page = current_wiki.get(url)
    form = EditorForm(obj=page)
    if form.validate_on_submit():
        if not page:
            page = current_wiki.get_bare(url)
        form.populate_obj(page)
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(current_app.config['UPLOAD_DIR'], filename))
        page.save()
        flash('"%s" was saved.' % page.title, 'success')
        return redirect(url_for('wiki.display', url=url))
    return render_template('editor.html', form=form, page=page)


@bp.route('/preview/', methods=['POST'])
@protect
def preview():
    data = {}
    processor = Processor(request.form['body'])
    data['html'], data['body'], data['meta'] = processor.process()
    return data['html']


@bp.route('/move/<path:url>/', methods=['GET', 'POST'])
@protect
def move(url):
    page = current_wiki.get_or_404(url)
    form = URLForm(obj=page)
    if form.validate_on_submit():
        newurl = form.url.data
        current_wiki.move(url, newurl)
        return redirect(url_for('wiki.display', url=newurl))
    return render_template('move.html', form=form, page=page)


@bp.route('/delete/<path:url>/')
@protect
def delete(url):
    page = current_wiki.get_or_404(url)
    current_wiki.delete(url)
    flash('Page "%s" was deleted.' % page.title, 'success')
    return redirect(url_for('wiki.home'))


@bp.route('/tags/')
@protect
def tags():
    tags = current_wiki.get_tags()
    return render_template('tags.html', tags=tags)


@bp.route('/tag/<string:name>/')
@protect
def tag(name):
    tagged = current_wiki.index_by_tag(name)
    return render_template('tag.html', pages=tagged, tag=name)


@bp.route('/search/', methods=['GET', 'POST'])
@protect
def search():
    form = SearchForm()
    if form.validate_on_submit():
        if form.search_option.data == 'tags':
            if ',' in form.term.data:
                tags = form.term.data.split(',')
            else:
                tags = [form.term.data]
            results = current_wiki.search_by_tags(tags, form.ignore_case.data)
        elif form.search_option.data == 'title':
            if ',' in form.term.data:
                titles = form.term.data.split(',')
            else:
                titles = [form.term.data]
            results = current_wiki.search_by_title(titles, form.ignore_case.data)
        elif form.search_option.data == 'body':
            results = current_wiki.search_by_body(form.term.data, form.ignore_case.data)
        else:
            results = current_wiki.search(form.term.data, form.ignore_case.data)
        return render_template('search.html', form=form, results=results, search=form.term.data)
    return render_template('search.html', form=form, search=None)


@bp.route('/user/login/', methods=['GET', 'POST'])
def user_login():
    form = LoginForm()
    if form.validate_on_submit():
        user = current_users.get_user(form.username.data)
        form.validate_username(user)
        form.validate_password(form.password.data)
        if user.is_active():
            login_user(user)
            user.set('authenticated', True)
            flash('Login successful.', 'success')
            return redirect(url_for('wiki.home'))
        else:
            flash('Login Failed: Invalid Username or Password.', 'danger')
            return render_template('login.html', form=form)
    return render_template('login.html', form=form)


@bp.route('/user/register/', methods=['GET', 'POST'])
def user_register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = current_users.get_user(form.username.data)
        flash('Account created.', 'success')
        return redirect(url_for('wiki.user_login'))

    return render_template('register.html', form=form)


@bp.route('/user/logout/')
@login_required
def user_logout():
    current_user.set('authenticated', False)
    logout_user()
    flash('Logout successful.', 'success')
    return redirect(url_for('wiki.index'))


@bp.route('/user/<username>')
@login_required
def user_profile(username):
    user = current_users.get_user(username)
    return render_template('user.html', user=user)


@bp.route('/user/edit_profile/', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.set('fname', form.fname.data)
        current_user.set('lname', form.lname.data)
        current_user.set('email', form.email.data)
        current_user.set('phone', form.phone.data)
        if form.username.data != "":
            form.validate_username(current_user)
            current_user.set('active', False)
            old_username = current_user.username
            current_user.username = form.username.data
            current_user.set('active', True)
            current_users.delete_user(old_username)
        if form.password.data != "":
            current_user.set('password', form.password.data)

        flash("Your profile has been updated.", "success")
        return redirect(url_for('wiki.user_profile', username=current_user.username))
    elif request.method == 'GET':
        form.fname.data = current_user.get('fname')
        form.lname.data = current_user.get('lname')
        form.email.data = current_user.get('email')
        form.phone.data = current_user.get('phone')
    return render_template('edit_profile.html', form=form)


@bp.route('/user/create/')
def user_create():
    pass


@bp.route('/user/<int:user_id>/')
def user_admin(user_id):
    pass


@bp.route('/user/delete/<int:user_id>/')
def user_delete(user_id):
    pass


"""
    Error Handlers
    ~~~~~~~~~~~~~~
"""


@bp.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404






"""

    Analytics


"""


@bp.route('/track_page_view', methods=['POST'])
def track_page_view():
    database = sqlite3.connect('database.db')
    cursor = database.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS page_views
                (id INTEGER PRIMARY KEY, page TEXT, views INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS timestamps
                (id INTEGER PRIMARY KEY, page_view_id INTEGER,
                timestamp TEXT, FOREIGN KEY(page_view_id) REFERENCES page_views(id))''')

    data = request.json
    page = data.get('page')

    cursor.execute('SELECT * FROM page_views WHERE page=?', (page,))
    result = cursor.fetchone()

    if result:
        views = result[2] + 1
        cursor.execute('UPDATE page_views SET views=? WHERE page=?', (views, page))
        page_view_id = result[0]
    else:
        cursor.execute('INSERT INTO page_views (page, views) VALUES (?, 1)', (page,))
        page_view_id = cursor.lastrowid

    timestamp = datetime.now().strftime('%Y-%m-%d')
    cursor.execute('INSERT INTO timestamps (page_view_id, timestamp) VALUES (?, ?)', (page_view_id, timestamp))

    database.commit()

    return 'Page view tracked successfully'


@bp.route('/get_view_count', methods=['POST'])
def get_view_count():
    database = sqlite3.connect('database.db')
    cursor = database.cursor()

    data = request.json
    page = data.get('page')

    cursor.execute('SELECT views FROM page_views WHERE page=?', (page,))
    result = cursor.fetchone()

    if result:
        view_count = result[0]
        return jsonify({'view_count': view_count})
    else:
        return jsonify({'error': 'Page not found'}), 404


@bp.route('/get_timestamps', methods=['POST'])
def get_timestamps():
    database = sqlite3.connect('database.db')
    cursor = database.cursor()

    data = request.json
    page = data.get('page')

    cursor.execute(
        'SELECT timestamp, COUNT(*) FROM timestamps JOIN page_views ON timestamps.page_view_id = page_views.id WHERE page_views.page = ? GROUP BY strftime("%Y-%m-%d", timestamp)',
        (page,))

    data = []
    for row in cursor.fetchall():
        data.append({
            'day': row[0],
            'count': row[1]
        })

    return jsonify(data)


@bp.route('/gallery')
def gallery():
    images = os.listdir(current_app.config['UPLOAD_DIR'])
    images = ['upload/' + file for file in images]
    return render_template('gallery.html', images=images)


@bp.route('/download/<path:url>/')
@protect
def download(url):
    page = current_wiki.get_or_404(url)
    title = page.title
    text_content = f"{title}\n\n{page.body}"
    filename = secure_filename(f"{url.replace('/', '_')}")
    file_obj = io.BytesIO()
    file_obj.write(text_content.encode())
    file_obj.seek(0)
    return send_file(file_obj, as_attachment=True, mimetype='text/plain', download_name=f"{filename}.txt")


