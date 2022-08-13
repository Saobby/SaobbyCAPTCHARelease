import pymysql
pymysql.install_as_MySQLdb()
from sqlalchemy import *
from sqlalchemy.orm import *
from config import *

engine = create_engine("mysql://{}:{}@{}/{}".format(DATABASE_USERNAME, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_NAME),
                       echo=False,
                       connect_args={"ssl": {"ssl_ca": "/etc/ssl/cert.pem"}})
base = declarative_base()


class DbCaptchaInfo(base):
    __tablename__ = "captcha_info"
    id = Column(Integer, primary_key=True)
    cid = Column(VARCHAR(1024))
    data = Column(VARCHAR(1024))

    def __init__(self, cid, data):
        self.cid = cid
        self.data = data


class DbCaptchaToken(base):
    __tablename__ = "captcha_token"
    id = Column(Integer, primary_key=True)
    token = Column(VARCHAR(1024))
    data = Column(VARCHAR(1024))

    def __init__(self, token, data):
        self.token = token
        self.data = data


def get_session():
    db_session = sessionmaker(bind=engine)
    session = db_session()
    return session


def get_captcha_info(cid, session):
    return session.query(DbCaptchaInfo).filter_by(cid=cid).first()


def save_captcha_info(cid, data, session):
    session.add(DbCaptchaInfo(cid, data))
    session.commit()


def get_captcha_token(token, session):
    return session.query(DbCaptchaToken).filter_by(token=token).first()


def save_captcha_token(token, data, session):
    session.add(DbCaptchaToken(token, data))
    session.commit()
    
    
if __name__ == "__main__":
    s = get_session()
    # print(get_captcha_info("test1", s))
    a = s.query(DbCaptchaInfo).all()
    for b in a:
        print(b.cid, b.data)
    print("------------------------------------")
    c = s.query(DbCaptchaToken).all()
    for d in c:
        print(d.token, d.data)
    s.close()
