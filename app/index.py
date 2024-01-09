from flask import Flask, render_template, request, redirect, url_for, flash
from app.models import Medicine, UserRoleEnum, Patient, MedicalReport, Prescription,Rule
from flask import Flask, render_template, request, redirect, url_for, flash, json
from app.models import Medicine, UserRoleEnum, Patient, MedicalReport, Prescription
import dao
from app import app, db, utils, login, form
from flask_login import login_user, logout_user, login_required, current_user
import datetime
from sqlalchemy import func, extract


@app.route('/')
def index():
    return render_template('index.html', UserRoleEnum=UserRoleEnum)

# Tạo route để hiển thị biểu đồ doanh thu
@app.route('/admin/tkdt')
def revenue_chart(year=2024, month=3):
    # Tạo câu truy vấn để lấy doanh thu theo ngày trong tháng
    query = db.session.query(extract('day', Prescription.created_date),
                             func.sum(Medicine.price * Prescription.count))\
              .join(Medicine, Medicine.id == Prescription.medicine_id)\
              .filter(extract('year', Prescription.created_date) == year)\
              .filter(extract('month', Prescription.created_date) == month)\
              .group_by(extract('day', Prescription.created_date))

    # Lấy kết quả truy vấn và chuyển thành danh sách
    results = query.all()
    days = [r[0] for r in results]
    revenues = [r[1] for r in results]

    # Truyền dữ liệu vào template để vẽ biểu đồ
    return render_template('admin/tkdt.html', days=days, revenues=revenues, year=year, month=month, UserRoleEnum=UserRoleEnum)


@app.route('/admin/tkbc')
def tkbc(year=2024, month=3):
    # Tạo câu truy vấn để lấy số thuốc đã sử dụng theo ngày trong tháng
    query = db.session.query(extract('day', Prescription.created_date),
                             func.sum(Prescription.count)) \
        .join(Medicine, Medicine.id == Prescription.medicine_id) \
        .filter(extract('year', Prescription.created_date) == year) \
        .filter(extract('month', Prescription.created_date) == month) \
        .group_by(extract('day', Prescription.created_date))

    # Lấy kết quả truy vấn và chuyển thành danh sách
    results = query.all()
    days = [r[0] for r in results]
    counts = list(map(int, [r[1] for r in results]))

    # Truyền dữ liệu vào template để vẽ biểu đồ
    return render_template('admin/tkbc.html', days=days, counts=counts, year=year, month=month, UserRoleEnum=UserRoleEnum)

@app.route('/admin')
def admin():
    return render_template('admin/index.html', UserRoleEnum=UserRoleEnum)


@app.route('/admin-login', methods=['post'])
def signin_admin():
    err_msg = ""
    try:
        username = request.form.get('username')
        password = request.form.get('password')

        user = utils.check_adminlogin(username=username,
                                      password=password, )
        if user:
            login_user(user=user)
            return redirect(url_for('admin'))
        else:
            err_msg = 'Tài khoản hoặc mật khẩu không chính xác'
    except Exception as ex:
        err_msg = str(ex)
    return render_template('admin/index.html', err_msg=err_msg)


@app.route('/admin-logout')
def admin_signout():
    logout_user()
    return redirect(url_for('admin'))


@app.route('/register', methods=['get', 'post'])
def user_register():
    err_msg = ""
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')

        try:
            if password.strip().__eq__(confirm.strip()):
                utils.add_user(name=name, username=username, password=password)
                return redirect(url_for('user_signin'))
            else:
                err_msg = 'Xác nhận mật khẩu không chính xác'
        except Exception as ex:
            err_msg = "Lỗi: " + str(ex)

    return render_template('register.html', err_msg=err_msg)


# LẤY DANH SÁCH KHÁM THEO NGÀY
@app.route('/appointment-list', methods=['get'])
def nurse_appointment_list():
    # CHECK ROLE Y TÁ
    if current_user.user_role == UserRoleEnum.NURSE:

        if request.method.__eq__('GET'):
            selected_date = request.args.get('selected_date')
            patients = Patient.query.filter_by(date_appointment=selected_date).all()
        return render_template('nurse/appointmentList.html',selected_date = selected_date,patients=patients, UserRoleEnum=UserRoleEnum)
    else:
        return redirect(url_for('index'))

@app.route('/receipt-list', methods=['get'])
def cashier_receipt_list():
    if current_user.user_role == UserRoleEnum.CASHIER:
        if request.method.__eq__('GET'):
            selected_date = request.args.get('selected_date')
            patients = Patient.query.filter_by(date_appointment=selected_date).all()
            medical_reports = MedicalReport.query.filter_by(date_examination=selected_date)
        return render_template('cashier/receipt.html', UserRoleEnum=UserRoleEnum, selected_date=selected_date,patients=patients, medical_reports=medical_reports)
    else:
        return redirect(url_for('index'))

