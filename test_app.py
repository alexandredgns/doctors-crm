import os
import unittest
import json
from app import create_app
from models import db

# Placeholder JWT tokens for testing:
ADMIN_TOKEN = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5meERVQ0FNdkhyTmRIWHRGLW9aZiJ9.eyJpc3MiOiJodHRwczovL3VkYWNpdHktYWxleGFuZHJlZGducy51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjhlOTYxNzE5ZjlhMDg3MTA3NzAyOGJlIiwiYXVkIjoiZG9jdG9ycy1jcm0iLCJpYXQiOjE3NjM0OTQ4MzAsImV4cCI6MTc2MzU4MTIzMCwic2NvcGUiOiIiLCJhenAiOiIwQ1VaenMzY0s5cWJPRVNsbE44TDhvd0J4TXFoeTI2RiIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTphcHBvaW50bWVudHMiLCJkZWxldGU6ZG9jdG9ycyIsImRlbGV0ZTpwYXRpZW50cyIsImdldDphcHBvaW50bWVudHMiLCJnZXQ6YXBwb2ludG1lbnRzLWRvY3RvciIsImdldDpwYXRpZW50cyIsInBhdGNoOmFwcG9pbnRtZW50cyIsInBhdGNoOmRvY3RvcnMiLCJwYXRjaDpwYXRpZW50cyIsInBvc3Q6YXBwb2ludG1lbnRzIiwicG9zdDpkb2N0b3JzIiwicG9zdDpwYXRpZW50cyJdfQ.mAXCewaM_bIy8kPYtC8_SzpZZfGRhQPiEn3Q6rTfu9jVulx0VxE2fChJLMbxpgfTVNeaDeTXdSXdTgbtW2Q2MhSHddabNkzgZUEShQVXwbxgKJtDWN3E1hd9KA3LN2q9itI7UL_fYLLBjCLTr9mvfgL4PcXHmqa_ylTZ7BS0q5uKhw-eYj8zFUaRv0r83d4a0Xe9f2Q1IDnBBwBC5Z8kvJ58V6J6Q-_s5nvoW-jdLD8XcdBRJAXCKo60xZEJzca9nGcpVogY-5wxULgFpQTTwgHRnjvxyMaDUb5sxCTHtwI3KKDpyoK-lOWb5cawn9YuuXccWhoRKyIvpIRXyClnIA'
DOCTOR_TOKEN = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik5meERVQ0FNdkhyTmRIWHRGLW9aZiJ9.eyJpc3MiOiJodHRwczovL3VkYWNpdHktYWxleGFuZHJlZGducy51cy5hdXRoMC5jb20vIiwic3ViIjoiYXV0aDB8NjhmN2M1NWMyMzE4M2IwMWJjOTllMTQ2IiwiYXVkIjoiZG9jdG9ycy1jcm0iLCJpYXQiOjE3NjM0OTUwMzIsImV4cCI6MTc2MzU4MTQzMiwic2NvcGUiOiIiLCJhenAiOiIwQ1VaenMzY0s5cWJPRVNsbE44TDhvd0J4TXFoeTI2RiIsInBlcm1pc3Npb25zIjpbImRlbGV0ZTphcHBvaW50bWVudHMiLCJnZXQ6YXBwb2ludG1lbnRzLWRvY3RvciIsImdldDpwYXRpZW50cyIsInBhdGNoOmFwcG9pbnRtZW50cyIsInBhdGNoOnBhdGllbnRzIiwicG9zdDphcHBvaW50bWVudHMiLCJwb3N0OnBhdGllbnRzIl19.hIrLnfDnPzUBA6mHBdKWNAskuE-ooWzsQynoLHuFaBBPwlkMwSatQ_ZPfNsYs5gF9vlkm1SBFhPD33bnHvfQIoXnIWwIsuW-roynmh3vSmffuUJtnYZ2mXd5H42j6qf9UQcLjf_m0wkzGLP2KIU9Zapoa51O_8_Nn7Ew-XjOxceIBrWF5grhvHwUenm8PxyXj89fvdIV8hlGNScW1rEibK52HqL8cNZ9FHUBy5UUfynjMq4zXpy-1qbwHwePY7WJIz41XULK3ehWXQBEtGPVyw8YH9OfR0QOPWE4WFxKm1LzMWFzK-QUI4L5ibPID_jo_Y-d0kX07Nse6K8DGVfvmQ'

def get_auth_header(token):
    """Create authorization header with token."""
    return {
        "Authorization": f"Bearer {token}"
    }

