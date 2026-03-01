from __future__ import annotations
from app.db.base import Base
from app.db.session import engine
from app import models  # noqa: F401


def run() -> None:
    with engine.begin() as conn:
        Base.metadata.create_all(bind=conn)
        if engine.url.get_backend_name().startswith("sqlite"):
            conn.exec_driver_sql("PRAGMA foreign_keys=OFF")
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        if engine.url.get_backend_name().startswith("sqlite"):
            conn.exec_driver_sql("PRAGMA foreign_keys=ON")
    print("Database cleared.")


if __name__ == "__main__":
    run()
