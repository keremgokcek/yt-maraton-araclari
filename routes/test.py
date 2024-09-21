from quart import Blueprint

test = Blueprint('test_page', __name__)
@test.route('/test')
async def test_page():
    return 'Hello, World!'