from repositorys.repository_manager import run


class OwnerRepository:
    async def insert(self, owner, branch):
        cur = await run(lambda conn: conn.execute(
            "INSERT INTO owners (oname, pnum, address, branch) VALUES (?, ?, ?, ?)",
            (owner.oname, owner.pnum, owner.address, branch),
        ))
        return cur.lastrowid

    async def find(self, oid, branch):
        row = await run(lambda conn: conn.execute("SELECT * FROM owners WHERE oid = ? AND branch = ?", (oid, branch)).fetchone())
        return dict(row) if row else None

    async def find_by_name(self, oname, branch):
        rows = await run(lambda conn: conn.execute("SELECT * FROM owners WHERE oname LIKE ? AND branch = ? ORDER BY oid", (f"%{oname}%", branch)).fetchall())
        return [dict(row) for row in rows]

    async def update(self, oid, fields):
        sets = ", ".join(f"{key} = ?" for key in fields)
        await run(lambda conn: conn.execute(f"UPDATE owners SET {sets} WHERE oid = ?", (*fields.values(), oid)))
