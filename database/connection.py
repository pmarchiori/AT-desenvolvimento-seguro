import os
from sqlmodel import SQLModel, Session, create_engine, select

database_file = "clinica.db"
sqlite_url = f"sqlite:///{database_file}"

connect_args = {"check_same_thread": False}
engine_url = create_engine(sqlite_url, connect_args=connect_args)

def conn():
    SQLModel.metadata.create_all(engine_url)
    with engine_url.begin() as connection:
        columns = {
            row[1] for row in connection.exec_driver_sql("PRAGMA table_info(patient)")
        }
        if "professional_id" not in columns:
            connection.exec_driver_sql(
                "ALTER TABLE patient ADD COLUMN professional_id INTEGER"
            )

    admin_email = os.getenv("INITIAL_ADMIN_EMAIL")
    admin_password = os.getenv("INITIAL_ADMIN_PASSWORD")
    if admin_email and admin_password:
        from auth.hash_password import HashPassword
        from models.users import User

        with Session(engine_url) as session:
            admin = session.exec(
                select(User).where(User.role == "admin")
            ).first()
            if admin is None:
                session.add(
                    User(
                        name=os.getenv("INITIAL_ADMIN_NAME", "Administrador"),
                        email=admin_email,
                        password=HashPassword().create_hash(admin_password),
                        role="admin",
                    )
                )
                session.commit()

def get_session():
    with Session(engine_url) as session:
        yield session
