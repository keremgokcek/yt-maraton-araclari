from user import User
from app import CustomApp
from quart_auth import QuartAuth

app = CustomApp(__name__)
app.secret_key = 'RX9PObOFHUf3zMZpq41TBA'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
auth_manager = QuartAuth(cookie_secure=False)
auth_manager.user_class = User

app.register_blueprint_folder('routes')

auth_manager.init_app(app)

@app.after_request
def add_header(response):
    response.cache_control.no_cache = True
    response.cache_control.no_store = True
    response.cache_control.max_age = 0
    response.cache_control.must_revalidate = True
    return response

if __name__ == '__main__':
    try:
        app.run(port=8080, debug=True, host='0.0.0.0')
    except BaseException:
        pass
