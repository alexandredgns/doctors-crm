from flask import Flask, request, abort, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import setup_db, db, Doctor, Patient, Appointment


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



    return app

app = create_app()
if __name__ == '__main__':
    app.run()