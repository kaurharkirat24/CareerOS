from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import inspect, text

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

APPLICATION_COLUMN_MIGRATIONS = {
    "stage": "VARCHAR DEFAULT 'Draft'",
    "status_reason": "TEXT",
    "source_url": "VARCHAR",
    "submitted_at": "DATETIME",
    "last_event_at": "DATETIME",
    "needs_user_review": "BOOLEAN DEFAULT 0",
}

APPLICATION_ARTIFACT_COLUMN_MIGRATIONS = {
    "change_classifications_json": "TEXT DEFAULT '[]'",
    "resume_diff_json": "TEXT DEFAULT '[]'",
    "authenticity_flags_json": "TEXT DEFAULT '[]'",
    "authenticity_requires_review": "BOOLEAN DEFAULT 0",
}

USER_COLUMN_MIGRATIONS = {
    "resume_file_path": "VARCHAR",
    "parsed_profile_json": "TEXT",
}

def _add_missing_columns(table_name: str, columns: dict[str, str]):
    inspector = inspect(engine)
    if table_name not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns(table_name)}
    missing_columns = [
        (column_name, column_definition)
        for column_name, column_definition in columns.items()
        if column_name not in existing_columns
    ]

    if not missing_columns:
        return

    with engine.begin() as connection:
        for column_name, column_definition in missing_columns:
            connection.execute(
                text(f'ALTER TABLE "{table_name}" ADD COLUMN "{column_name}" {column_definition}')
            )

def migrate_sqlite_schema():
    _add_missing_columns("application", APPLICATION_COLUMN_MIGRATIONS)
    _add_missing_columns("applicationartifact", APPLICATION_ARTIFACT_COLUMN_MIGRATIONS)
    _add_missing_columns("user", USER_COLUMN_MIGRATIONS)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    migrate_sqlite_schema()

def get_session():
    with Session(engine) as session:
        yield session
