from repositorys.repository_manager import run

# 진료 + 담당 의사 이름 + 동물 정보 (owners는 지점 확인용)
SELECT = """
    SELECT c.*, u.name AS vet_name, p.pname, p.gender, p.age, p.weight, p.type, p.breed, p.notes
    FROM consultations c
    JOIN users u ON u.uid = c.vet_uid
    JOIN pets p ON p.pid = c.pid
    JOIN owners o ON o.oid = p.oid
"""


class ConsultationRepository:
    async def insert(self, pid, vet_uid, purpose):
        cur = await run(lambda conn: conn.execute(
            "INSERT INTO consultations (pid, vet_uid, purpose) VALUES (?, ?, ?)",
            (pid, vet_uid, purpose),
        ))
        return cur.lastrowid

    async def find(self, cid):
        row = await run(lambda conn: conn.execute(SELECT + " WHERE c.cid = ?", (cid,)).fetchone())
        return dict(row) if row else None

    async def find_by_pet(self, pid, branch):
        rows = await run(lambda conn: conn.execute(SELECT + " WHERE c.pid = ? AND o.branch = ? ORDER BY c.cid DESC", (pid, branch)).fetchall())
        return [dict(row) for row in rows]

    async def find_assigned(self, vet_uid):
        rows = await run(lambda conn: conn.execute(SELECT + " WHERE c.vet_uid = ? AND c.status IN ('대기', '진료중') ORDER BY c.cid", (vet_uid,)).fetchall())
        return [dict(row) for row in rows]

    async def update_status(self, cid, vet_uid, before, after):
        cur = await run(lambda conn: conn.execute(
            "UPDATE consultations SET status = ? WHERE cid = ? AND vet_uid = ? AND status = ?",
            (after, cid, vet_uid, before),
        ))
        return cur.rowcount

    async def update_diagnosis(self, cid, vet_uid, diagnosis):
        cur = await run(lambda conn: conn.execute(
            "UPDATE consultations SET diagnosis = ? WHERE cid = ? AND vet_uid = ? AND status = '진료중'",
            (diagnosis, cid, vet_uid),
        ))
        return cur.rowcount
