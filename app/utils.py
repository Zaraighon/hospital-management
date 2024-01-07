from app import app, db
from app.models import User, UserRoleEnum,Patient
import hashlib


def add_user(name, username, password, **kwargs):
    password = hashlib.md5(password.strip().encode('utf-8')).hexdigest()
    user = User(name=name.strip(), username=username.strip(), password=password)

    db.session.add(user)
    db.session.commit()

# bệnh nhân đăng ký khám
def add_appointment(name,gender, date_appointment, date_of_birth, address, disease_history):
    patient_appointment = Patient(name=name.strip(),gender=gender,date_appointment=date_appointment, date_of_birth=date_of_birth,address=address.strip(),disease_history=disease_history.strip())

    db.session.add(patient_appointment)
    db.session.commit()


def check_userlogin(username, password,):
    if username and password:
        password = hashlib.md5(password.strip().encode('utf-8')).hexdigest()

        return User.query.filter(User.username.__eq__(username.strip()),
                                 User.password.__eq__(password),).first()


def check_adminlogin(username, password, role=UserRoleEnum.ADMIN):
    if username and password:
        password = hashlib.md5(password.strip().encode('utf-8')).hexdigest()

        return User.query.filter(User.username.__eq__(username.strip()),
                                 User.password.__eq__(password),
                                 User.user_role.__eq__(role)).first()


# def check_doctorlogin(username, password, role=UserRoleEnum.DOCTOR):
#     if username and password:
#         password = hashlib.md5(password.strip().encode('utf-8')).hexdigest()
#
#         return User.query.filter(User.username.__eq__(username.strip()),
#                                  User.password.__eq__(password),
#                                  User.user_role.__eq__(role)).first()
#
#
# def check_cashierlogin(username, password, role=UserRoleEnum.CASHIER):
#     if username and password:
#         password = hashlib.md5(password.strip().encode('utf-8')).hexdigest()
#
#         return User.query.filter(User.username.__eq__(username.strip()),
#                                  User.password.__eq__(password),
#                                  User.user_role.__eq__(role)).first()


def get_user_by_id(user_id):
    return User.query.get(user_id)