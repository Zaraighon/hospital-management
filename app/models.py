from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from app import db, app
from datetime import datetime
from flask_login import UserMixin
import enum


class UserRoleEnum(enum.Enum):
    PATIENT = 1
    ADMIN = 2
    NURSE = 3
    DOCTOR = 4
    CASHIER = 5


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    user_role = Column(Enum(UserRoleEnum), default=UserRoleEnum.PATIENT)

    def __str__(self):
        return self.name


class GenderEnum(Enum):
    MALE = 'Male'
    FEMALE = 'Female'


class Patient(db.Model):
    __tablename__ = 'patient'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=True)
    # gender = Column(Enum(GenderEnum), default=GenderEnum.MALE)
    date_of_birth = Column(DateTime, nullable=True)
    address = Column(String(100), nullable=True)
    disease_history = Column(String(100), nullable=True)
    # date_id = Column(Integer, ForeignKey('dateappointment.id'))
    # date_appointment = relationship('DateAppointment', back_populates='patients')

    def __str__(self):
        return self.name


# class DateAppointment(db.Model):
#     __tablename__ = 'dateappointment'
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     date = Column(DateTime, nullable=True)
#     patients = relationship('Patient', back_populates='date_appointment')


class MedicineUnit(db.Model):
    __tablename__ = 'medicineunit'
    id = Column(Integer, primary_key=True, autoincrement=True)
    unit_name = Column(String(50), nullable=False, unique=True)

    def __str__(self):
        return self.tendonvi


class Medicine(db.Model):
    __tablename__ = 'medicine'

    id = Column(Integer, primary_key=True, autoincrement=True)
    medicine_name = Column(String(50), nullable=False, unique=True)
    how_to_use = Column(String(255), nullable=False, unique=True)
    price = Column(Float, default=0)
    unit_name = Column(String(50), ForeignKey(MedicineUnit.unit_name), nullable=False)
    unit = relationship(MedicineUnit, backref='medicines')

    def __str__(self):
        return self.medicine_name


class PhieuKham(db.Model):
    __tablename__ = 'phieukham'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ngaykham = Column(DateTime, default=datetime.now())
    trieuchung = Column(String(255), nullable=False, unique=True)
    loaibenh = Column(String(50), nullable=False, unique=True)

    phieukham_thuoc = db.Table('phieukham_thuoc',
                               Column('phieukham_id', Integer, ForeignKey('phieukham.id'), primary_key=True),
                               Column('thuoc_id', Integer, ForeignKey(Medicine.id), primary_key=True),
                               Column('soluong', Integer, nullable=False))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        import hashlib

        u = User(name='Admin', username='admin',
                 password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()), user_role=UserRoleEnum.ADMIN)
        p = User(name='Patient1', username='patient1',
                 password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()), user_role=UserRoleEnum.PATIENT)
        n = User(name='Nurse1', username='nurse1',
                 password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()), user_role=UserRoleEnum.NURSE)
        d = User(name='doctor1', username='doctor1',
                 password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()), user_role=UserRoleEnum.DOCTOR)
        c = User(name='cashier1', username='cashier1',
                 password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()), user_role=UserRoleEnum.CASHIER)
        db.session.add_all([u, p, n, d, c])
        db.session.commit()