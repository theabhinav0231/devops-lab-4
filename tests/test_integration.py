"""Integration tests for Lab 4 CI/CD pipeline gate 2."""
import os
import shutil
import sqlite3
import tempfile
from app.app import app


def test_sqlite_persistence_and_backup_restore(monkeypatch):
    tmpdir = tempfile.mkdtemp(prefix="lab4_int_")
    primary_db = os.path.join(tmpdir, "primary.db")
    backup_db = os.path.join(tmpdir, "backup.db")
    standby_db = os.path.join(tmpdir, "standby.db")
    try:
        monkeypatch.setattr("app.app.DB_PATH", primary_db)
        monkeypatch.setattr("app.app.DEPLOYMENT_SLOT", "primary")
        c = app.test_client()
        for label in ("order-101", "order-102", "order-103"):
            r = c.post("/items", json={"name": label})
            assert r.status_code == 201

        # Online SQLite backup
        src = sqlite3.connect(primary_db)
        dst = sqlite3.connect(backup_db)
        src.backup(dst)
        dst.close()
        src.close()

        # Simulate primary loss and restore to standby
        os.remove(primary_db)
        shutil.copy2(backup_db, standby_db)
        monkeypatch.setattr("app.app.DB_PATH", standby_db)
        monkeypatch.setattr("app.app.DEPLOYMENT_SLOT", "standby")
        r = c.get("/items")
        assert r.status_code == 200
        body = r.get_json()
        assert body["count"] == 3
        assert [it["name"] for it in body["items"]] == ["order-101", "order-102", "order-103"]
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
