"""
    Autore: Cavallo Luigi
    Descrizione : File di configurazione principale
"""
import os

class ServerConfiguration:
    ENV                 = "production"
    SECRET_KEY          = "secret"
    MYSQL_DATABASE_HOST = "localhost"
    MYSQL_DATABASE_USER = "guest"
    MYSQL_DATABASE_PASS = "guest"
    MYSQL_DATABASE_DB   = "foo"
    BASIC_AUTH_USERNAME = "Mike"
    BASIC_AUTH_PASSWORD = "VeryInvulnerablePasswordThatYouCanUndiscover202020!$?_"
    LOGS_DIR            = r"logs"
    LOGS = [
        os.path.join(LOGS_DIR, "operational.log"),
        os.path.join(LOGS_DIR, "queries.log"),
        os.path.join(LOGS_DIR, "access.log")
    ]


status = dict(
    mode=ServerConfiguration
)
