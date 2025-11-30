import pytest
from project import app, db
from project.customers.models import Customer
import time
@pytest.fixture
def test_db():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()

def test_true():
    assert True
def test_correct_customer(test_db):
    customer = Customer(name="John Doe", city="New York", age=30, pesel="12345678901", street="Main St", appNo="1A")
    test_db.session.add(customer)
    test_db.session.commit()
    assert customer is not None
    found = Customer.query.filter_by(pesel="12345678901").first()
    assert found is not None
    assert found.name == "John Doe"

def test_wrong_name_customer(test_db):
    incorrect_names = [
        "",  # Empty name
        "A" * 101,  # Name too long
        "John123",  # Name with numbers
        "John@Doe",  # Name with special characters
        "John; DROP TABLE Customers;--"  # SQL Injection attempt
    ]
    with pytest.raises(Exception):
        for name in incorrect_names:
            Customer(name=name, city="New York", age=30, pesel="12345678901", street="Main St", appNo="1A")
def test_wrong_age_customer(test_db):
    incorrect_ages = [
        -1,  # Negative age
        200,  # Unrealistically high age
        "thirty",  # Non-integer age
        None  # Null age
    ]
    with pytest.raises(Exception):
        for age in incorrect_ages:
            Customer(name="John Doe", city="New York", age=age, pesel="12345678901", street="Main St", appNo="1A")

def test_wrong_pesel_customer(test_db):
    incorrect_pesels = [
        "123",  # Too short
        "12345678901234567890",  # Too long
        "ABCDEFGHIJK",  # Non-numeric
        "12345; DROP TABLE Customers;--"  # SQL Injection attempt
    ]
    with pytest.raises(Exception):
        for pesel in incorrect_pesels:
            Customer(name="John Doe", city="New York", age=30, pesel=pesel, street="Main St", appNo="1A")

def test_wrong_city_customer(test_db):
    incorrect_cities = [
        "",  # Empty city
        "A" * 101,  # City name too long
        "New York123",  # City with numbers
        "New York@City",  # City with special characters
        "New York; DROP TABLE Customers;--"  # SQL Injection attempt
    ]
    with pytest.raises(Exception):
        for city in incorrect_cities:
            Customer(name="John Doe", city=city, age=30, pesel="12345678901", street="Main St", appNo="1A")

def test_wrong_street_customer(test_db):
    incorrect_streets = [
        "",  # Empty street
        "A" * 129,  # Street name too long
        "Main St123",  # Street with numbers
        "Main St@Home",  # Street with special characters
        "Main St; DROP TABLE Customers;--"  # SQL Injection attempt
    ]
    with pytest.raises(Exception):
        for street in incorrect_streets:
            Customer(name="John Doe", city="New York", age=30, pesel="12345678901", street=street, appNo="1A")

def test_wrong_appNo_customer(test_db):
    incorrect_appNos = [
        "",  # Empty appNo
        "A" * 11,  # appNo too long
        "1A@2B",  # appNo with special characters
        "1A; DROP TABLE Customers;--"  # SQL Injection attempt
    ]
    with pytest.raises(Exception):
        for appNo in incorrect_appNos:
            Customer(name="John Doe", city="New York", age=30, pesel="12345678901", street="Main St", appNo=appNo)

xss_payloads = [
        "<script>alert('XSS')</script>",
        "<img src='x' onerror='alert(1)'>",
        "<iframe src='javascript:alert(1)'></iframe>",
        "<div style='background-image: url(javascript:alert(1))'>"
]
@pytest.mark.parametrize("payload", xss_payloads)
def test_customer_xss_name(payload):
    with pytest.raises(Exception):
        Customer(name=payload, city="New York", age=30, pesel="43567890123", street="Main St", appNo="1A")
@pytest.mark.parametrize("payload", xss_payloads)
def test_customer_xss_city(payload):
    with pytest.raises(Exception):
        Customer(name="John Doe", city=payload, age=30, pesel="12345678901", street="Main St", appNo="1A")
@pytest.mark.parametrize("payload", xss_payloads)
def test_customer_xss_street(payload):
    with pytest.raises(Exception):
        Customer(name="John Doe", city="New York", age=30, pesel="12445678901", street=payload, appNo="1A")
@pytest.mark.parametrize("payload", xss_payloads)
def test_customer_xss_street(payload):
    with pytest.raises(Exception):
        Customer(name="John Doe", city="New York", age=30, pesel="12445678901", street="Main St", appNo=payload)


def test_extreme_data(test_db):
    extreme_names = [
        "A" * 1000,
        "A" * 10000,
        "A" * 100000,
        "A" * 1000000,
        "A" * 10000000,
    ]
    now = time.time()
    with pytest.raises(Exception):
        for name in extreme_names:
            Customer(name=name, city="New York", age=30, pesel="12345678901", street="Main St", appNo="1A")
    end = time.time()
    operation_time = end - now
    print(f"Extreme data test operation time: {operation_time} seconds")
    assert (end - now) < 5