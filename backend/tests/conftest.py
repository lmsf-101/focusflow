import os

os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "test")

os.environ.setdefault("SECRET_KEY", "test")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "5")
