from quart import Blueprint, render_template
from quart_auth import current_user


index = Blueprint('index_page', __name__)

@index.route('/')
async def index_page():
    return await render_template('index.html', authorized=await current_user.is_authenticated, username=await current_user.username)
