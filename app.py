from flask import Flask, request, abort, jsonify
from flask_cors import CORS

from models import setup_db, db, Doctor, Patient, Appointment


def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is None:
        setup_db(app)
    else:
        database_path = test_config.get('SQLALCHEMY_DATABASE_URI')
        setup_db(app, database_path=database_path)

    cors = CORS(app, resources={r"/*": {"origins": "*"}})

    with app.app_context():
        db.create_all()

    @app.after_request
    def after_request(response):
        if not response.headers.get('Access-Control-Allow-Origin'):
            response.headers.add('Access-Control-Allow-Origin', '*')  
    
        if not response.headers.get('Access-Control-Allow-Headers'):
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
    
        if not response.headers.get('Access-Control-Allow-Methods'):
            response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')

        return response

    @app.route('/')
    def starting():
        return jsonify({
            'message': 'lets start this fucking project!' 
        })

    return app


app = create_app()
if __name__ == '__main__':
    app.run()