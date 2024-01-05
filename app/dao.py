from sqlalchemy.dialects import mysql

from app.models import Medicine, Patient
from flask import Flask, render_template, request, redirect, url_for, flash
from app import app,db


def get_medicine():
    return Medicine.query.all()


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


# bệnh nhân đăng ký khám
def patient_add_appointment(name,birth, address, desease_history):
    patient_appointment = Patient(name=name.strip(), birth=birth,address=address.strip(),desease_history=desease_history.strip())

    db.session.add(patient_appointment)
    db.session.commit()
