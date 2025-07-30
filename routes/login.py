from user import User
from quart_auth import login_user, current_user
from quart import Blueprint, request, redirect, render_template
from json import load

login = Blueprint('login_page', __name__, template_folder='templates')


@login.route('/login', methods=['GET', 'POST'])
async def login_page():
    if request.method == 'POST':
        username = (await request.form).get('username')
        password = (await request.form).get('password')

        with open('logins.json') as f:
            logins = load(f)

        pair = logins.get(username)
        if pair and pair['password'] == password:
            login_user(User(pair['id']))
            return redirect('/manage/countdown')

        return await render_template(
            'login.html', error='Geçersiz kullanıcı adı veya şifre.'
        )
    else:
        if await current_user.is_authenticated:
            return redirect('/manage/countdown')

        return await render_template('login.html')
