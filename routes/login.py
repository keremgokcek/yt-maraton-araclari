from user import User
from tools import get_user_data
from quart_auth import login_user, current_user
from quart import Blueprint, request, redirect, render_template

login = Blueprint('login_page', __name__, template_folder='templates')

@login.route('/login', methods=['GET', 'POST'])
async def login_page():
    if request.method == 'POST':
        username = (await request.form).get('username')
        password = (await request.form).get('password')
        
        if id := await get_user_data(username, password):
            login_user(User(id))
            return redirect('/panel')
        
        return await render_template('login.html', error='Geçersiz kullanıcı adı veya şifre.')
    else:
        if await current_user.is_authenticated:
            return redirect('/panel')
        
        return await render_template('login.html')
