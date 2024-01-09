from sqlalchemy.dialects import mysql
from sqlalchemy import create_engine, Column, Integer, String, Date, distinct
from app.models import Medicine, Patient, MedicalReport, Prescription
from flask import Flask, render_template, request, redirect, url_for, flash, session
from app import app, db
import math
import logging
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func


def get_medicine():
    return Medicine.query.all()


# lấy thông tin pk
def get_phieukham():
    return MedicalReport.query.all()

# lấy bệnh nhân
def get_patient():
    return Patient.query.all()


# lấy Đơn thuốc
def get_prescription():
    return Prescription.query.all()


def insert_medicine():
    if request.method == "POST":
        flash("Data Inserted Successfully")
        medicine_name = request.form['medicine_name']
        how_to_use = request.form['how_to_use']
        # soluong = request.form['soluong']
        unit_name = request.form['unit_name']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO medicine (medicine_name, how_to_use, unit_name) VALUES (%s, %s, %s, %s)",
                    (medicine_name, how_to_use, unit_name))
        mysql.connection.commit()


def date_chart():
    return db.session.query(distinct(Medicine.created_date)).order_by(Medicine.created_date).all()

def count_patients_by_date():
    # Sử dụng hàm func.count() để đếm số thuốc
    # Sử dụng hàm func.date() để lấy phần ngày từ createed_date
    # Sử dụng hàm group_by() để nhóm theo ngày
    # Sử dụng hàm order_by() để sắp xếp theo ngày
    result = (db.session.query(func.date(Medicine.created_date), func.count(Medicine.id)).group_by(func.date(Medicine.created_date))
              .order_by(func.date(Medicine.created_date)).all())
    return result