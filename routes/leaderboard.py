from quart import Blueprint, current_app, render_template, websocket
from quart_auth import login_required, current_user
from json import loads

leaderboard = Blueprint('leaderboard', __name__, template_folder='templates')


@leaderboard.route('/view/leaderboard')
async def view():
    users = await current_app.db_conn.execute_fetchall(
        "SELECT username, amount, minutes FROM leaderboard ORDER BY minutes DESC LIMIT 10"
    )
    return await render_template('view/leaderboard.html', users=users)


@leaderboard.websocket('/view/leaderboard')
async def view_socket():
    users = await current_app.db_conn.execute_fetchall(
        "SELECT username, amount, minutes FROM leaderboard ORDER BY minutes DESC LIMIT 10"
    )
    await websocket.send_json(users)

    async for _ in current_app.connections.leaderboard.subscribe():
        users = await current_app.db_conn.execute_fetchall(
            "SELECT username, amount, minutes FROM leaderboard ORDER BY minutes DESC LIMIT 10"
        )
        await websocket.send_json(users)


@leaderboard.route('/manage/leaderboard')
@login_required
async def manage():
    users = await current_app.db_conn.execute_fetchall(
        'SELECT id, username, amount, minutes FROM leaderboard ORDER BY minutes DESC'
    )
    donations = await current_app.db_conn.execute_fetchall(
        'SELECT id, username, amount, minutes, source, message from waiting_donations'
    )

    return await render_template(
        'manage/leaderboard.html',
        username=current_user.username,
        users=users,
        donations=donations,
    )


@leaderboard.websocket('/manage/leaderboard')
@login_required
async def manage_socket():
    await websocket.accept()

    while True:
        data = loads(await websocket.receive())

        if data['type'] == 'ping':
            continue

        if data['type'] == 'update':
            cursor = await current_app.db_conn.execute(
                'SELECT amount, minutes FROM waiting_donations WHERE id = ?',
                (data['source'],),
            )
            donation_amount, donation_minutes = await cursor.fetchone()

            cursor = await current_app.db_conn.execute(
                'SELECT amount, minutes FROM leaderboard WHERE id = ?',
                (data['target'],),
            )
            user_amount, user_minutes = await cursor.fetchone()

            await current_app.db_conn.execute(
                'UPDATE leaderboard SET amount = ?, minutes = ? WHERE id = ?',
                (
                    user_amount + donation_amount,
                    user_minutes + donation_minutes,
                    data['target'],
                ),
            )
        elif data['type'] == 'create':
            cursor = await current_app.db_conn.execute(
                'SELECT username, amount, minutes FROM waiting_donations WHERE id = ?',
                (data['source'],),
            )
            username, amount, minutes = await cursor.fetchone()
            await current_app.db_conn.execute(
                'INSERT INTO leaderboard (username, amount, minutes) VALUES (?, ?, ?)',
                (username, amount, minutes),
            )

        await current_app.db_conn.execute(
            'DELETE FROM waiting_donations WHERE id = ?', (data['source'],)
        )
        await current_app.db_conn.commit()

        users = await current_app.db_conn.execute_fetchall(
            'SELECT username, amount, minutes FROM leaderboard ORDER BY minutes DESC LIMIT 10'
        )
        await current_app.connections.leaderboard.publish(users)