@app.route('/receipt-list/export/<int:id>', methods=['get','post'])
def export_receipt(id):
    if current_user.user_role == UserRoleEnum.CASHIER:
        patient = Patient.query.get_or_404(id)
        medical_report = MedicalReport.query.filter_by(id=patient.id).first()
        prescriptions = Prescription.query.filter_by(medical_report_id=medical_report.id).all()
        medicines=[]
        for prescription in prescriptions:
            medicine = Medicine.query.filter_by(id=prescription.medicine_id).first()
            if medicine:
                medicines.append(medicine)
        return render_template('cashier/export-receipt.html', patient=patient, medical_report=medical_report, prescriptions=prescriptions, medicines=medicines, UserRoleEnum=UserRoleEnum)


@app.route('/appointment-list/edit/<int:id>', methods=['get', 'post'])
def nurse_edit_appointment(id):
    if current_user.user_role == UserRoleEnum.NURSE:
        patient = Patient.query.get_or_404(id)
        before_edit_date = patient.date_appointment
        if request.method.__eq__('POST'):
            patient.name = request.form.get('name')
            patient.gender = request.form.get('gender')
            patient.date_appointment = request.form.get('date_appointment')
            patient.date_of_birth = request.form.get('date_of_birth')
            patient.address = request.form.get('address')
            patient.disease_history = request.form.get('disease_history')
            patient.tel = request.form.get('tel')
            db.session.commit()
            return redirect(url_for('nurse_appointment_list',UserRoleEnum=UserRoleEnum, selected_date = before_edit_date))
        return render_template('nurse/update_appointment.html', patient=patient,UserRoleEnum=UserRoleEnum)

@app.route('/appointment-list/delete/<int:id>')
def nurse_delete_appointment(id):
    patient = Patient.query.get_or_404(id)
    deleted_date = patient.date_appointment
    try:
        db.session.delete(patient)
        db.session.commit()
        return redirect(url_for('nurse_appointment_list',UserRoleEnum=UserRoleEnum, selected_date = deleted_date))
    except:
        return 'Có lỗi xảy ra khi xóa'

# Y TÁ GHI DANH BỆNH NHÂN
@app.route('/add_appointment', methods=['get', 'post'])
def nurse_add_appointment():
    # CHECK ROLE Y TÁ
    err_msg = ""
    sc_msg = ""
    if current_user.user_role == UserRoleEnum.NURSE:
        if request.method.__eq__('POST'):
            name = request.form.get('name')
            gender = request.form['gender']
            date_appointment = request.form.get('date_appointment')
            date_of_birth = request.form.get('date_of_birth')
            address = request.form.get('address')
            disease_history = request.form.get('disease_history')
            tel = request.form.get('tel')

            try:
                count = Patient.query.filter_by(date_appointment=date_appointment).count()
                if count == 10 or count > 10:
                    err_msg = 'Ngày đăng ký khám đã hết chỗ'
                    return render_template('nurse/add_appointment.html', err_msg=err_msg, UserRoleEnum=UserRoleEnum)
                utils.add_appointment(name=name, gender=gender, date_appointment=date_appointment,
                                      date_of_birth=date_of_birth, address=address, disease_history=disease_history, tel=tel)
            except Exception as ex:
                err_msg = 'Thêm bệnh nhân không thành công' + str(ex)
            else:
                sc_msg = 'Thêm bệnh nhân thành công'
                return render_template('nurse/add_appointment.html', sc_msg=sc_msg, UserRoleEnum=UserRoleEnum)
        return render_template('nurse/add_appointment.html', err_msg=err_msg, UserRoleEnum=UserRoleEnum)
    else:
        return redirect(url_for('index'))

# BỆNH NHÂN ĐĂNG KÝ KHÁM
@app.route('/appointment', methods=['get', 'post'])
def user_appointment():
    # check role bệnh nhân
    err_msg = ""
    sc_msg = ""
    patient_per_date = Rule.query.filter_by(rule_name='Patient per day').first()
    if current_user.user_role == UserRoleEnum.PATIENT:
        if request.method.__eq__('POST'):
            name = request.form.get('name')
            gender = request.form['gender']
            date_appointment = request.form.get('date_appointment')
            date_of_birth = request.form.get('date_of_birth')
            address = request.form.get('address')
            disease_history = request.form.get('disease_history')
            tel = request.form.get('tel')

            try:
                count = Patient.query.filter_by(date_appointment=date_appointment).count()
                if count == patient_per_date or count > patient_per_date:
                    err_msg = 'Ngày đăng ký khám đã hết chỗ'
                    return render_template('patient/update_appointment.html', err_msg=err_msg, UserRoleEnum=UserRoleEnum)
                utils.add_appointment(name=name, gender=gender, date_appointment=date_appointment,
                                      date_of_birth=date_of_birth, address=address, disease_history=disease_history, tel=tel)
            except Exception as ex:
                err_msg = 'Đăng ký khám không thành công' + str(ex)
            else:
                sc_msg = 'Đăng ký khám thành công'
                return render_template('patient/update_appointment.html', sc_msg=sc_msg, UserRoleEnum=UserRoleEnum)
        return render_template('patient/update_appointment.html', err_msg=err_msg, UserRoleEnum=UserRoleEnum)
    else:
        return redirect(url_for('index'))



