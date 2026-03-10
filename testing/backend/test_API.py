import requests, pytest
import os, sys,string
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if root_path not in sys.path:
    sys.path.append(root_path)
from backend.backend_constants import CustomHeaders
from backend.database_init import initialize_database
from backend.query_handler import shutdown_sessions
from backend.backend_functions import get_caller_filename
# constants
TRUE_HEADER = CustomHeaders.CUSTOM_HEADER_FRONTEND.value
TRUE_HEADER_RESPONSE = CustomHeaders.CUSTOM_HEADER_FRONTEND_RESPONSE.value
API_URL = "http://127.0.0.1:5000"

def generate_random_username_valid():
    """
    Generate random usernames within allowed length using allowed character list
    Returns the generated username
    """
    length = os.urandom(1)[0] % 6 + 5  # random length between 5 and 10
    ALLOWED_CHARS = string.ascii_letters + string.digits
    username = ''.join(ALLOWED_CHARS[b % len(ALLOWED_CHARS)] for b in os.urandom(length))
    return username

# helper to wrap assert call and print response body in case of failure
def assertion_wrapper(response,expected_status:int):
    caller_data = get_caller_filename()
    print(f"{caller_data.get("caller_func_name")} Response: {response.json()}")
    assert response.status_code == expected_status

# helper to inject session changes
def change_session_details(session):
    session.headers.update({TRUE_HEADER: "My-Fake-Header"})

@pytest.fixture
def session_manager():
    """Fixture to manage session creation and shutdown"""
    session = requests.session()
    session = requests.session()
    session.headers.update({TRUE_HEADER: TRUE_HEADER_RESPONSE})
    initialize_database(test_mode=True)
    yield {"session":session} 
    shutdown_sessions()

@pytest.fixture
def gen_bad_data():
    """Fixture to generate invalid user data"""
    # invalid usernames and passwords
    bad_username = f"user_{os.urandom(2).hex()}" # 2 bytes(16 bits) random, 4 bits are 1 hexadecimal number, total 4 randoms
    bad_password = f"test_password{os.urandom(5).hex()}" 
    yield {
        "bad_username":bad_username,
        "bad_password":bad_password,
    }

# signup test
def test_signup(session_manager):
    """Test to validate signup route logic.
    APIs tested: /check_username, /signup"""
    # extract from fixture
    session = session_manager["session"]
    # generate signup data
    signup_username = generate_random_username_valid()
    signup_password = f"test_password{os.urandom(2).hex()}"
    # valid dummy user data
    signup_dummy_user_data = {"username":signup_username,"password":signup_password}
    signup_check_data = {"username":signup_dummy_user_data["username"]}
    # check username availability
    signup_check_username = session.post(f"{API_URL}/check_username",json=signup_check_data)
    assertion_wrapper(signup_check_username,200)
    print("\nSignup username check response:",signup_check_username.json())
    # actual signup API hit
    signup_data = signup_dummy_user_data
    signup_request = session.post(f"{API_URL}/signup",json=signup_data)
    assertion_wrapper(signup_request,201)
    # print("\nSignup response:",signup_request.json())

# login test
def test_login(session_manager):
    """Test to confirm login API.
    API Tested: /login"""
    session = session_manager["session"]
    username = generate_random_username_valid()
    password = f"test_password{os.urandom(2).hex()}"
    login_data = {"username":username,"password":password}
    session.post(f"{API_URL}/signup",json=login_data)
    login_request = session.post(f"{API_URL}/login",json=login_data)
    assertion_wrapper(login_request,200)
    # print("\nLogin response:",login_request.json())
    session.get(f"{API_URL}/logout")

# auth test for delete action
def test_delete(session_manager):
    """Test to validate role-based authorisation for admin actions(Delete).
    API Teste: /api/users"""
    session = session_manager["session"]
    username = generate_random_username_valid()
    password = f"test_password{os.urandom(2).hex()}"
    login_data = {"username":username,"password":password}
    session.post(f"{API_URL}/signup",json=login_data)
    session.post(f"{API_URL}/login",json=login_data)
    user_data = {"username":username}
    delete_request = session.delete(f"{API_URL}/api/users",json=user_data)
    assertion_wrapper(delete_request,403)
    # print("\nDelete response:",delete_request.json())
    session.get(f"{API_URL}/logout")

# logout test for users
def test_logout(session_manager):
    """Test for confirmation of logout functionality.
    API Tested: /logout"""
    session = session_manager["session"]
    username = generate_random_username_valid()
    password = f"test_password{os.urandom(2).hex()}"
    login_data = {"username":username,"password":password}
    session.post(f"{API_URL}/signup",json=login_data)
    session.post(f"{API_URL}/login",json=login_data)
    logout_request=session.get(f"{API_URL}/logout")
    assertion_wrapper(logout_request,200)
    # print("\nLogout response:",logout_request.json())

def test_bad_data_username(session_manager,gen_bad_data):
    """Test for bad username validation rule"""
    session = session_manager["session"]
    # invalid data signup checks
    bad_check_data_username = {"username":gen_bad_data["bad_username"]}
    bad_signup_check_username = session.post(f"{API_URL}/check_username",json=bad_check_data_username)
    assertion_wrapper(bad_signup_check_username,400) # reject bad username
    # print("\nBad Username Check Username response:",bad_signup_check_username.json())
    
def test_bad_data_password(session_manager,gen_bad_data):
    """Test for bad password validation rule"""
    session = session_manager["session"]
    username_2 = generate_random_username_valid()
    bad_check_data_password = {"username":username_2,"password":gen_bad_data["bad_password"]}
    bad_signup_check_password = session.post(f"{API_URL}/check_username",json=bad_check_data_password)
    assertion_wrapper(bad_signup_check_password,200) # accept valid username
    bad_data_username = {"username":username_2,"password":gen_bad_data["bad_password"]}
    bad_signup_request_password = session.post(f"{API_URL}/signup",json=bad_data_username)
    assertion_wrapper(bad_signup_request_password,400) # reject bad password
    # print("\nBad Signup Check Password response:",bad_signup_request_password.json())

# try signup with fake header
def test_malicious_attacker(session_manager):
    session=session_manager["session"]
    change_session_details(session=session)
    username_hacker = generate_random_username_valid()
    password_hacker = f"test_password{os.urandom(2).hex()}" 
    user_data_hacker = {"username":username_hacker,"password":password_hacker}
    signup_data_hacker = user_data_hacker
    signup_request_hacker = session.post(f"{API_URL}/signup",json=signup_data_hacker)
    assertion_wrapper(signup_request_hacker,403)
    # print("\nHacker Signup response:",signup_request_hacker.json())