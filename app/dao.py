from sqlalchemy.dialects import mysql

from app.models import Medicine, Patient, MedicalReport, Prescription
from flask import Flask, render_template, request, redirect, url_for, flash
from app import app,db


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