@app.route('/user-login', methods=['get', 'post'])
def user_signin():
    err_msg = ''
    if request.method.__eq__('POST'):
        try:
            username = request.form.get('username')
            password = request.form.get('password')

            user = utils.check_userlogin(username=username, password=password)

            if user:
                login_user(user=user)
                return redirect(url_for('index'))
            else:
                err_msg = 'Tên đăng nhập hoặc mật khẩu không chính xác'
        except Exception as ex:
            err_msg = str(ex)
    return render_template('login.html', err_msg=err_msg)


@app.route('/user-logout')
def user_signout():
    logout_user()
    return redirect(url_for('index'))


@login.user_loader
def user_load(user_id):
    return utils.get_user_by_id(user_id=user_id)




# them sua xóa thuốc
@app.route('/admin/medicine/index')
def medicine():
    if current_user.user_role == UserRoleEnum.ADMIN:
        if request.method.__eq__('GET'):
            get_medicine = dao.get_medicine()
        return render_template('admin/medicine/index.html', thuoc=get_medicine, UserRoleEnum=UserRoleEnum)
    else:
        return redirect(url_for('index'))

@app.route('/admin/medicine/create')
def medicine_add():
    # validation = form.MedicineForm(request.form)
    return render_template('admin/medicine/create.html', UserRoleEnum=UserRoleEnum)

@app.route('/admin/medicine/create/submit', methods=['POST'])
def medicine_submit():
    err_msg = ""
    # validation = form.MedicineForm(request.form)
    if request.method == "POST":
        # and validation.validate()
        medicine_name = request.form['medicine_name']
        how_to_use = request.form['how_to_use']
        price = request.form['price']
        unit_name = request.form['unit_name']
        #
        # medicine = Medicine(medicine_name=medicine_name, how_to_use=how_to_use, price=price, unit_name=unit_name)
        # db.session.add(medicine)
        # db.session.commit()
        # flash('Thêm thành công')
        # return redirect('/medicine/index')
        try:
            if medicine_name == "" or how_to_use == "":
                err_msg = 'Vui lòng nhập đầy đủ thông tin'
                return render_template('admin/medicine/create.html', err_msg=err_msg, UserRoleEnum=UserRoleEnum)
            else:
                medicine = Medicine(medicine_name=medicine_name, how_to_use=how_to_use, price=price,
                                    unit_name=unit_name)
                db.session.add(medicine)
                db.session.commit()
                flash('Thêm thành công')
                return redirect('/admin/medicine/index')
        except:
            return 'Thuốc đã có sẵn vui lòng kiểm tra lại'

    return render_template('admin/medicine/create.html', UserRoleEnum=UserRoleEnum)

@app.route('/admin/medicine/update/<int:id>', methods=['GET', 'POST'])
def update_medicine(id):
    task = Medicine.query.get_or_404(id)
    if request.method == "POST":
        task.medicine_name = request.form['medicine_name']
        task.how_to_use = request.form['how_to_use']
        task.price = request.form['price']
        task.unit_name = request.form['unit_name']

        try:
            if task.medicine_name == "" or task.how_to_use == "":
                err_msg = 'Vui lòng nhập đầy đủ thông tin'
                return render_template('admin/medicine/update.html', err_msg=err_msg, UserRoleEnum=UserRoleEnum)
            else:
                db.session.commit()
                return redirect('/admin/medicine/index')
        except:
            return 'Thuốc đã có sẵn vui lòng kiểm tra lại'

    else:
        return render_template('admin/medicine/update.html', task=task, UserRoleEnum=UserRoleEnum)


@app.route('/admin/medicine/delete/<int:id>')
def delete_medicine(id):
    task_to_delete = Medicine.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/admin/medicine/index')
    except:
        return 'Có lỗi sảy ra khi xóa'



# them sua xoa phieu kham
@app.route('/doctor/index')
def phieukham():
    get_phieukham = dao.get_phieukham()
    return render_template('doctor/index.html', get_phieukham=get_phieukham, UserRoleEnum=UserRoleEnum)

@app.route('/doctor/create')
def phieukham_add():
    get_patient = dao.get_patient()
    return render_template('doctor/create.html', get_patient=get_patient, UserRoleEnum=UserRoleEnum)


