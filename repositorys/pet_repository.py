from repositorys.repository_manager import run


class PetRepository:
    async def insert(self, oid, pet):
        cur = await run(lambda conn: conn.execute(
            "INSERT INTO pets (oid, pname, gender, age, weight, type, breed, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (oid, pet.pname, pet.gender, pet.age, pet.weight, pet.type, pet.breed, pet.notes),
        ))
        return cur.lastrowid

    async def find(self, pid, branch):
        row = await run(lambda conn: conn.execute(
            "SELECT p.* FROM pets p JOIN owners o ON o.oid = p.oid WHERE p.pid = ? AND o.branch = ?", (pid, branch)
        ).fetchone())
        return dict(row) if row else None

    async def find_by_owner(self, oid):
        rows = await run(lambda conn: conn.execute("SELECT * FROM pets WHERE oid = ? ORDER BY pid", (oid,)).fetchall())
        return [dict(row) for row in rows]

    async def update(self, pid, fields):
        sets = ", ".join(f"{key} = ?" for key in fields)
        await run(lambda conn: conn.execute(f"UPDATE pets SET {sets} WHERE pid = ?", (*fields.values(), pid)))