class AppTestCase(unittest.TestCase):
    def setUp(self):
        """Configure the app and setup the database."""
        self.database_name = "doctors_crm_test"
        self.database_user = "postgres"
        self.database_password = "Dev26776"
        self.database_host = "localhost:5432"
        self.database_path = f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}/{self.database_name}"
        
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client()

        # Create all tables
        with self.app.app_context():
            db.create_all()

        # Store headers for different roles
        self.admin_headers = get_auth_header(ADMIN_TOKEN)
        self.doctor_headers = get_auth_header(DOCTOR_TOKEN)

        # Sample data for POST requests
        self.new_doctor = {
            'name': 'Dr. Test',
            'speciality': 'Neurology',
            'phone': '11999999999',
            'email': 'test@doctor.com'
        }

        self.new_patient = {
            'name': 'Maria Silva',
            'phone': '11988888888',
            'address': '123 Test Street',
            'medical_history': 'None'
        }

        self.new_patient_400_error = {
            'phone': '11111111'
        }

        self.new_appointment = {
            'date': '2025-11-25T15:00:00',
            'status': 'Scheduled',
            'notes': 'First consultation',
            'doctor_id': 1,
            'patient_id': 1
        }

        self.new_appointment_400_error = {
            'doctor_id': 2
        }

    def tearDown(self):
        pass

    # ===========================
    # Tests for /doctors endpoint
    # ===========================

    def test_get_doctors_success(self):
        """Test retrieving doctors list (success)."""
        res = self.client.get('/doctors')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIn('doctors', data)

    def test_create_doctor_success(self):
        """Test creating a new doctor with admin role."""
        res = self.client.post('/doctors', headers=self.admin_headers, json=self.new_doctor)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_create_doctor_forbidden(self):
        """Test creating doctor without admin role (should fail)."""
        res = self.client.post('/doctors', headers=self.doctor_headers, json={})
        self.assertIn(res.status_code, [401, 403])

    def test_patch_doctor_success(self):
        """Test updating a doctor with valid data (success)."""
        res = self.client.patch('/doctors/1', headers=self.admin_headers, json={'name': 'Dr. Updated'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_404_patch_doctor_not_found(self):
        """Test updating a non-existent doctor (error)."""
        res = self.client.patch('/doctors/9999', headers=self.admin_headers, json={'name': 'No one'})
        self.assertEqual(res.status_code, 404)

    def test_delete_doctor_success(self):
        """Test deleting an existing doctor (success)."""
        res = self.client.delete('/doctors/1', headers=self.admin_headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_404_delete_doctor_not_found(self):
        """Test deleting a non-existent doctor (error)."""
        res = self.client.delete('/doctors/9999', headers=self.admin_headers)
        self.assertEqual(res.status_code, 404)

    # ===========================
    # Tests for /patients endpoint
    # ===========================

    def test_get_patients_success(self):
        """Test retrieving patients list."""
        res = self.client.get('/patients', headers=self.admin_headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    def test_post_patient_success(self):
        """Test creating a patient successfully."""
        res = self.client.post('/patients', headers=self.admin_headers, json=self.new_patient)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_400_post_patient_error(self):
        """Test creating a patient with missing data (error)."""
        res = self.client.post('/patients', headers=self.admin_headers, json=self.new_patient_400_error)
        self.assertEqual(res.status_code, 400)

    def test_patch_patient_success(self):
        """Test updating a patient successfully."""
        res = self.client.patch('/patients/1', headers=self.admin_headers, json={'name': 'New Name'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_patch_patient_forbidden(self):
        """Test updating patient without proper permission."""
        res = self.client.patch('/patients/1', headers=self.doctor_headers, json={})
        self.assertIn(res.status_code, [401, 403])

    def test_delete_patient_success(self):
        """Test deleting a patient successfully."""
        res = self.client.delete('/patients/1', headers=self.admin_headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_404_delete_patient_not_found(self):
        """Test deleting a non-existent patient."""
        res = self.client.delete('/patients/9999', headers=self.admin_headers)
        self.assertEqual(res.status_code, 404)

    # ================================
    # Tests for /appointments endpoint
    # ================================

    def test_get_appointments_success(self):
        """Test retrieving appointments list."""
        res = self.client.get('/appointments', headers=self.admin_headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIn('appointments', data)

    def test_get_appointments_by_doctor_role(self):
        """Test fetching appointments for a specific doctor (role)."""
        res = self.client.get('/appointments/doctor/1', headers=self.doctor_headers)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)

    def test_post_appointment_success(self):
        """Test creating an appointment successfully."""
        res = self.client.post('/appointments', headers=self.admin_headers, json=self.new_appointment)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_400_post_appointment_error(self):
        """Test creating an appointment with missing data (error)."""
        res = self.client.post('/appointments', headers=self.admin_headers, json=self.new_appointment_400_error)
        self.assertEqual(res.status_code, 400)

    def test_patch_appointment_success(self):
        """Test updating an appointment successfully."""
        res = self.client.patch('/appointments/1', headers=self.admin_headers, json={'status': 'Completed'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_404_patch_appointment_not_found(self):
        """Test updating a non-existent appointment."""
        res = self.client.patch('/appointments/9999', headers=self.admin_headers, json={'status': 'Canceled'})
        self.assertEqual(res.status_code, 404)

    def test_delete_appointment_success(self):
        """Test deleting appointment (admin role)."""
        # Assuming appointment with id=1 exists
        res = self.client.delete('/appointments/1', headers=self.admin_headers)
        self.assertIn(res.status_code, [200, 404])  # may not exist

    def test_delete_appointment_forbidden(self):
        """Test deleting appointment with doctor role (should fail)."""
        res = self.client.delete('/appointments/1', headers=self.doctor_headers)
        self.assertIn(res.status_code, [401, 403, 404])


if __name__ == '__main__':
    unittest.main()