@app.route('/doctor/create/submit', methods=['POST'])
def phieukham_submit():
    # validation = form.MedicalCertificateForm(request.form)
    # if request.method == 'POST' and validation.validate():
    #     phieukham = MedicalCertificate(validation.date_examination.data, validation.symptom.data,
    #                                    validation.sickness.data, validation.sum_price.data,
    #                                    validation.patient_id.data,)
    #     db.session.add(phieukham)
    #     flash('Tạo thành công')
    #     return redirect('/doctor/index')
    # return render_template('doctor/create.html', validation=validation, UserRoleEnum=UserRoleEnum)
    if request.method == "POST":
        date_examination = request.form['date_examination']
        symptom = request.form['symptom']
        disease_name = request.form['disease_name']
        total_amount = request.form['total_amount']
        patient_id = request.form['patient_id']


        phieukham = MedicalReport(date_examination = date_examination, symptom = symptom, disease_name=disease_name, total_amount=total_amount, patient_id=patient_id)

        db.session.add(phieukham)
        db.session.commit()

    return redirect('/doctor/index')

@app.route('/doctor/update/<int:id>', methods=['GET', 'POST'])
def update_phieukham(id):
    task = MedicalReport.query.get_or_404(id)
    get_patient = dao.get_patient()
    if request.method == "POST":
        task.date_examination = request.form['date_examination']
        task.symptom = request.form['symptom']
        task.disease_name = request.form['disease_name']
        task.total_amount = request.form['total_amount']
        task.patient_id = request.form['patient_id']
        try:
            db.session.commit()
            return redirect('/doctor/index')
        except:
            return 'Có lỗi sẩy ra khi cập nhật'

    else:
        return render_template('doctor/update.html', task=task,get_patient=get_patient, UserRoleEnum=UserRoleEnum)

@app.route('/doctor/delete/<int:id>')
def delete_phieukham(id):
    task_to_delete = MedicalReport.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/doctor/index')
    except:
        return 'Có lỗi sảy ra khi xóa'


# kiem tra thuoc
@app.route('/doctor/check-medicine')
def check_medicine():
    if current_user.user_role == UserRoleEnum.DOCTOR:
        if request.method.__eq__('GET'):
            get_medicine = dao.get_medicine()
        return render_template('doctor/check-medicine.html', thuoc=get_medicine, UserRoleEnum=UserRoleEnum)
    else:
        return redirect(url_for('index'))

# kiem tra benh nhan
@app.route('/doctor/check-disease-history')
def patientlist():
    get_patient = dao.get_patient()
    return render_template('doctor/check-disease-history.html', get_patient=get_patient, UserRoleEnum=UserRoleEnum)

# them don thuoc
@app.route('/doctor/prescription/index')
def donthuoc():
    get_prescription = dao.get_prescription()
    return render_template('doctor/prescription/index.html', get_prescription=get_prescription, UserRoleEnum=UserRoleEnum)


@app.route('/doctor/prescription/create')
def donthuoc_add():
    get_medicine = dao.get_medicine()
    get_phieukham = dao.get_phieukham()
    return render_template('doctor/prescription/create.html', get_medicine=get_medicine, get_phieukham=get_phieukham, UserRoleEnum=UserRoleEnum)


@app.route('/doctor/prescription/create/submit', methods=['POST'])
def donthuoc_submit():
    if request.method == "POST":
        count = request.form['count']
        medical_report_id = request.form['medical_report_id']
        medicine_id = request.form['medicine_id']


        donthuoc = Prescription(count = count, medical_report_id = medical_report_id, medicine_id=medicine_id)

        db.session.add(donthuoc)
        db.session.commit()

    return redirect('/doctor/prescription/index')

@app.route('/doctor/prescription/update/<int:phieukham_id><int:thuoc_id>', methods=['GET', 'POST'])
def update_donthuoc(phieukham_id,thuoc_id):
    task = Prescription.query.get_or_404(phieukham_id,thuoc_id)
    get_medicine = dao.get_medicine()
    get_phieukham = dao.get_phieukham()
    if request.method == "POST":
        task.count = request.form['count']
        task.phieukham_id = request.form['phieukham_id']
        task.thuoc_id = request.form['thuoc_id']
        try:
            db.session.commit()
            return redirect('/donthuoc/index')
        except:
            return 'Có lỗi sẩy ra khi cập nhật'

    else:
        return render_template('donthuoc/update.html', task=task,get_medicine=get_medicine,get_phieukham=get_phieukham)

@app.route('/doctor/prescription/delete/<int:phieukham_id><int:thuoc_id>')
def delete_donthuoc(phieukham_id,thuoc_id):
    task_to_delete = Prescription.query.get_or_404(phieukham_id,thuoc_id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/donthuoc/index')
    except:
        return 'Có lỗi xảy ra khi xóa'



if __name__ == "__main__":
    app.run(debug=True)