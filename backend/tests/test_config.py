from app.core.config import Settings


def test_database_url_postgres_scheme_is_normalized():
    settings = Settings(database_url="postgres://u:p@host:5432/db", jwt_secret="x")
    assert settings.database_url == "postgresql://u:p@host:5432/db"


def test_database_url_postgresql_scheme_is_unchanged():
    settings = Settings(database_url="postgresql://u:p@host:5432/db", jwt_secret="x")
    assert settings.database_url == "postgresql://u:p@host:5432/db"


def test_database_url_only_first_occurrence_replaced():
    settings = Settings(
        database_url="postgres://u:p@host:5432/postgres://weird", jwt_secret="x"
    )
    assert settings.database_url == "postgresql://u:p@host:5432/postgres://weird"
