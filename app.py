from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from models import setup_db, db, Doctor, Patient, Appointment
from datetime import datetime, timezone


def create_app(test_config=None):
    app = Flask(__name__)
    app.config['DEBUG'] = True

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
        setup_db(app, database_path=database_path)

    migrate = Migrate(app, db)
    with app.app_context():
        db.create_all()

    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        if not response.headers.get('Access-Control-Allow-Origin'):
            response.headers.add('Access-Control-Allow-Origin', '*')  
    
        if not response.headers.get('Access-Control-Allow-Headers'):
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    
        if not response.headers.get('Access-Control-Allow-Methods'):
            response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')

        return response


    # ======================================
    #  ROUTES
    # ======================================

    # 1. DOCTOR
    # ======================================
    @app.route('/doctors', methods=['GET'])
    def get_doctors():
        selection = Doctor.query.all()
        doctors = [doctor.format() for doctor in selection]
        return jsonify({
            'success': True,
            'doctors': doctors
        })
    
    @app.route('/doctors', methods=['POST'])
    def create_doctor():
        body = request.get_json()
        name = body.get('name', None)
        speciality = body.get('speciality', None)
        phone = body.get('phone', None)
        email = body.get('email', None)

        if not name or not speciality:
            abort(400)

        try:
            new_doctor = Doctor(
                name=name,
                speciality=speciality,
                phone=phone,
                email=email
            )
            new_doctor.insert()
            return jsonify({
                'success': True,
                'doctor': new_doctor.format()
            })
        except:
            db.session.rollback()
            abort(422)
    
    @app.route('/doctors/<int:doctor_id>', methods=['PATCH'])
    def update_doctor(doctor_id):
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            abort(404)

        body = request.get_json()
        name = body.get('name', None)
        speciality = body.get('speciality', None)
        phone = body.get('phone', None)
        email = body.get('email', None)

        if name:
            doctor.name = name
        if speciality:
            doctor.speciality = speciality
        if phone:
            doctor.phone = phone
        if email:
            doctor.email = email

        try:
            doctor.update()
            return jsonify({
                'success': True,
                'doctor': doctor.format()
            })
        except:
            db.session.rollback()
            abort(422)

    @app.route('/doctors/<int:doctor_id>', methods=['DELETE'])
    def delete_doctor(doctor_id):
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            abort(404)

        try:
            doctor.delete()
            return jsonify({
                'success': True,
                'deleted': doctor_id
            })
        except:
            db.session.rollback()
            abort(422)


    # 2. PATIENT
    # ======================================
    @app.route('/patients', methods=['GET'])
    def get_patients():
        selection = Patient.query.all()
        patients = [patient.format() for patient in selection]
        return jsonify({
            'success': True,
            'patients': patients
        })
    
    @app.route('/patients', methods=['POST'])
    def create_patient():
        body = request.get_json()
        name = body.get('name', None)
        phone = body.get('phone', None)
        address = body.get('address', None)
        medical_history = body.get('medical_history', None)

        if not name:
            abort(404)

        try:
            new_patient = Patient(
                name=name,
                phone=phone,
                address=address,
                medical_history=medical_history
            )
            new_patient.insert()
            return jsonify({
                'success': True,
                'patient': new_patient.format()
            })
        except:
            db.session.rollback()
            abort(422)

    @app.route('/patients/<int:patient_id>', methods=['PATCH'])
    def update_patient(patient_id):
        patient = Patient.query.get(patient_id)
        if not patient:
            abort(404)

        body = request.get_json()
        name = body.get('name', None)
        phone = body.get('phone', None)
        address = body.get('address', None)
        medical_history = body.get('medical_history', None)

        if name:
            patient.name = name
        if phone:
            patient.phone = phone
        if address:
            patient.address = address
        if medical_history:
            patient.medical_history = medical_history

        try:
            patient.update()
            return jsonify({
                'success': True,
                'patient': patient.format()
            })
        except:
            db.session.rollback()
            abort(422)

    @app.route('/patients/<int:patient_id>', methods=['DELETE'])
    def delete_patient(patient_id):
        patient = Patient.query.get(patient_id)
        if not patient:
            abort(404)

        try:
            patient.delete()
            return jsonify({
                'success': True,
                'patient': patient_id
            })
        except:
            db.session.rollback()
            abort(422)


    # 3. APPOINTMENTS
    # ======================================

    #  GET /appointments
    #  Description: Retrieves all APPOINTMENTS and GROUPS THEM BY DOCTOR.
    @app.route('/appointments', methods=['GET'])
    def get_appointments():
        appointments = Appointment.query.all()

        # Empty dictionary to hold appointments grouped by doctor
        grouped = {}

        # Iterate through each appointment
        for appointment in appointments:
            doctor_id = appointment.doctor_id
            doctor_name = appointment.doctor.name   #Backref

            if doctor_id not in grouped:
                grouped[doctor_id] = {
                    'doctor_name': doctor_name,
                    'appointments': []
                }

            # Append to the doctor's list
            grouped[doctor_id]['appointments'].append(appointment.format())

        # Convert dict into a list for easier JSON serialization
        result = list(grouped.values())

        return jsonify({
            'success': True,
            'appointments_by_doctor': result
        })
    
    #  GET /appointments/doctor/<doctor_id>
    #  Description: Retrieves all appointments related to a specific doctor by ID.
    @app.route('/appointments/doctor/<int:doctor_id>', methods=['GET'])
    def get_appointments_by_doctor(doctor_id):
        appointments = Appointment.query.filter_by(doctor_id=doctor_id).all()
        result = [appointment.format() for appointment in appointments]
        return jsonify({
            'success': True,
            'appointments': result
        })
    
    @app.route('/appointments', methods=['POST'])
    def create_appointment():
        body = request.get_json()
        date_str = body.get('date', None)
        status = body.get('status', None)
        notes = body.get('notes', None)
        doctor_id = body.get('doctor_id', None)
        patient_id = body.get('patient_id', None)

        if not date_str or not doctor_id or not patient_id:
            abort(400)

        try:
            date = datetime.fromisoformat(date_str)
            new_appointment = Appointment(
                date=date,
                status=status,
                notes=notes,
                doctor_id=doctor_id, 
                patient_id=patient_id
            )
            new_appointment.insert()
            return jsonify({
                'success': True, 
                'appointment': new_appointment.format()
            })
        except:
            db.session.rollback()
            abort(422)

    @app.route('/appointments/<int:appointment_id>', methods=['PATCH'])
    def update_appointments(appointment_id):
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            abort(404)

        body = request.get_json()
        date_str = body.get('date', None)
        status = body.get('status', None)
        notes = body.get('notes', None)

        if date_str:
            try:
                appointment.date = datetime.fromisoformat(date_str)
            except:
                abort(400)
        if status:
            appointment.status = status
        if notes:
            appointment.notes = notes

        try:
            appointment.update()
            return jsonify({
                'success': True,
                'appointment': appointment.format()
            })
        except:
            db.session.rollback()
            abort(422)

    @app.route('/appointments/<int:appointment_id>', methods=['DELETE'])
    def delete_appointment(appointment_id):
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            abort(404)

        try:
            appointment.delete()
            return jsonify({
                'success': True,
                'deleted': appointment_id
            })
        except:
            db.session.rollback()
            abort(422)


    return app

app = create_app()
if __name__ == '__main__':
    app.run()