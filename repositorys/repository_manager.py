import asyncio
import contextvars
import hashlib
import sqlite3
from contextlib import asynccontextmanager, closing
from decimal import Decimal

from config import DB_PATH   # 파일이 없으면 새로 만들어요

sqlite3.register_adapter(Decimal, float)   # sqlite는 Decimal 저장 불가

_transaction = contextvars.ContextVar("transaction", default=None)   # 현재 작업의 트랜잭션 연결


def connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)   # 트랜잭션 연결은 여러 스레드에서 이어 씀
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


async def run(work):
    # work(conn)을 스레드에서 실행 → DB를 기다리는 동안 다른 요청 처리 (비동기 I/O)
    conn = _transaction.get()
    if conn is not None:
        return await asyncio.to_thread(work, conn)

    def job():
        with closing(connect()) as conn, conn:   # 끝나면 commit(예외면 rollback) 후 close
            return work(conn)
    return await asyncio.to_thread(job)


@asynccontextmanager
async def transaction():
    # 안에서 실행되는 run()을 한 연결로 묶음 → 전부 저장 또는 전부 취소
    conn = connect()
    token = _transaction.set(conn)
    try:
        yield
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    finally:
        _transaction.reset(token)
        conn.close()


def init_db():
    with closing(connect()) as conn, conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                uid      INTEGER PRIMARY KEY AUTOINCREMENT,
                login_id TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                name     TEXT NOT NULL,
                role     TEXT NOT NULL,      -- desk / vet
                branch   TEXT NOT NULL
            )""")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,   -- 쿠키로 주고받는 값
                uid        INTEGER NOT NULL REFERENCES users(uid),
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
            )""")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS owners (
                oid     INTEGER PRIMARY KEY AUTOINCREMENT,
                oname   TEXT NOT NULL,
                pnum    TEXT NOT NULL,
                address TEXT,
                branch  TEXT NOT NULL     -- 등록한 지점 (다른 지점에서는 안 보임)
            )""")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS pets (
                pid    INTEGER PRIMARY KEY AUTOINCREMENT,
                oid    INTEGER NOT NULL REFERENCES owners(oid),
                pname  TEXT NOT NULL,
                gender TEXT,
                age    INTEGER,
                weight REAL,
                type   TEXT NOT NULL,
                breed  TEXT,
                notes  TEXT
            )""")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS consultations (
                cid       INTEGER PRIMARY KEY AUTOINCREMENT,
                pid       INTEGER NOT NULL REFERENCES pets(pid),
                vet_uid   INTEGER NOT NULL REFERENCES users(uid),
                date      TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
                purpose   TEXT NOT NULL,
                diagnosis TEXT,
                status    TEXT NOT NULL DEFAULT '대기'   -- 대기 / 진료중 / 종료
            )""")

        # 테스트 계정 (비밀번호 모두 1234), 이미 있는 아이디는 건너뜀
        password = hashlib.sha256(b"1234").hexdigest()
        conn.executemany(
            "INSERT OR IGNORE INTO users (login_id, password, name, role, branch) VALUES (?, ?, ?, ?, ?)",
            [
                ("desk1", password, "김간호", "desk", "강남점"),
                ("vet1", password, "이수의", "vet", "강남점"),
                ("vet2", password, "박수의", "vet", "강남점"),
                ("desk2", password, "최간호", "desk", "홍대점"),
                ("vet3", password, "정수의", "vet", "홍대점"),
                ("vet4", password, "한수의", "vet", "홍대점"),
                ("desk3", password, "윤간호", "desk", "서초점"),
                ("vet5", password, "강수의", "vet", "서초점"),
                ("vet6", password, "조수의", "vet", "서초점"),
                ("desk4", password, "임간호", "desk", "잠실점"),
                ("vet7", password, "신수의", "vet", "잠실점"),
                ("vet8", password, "오수의", "vet", "잠실점"),
                ("desk5", password, "서간호", "desk", "분당점"),
                ("vet9", password, "권수의", "vet", "분당점"),
                ("vet10", password, "황수의", "vet", "분당점"),
            ],
        )
