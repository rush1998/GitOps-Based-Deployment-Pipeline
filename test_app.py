import pytest
from models import models
from app import app, db


@pytest.fixture
def client():
    """Fixture to provide a test client with a fresh DB each test."""
    DATABASE = 'test_emp_db.db'
    app.config.update(
        SQLALCHEMY_DATABASE_URI='sqlite:///' + DATABASE,
        TESTING=True
    )
    with app.app_context():
        db.create_all()
    with app.test_client() as client:
        yield client
    with app.app_context():
        db.drop_all()


def test_index(client):
    response = client.get('/')
    assert response.status_code == 200


def test_index_response(client):
    response = client.get('/')
    assert b"Employee Data" in response.data
    assert models.Employee.query.count() == 0


def test_add(client):
    test_data = {
        'name': 'Mickey Test',
        'gender': 'male',
        'address': 'IN',
        'phone': '0123456789',
        'salary': '2000',
        'department': 'Sales'
    }
    client.post('/add', data=test_data)
    assert models.Employee.query.count() == 1

    emp = models.Employee.query.first()
    assert emp.name == 'Mickey Test'
    assert emp.department == 'Sales'


def test_edit(client):
    response = client.post('/edit/0')
    assert response.status_code == 200
    assert b"Sorry, the employee does not exist." in response.data


def test_delete(client):
    test_data = {'emp_id': 0}
    response = client.post('/delete', data=test_data)
    assert response.status_code == 200
    assert b"Sorry, the employee does not exist." in response.data
