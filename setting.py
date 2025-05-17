from dotenv import load_dotenv
from pathlib import Path
import os
import platform

class EnvVariables:
    def __init__(self):

        dotenv_path = None
        os_name = platform.system()

        if (os_name=="Windows"):
            dotenv_path = Path('cred\.env')
        else:
            dotenv_path = Path('cred/.env')

        load_dotenv(dotenv_path=dotenv_path)

        self.MONGODB_HOST=os.getenv("MONGODB_HOST")
        self.MONGODB_PORT=os.getenv("MONGODB_PORT")
        self.MONGODB_USERNAME=os.getenv("MONGODB_USERNAME")
        self.MONGODB_PASSWORD= os.getenv("MONGODB_PASSWORD")
        self.IS_SOURCE_MONGODB_ATLAS= os.getenv("IS_SOURCE_MONGODB_ATLAS")
        self.SOURCE_MONGODB_URL= os.getenv("SOURCE_MONGODB_URL")
        
        self.DATA_RETENTION_DAYS= int(os.getenv("DATA_RETENTION_DAYS"))
        self.BATCH_SIZE= int(os.getenv("BATCH_SIZE"))
        self.IS_ARCHIVE_ENABLED= os.getenv("IS_ARCHIVE_ENABLED")

        self.ARCHIVE_MONGODB_HOST=os.getenv("ARCHIVE_MONGODB_HOST")
        self.ARCHIVE_MONGODB_PORT=os.getenv("ARCHIVE_MONGODB_PORT")
        self.ARCHIVE_MONGODB_USERNAME=os.getenv("ARCHIVE_MONGODB_USERNAME")
        self.ARCHIVE_MONGODB_PASSWORD= os.getenv("ARCHIVE_MONGODB_PASSWORD")
        self.IS_ARCHIVE_MONGODB_ATLAS= os.getenv("IS_ARCHIVE_MONGODB_ATLAS")
        self.ARCHIVE_MONGODB_URL= os.getenv("ARCHIVE_MONGODB_URL")
        
        # FOR ETL
        self.ETL_PG_HOST = os.getenv("ETL_PG_HOST")
        self.ETL_PG_PORT = os.getenv("ETL_PG_PORT")
        self.ETL_PG_DATABASE = os.getenv("ETL_PG_DATABASE")
        self.ETL_PG_USER = os.getenv("ETL_PG_USER")
        self.ETL_PG_PASSWORD = os.getenv("ETL_PG_PASSWORD")
        self.ETL_PG_SCHEMA = os.getenv("ETL_PG_SCHEMA")

        if (os_name=="Windows"):
            self.INDEXES_XML_FILE_PATH= os.getenv("INDEXES_XML_FILE_PATH").replace("/", "\\")
            self.LOG_DIRECTORY = os.getenv("LOG_DIRECTORY").replace("/", "\\")
            self.LOG_FILE = os.getenv("LOG_FILE").replace("/", "\\")
            self.PID_FILE = os.getenv("PID_FILE").replace("/", "\\")
            self.AUTOMATION_DB = os.getenv("AUTOMATION_DB").replace("/", "\\")
        else:
            self.INDEXES_XML_FILE_PATH = os.getenv("INDEXES_XML_FILE_PATH").replace("\\", "/")
            self.LOG_DIRECTORY = os.getenv("LOG_DIRECTORY").replace("\\", "/")
            self.LOG_FILE = os.getenv("LOG_FILE").replace("\\", "/")
            self.PID_FILE = os.getenv("PID_FILE").replace("\\", "/")
            self.AUTOMATION_DB = os.getenv("AUTOMATION_DB").replace("\\", "/")
        
        # Notification
        self.SMTP_LOGIN_USERNAME = os.getenv("SMTP_LOGIN_USERNAME")
        self.SMTP_LOGIN_PASSWORD = os.getenv("SMTP_LOGIN_PASSWORD")

        self.SMTP_SERVER = os.getenv("SMTP_SERVER")
        self.SMTP_PORT = os.getenv("SMTP_PORT")
        self.SENDER_EMAIL = os.getenv("SENDER_EMAIL")
        # self.SENDER_EMAIL_PASSWORD = os.getenv("SENDER_EMAIL_PASSWORD")
        self.RECEEIVER_EMAIL = os.getenv("RECEEIVER_EMAIL")
        self.NOTIFICATION_INTERVAL_HOUR = os.getenv("NOTIFICATION_INTERVAL_HOUR")
        self.TLS_ENABLED = os.getenv("TLS_ENABLED")
        self.EMAIL_PASS_AUTH_ENABLED = os.getenv("EMAIL_PASS_AUTH_ENABLED")
        self.EMAIL_SUBJECT = os.getenv("EMAIL_SUBJECT")
        if (os_name=="Windows"):
            self.EMAIL_TEMPLATE = os.getenv("EMAIL_TEMPLATE").replace("/", "\\")
            self.NOTIFICATION_LOG = os.getenv("NOTIFICATION_LOG").replace("/", "\\")
        else:
            self.EMAIL_TEMPLATE = os.getenv("EMAIL_TEMPLATE").replace("\\", "/")
            self.NOTIFICATION_LOG = os.getenv("NOTIFICATION_LOG").replace("\\", "/")
        
def get_variables():
    try:
        env_variable = EnvVariables()

        return env_variable
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    VARIABLES = EnvVariables()
    print(f"MONGODB_HOST = {VARIABLES.MONGODB_HOST}")
   