from repositorys.repository_manager import run


class SessionRepository:
    async def insert(self, session_id, uid):
        await run(lambda conn: conn.execute("INSERT INTO sessions (session_id, uid) VALUES (?, ?)", (session_id, uid)))

    async def find_user(self, session_id):
        row = await run(lambda conn: conn.execute(
            "SELECT u.* FROM sessions s JOIN users u ON u.uid = s.uid WHERE s.session_id = ?", (session_id,)
        ).fetchone())
        return dict(row) if row else None

    async def delete(self, session_id):
        await run(lambda conn: conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,)))
