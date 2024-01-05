from flask import Flask, render_template, request, redirect, url_for, flash
from app.models import Medicine, UserRoleEnum, Patient
import dao
from app import app, db, utils, login
from flask_login import login_user, logout_user, login_required, current_user


@app.route('/')
def index():
    return render_template('index.html', UserRoleEnum=UserRoleEnum)


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


@app.route('/appointment', methods=['get','post'])
def user_appointment():
    # check role bệnh nhân
    err_msg = ""
    sc_msg=""
    if current_user.user_role == UserRoleEnum.PATIENT:
        if request.method.__eq__('POST'):
            name = request.form.get('name')
            gender = request.form['gender']
            date_appointment = request.form.get('date_appointment')
            date_of_birth = request.form.get('date_of_birth')
            address = request.form.get('address')
            disease_history = request.form.get('disease_history')

            try:
                count = Patient.query.filter_by(date_appointment=date_appointment).count()
                if count == 10:
                    err_msg = 'Ngày đăng ký khám đã hết chỗ'
                    return render_template('patient/appointment.html', err_msg = err_msg, UserRoleEnum=UserRoleEnum)
                utils.add_appointment(name=name,gender=gender,date_appointment=date_appointment, date_of_birth=date_of_birth,address=address,disease_history=disease_history)
            except Exception as ex:
                err_msg = 'Đăng ký khám không thành công' + str(ex)
            else:
                sc_msg = 'Đăng ký khám thành công'
                return  render_template('patient/appointment.html', sc_msg=sc_msg,UserRoleEnum=UserRoleEnum)
        return render_template('patient/appointment.html',err_msg=err_msg, UserRoleEnum=UserRoleEnum)
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





@app.route('/medicine/index')
def medicine():
    thuoc = dao.get_medicine()
    return render_template('medicine/index.html', thuoc=thuoc)


@app.route('/medicine/create')
def medicine_add():
    return render_template('medicine/create.html')
    # insertthuoc = dao.insertthuoc()


@app.route('/medicine/create/submit', methods=['POST'])
def medicine_submit():
    if request.method == "POST":
        medicine_name = request.form['medicine_name']
        how_to_use = request.form['how_to_use']
        unit_name = request.form['unit_name']

        medicine = Medicine(medicine_name=medicine_name, how_to_use=how_to_use, unit_name=unit_name)

        db.session.add(medicine)
        db.session.commit()

    return redirect('/medicine/index')


@app.route('/medicine/delete/<int:id>')
def delete(id):
    task_to_delete = Medicine.query.get_or_404(id)

    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/medicine/index')
    except:
        return 'Có lỗi sảy ra khi xóa'


@app.route('/medicine/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = Medicine.query.get_or_404(id)

    if request.method == "POST":
        task.tenthuoc = request.form['tenthuoc']
        task.cachdung = request.form['cachdung']
        task.soluong = request.form['soluong']
        task.donvi = request.form['donvi']

        try:
            db.session.commit()
            return redirect('/medicine/index')
        except:
            return 'Có lỗi xảy ra khi cập nhật'

    else:
        return render_template('medicine/update.html', task=task)


if __name__ == "__main__":
    app.run(debug=True)