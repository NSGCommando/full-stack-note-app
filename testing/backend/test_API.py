import requests, pytest, logging
import os, sys,string
from pathlib import Path
from urllib.parse import urlparse
root_path = Path(__file__).resolve().parents[2] # root/testing/backend/ThisFile ~ 2/1/0/file
if root_path not in sys.path:
    sys.path.append(str(root_path))
from backend.utils.backend_constants import CustomHeaders
from backend.database.database_init import initialize_database
from backend.database.queries.query_handler import shutdown_sessions
from backend.utils.backend_functions import get_caller_filename
from backend.utils.project_logger import get_project_logger
# constants
TRUE_HEADER = CustomHeaders.CUSTOM_HEADER_FRONTEND.value
TRUE_HEADER_RESPONSE = CustomHeaders.CUSTOM_HEADER_FRONTEND_RESPONSE.value
API_URL = "http://127.0.0.1:5000"
test_logger = get_project_logger(logging.DEBUG,Path(__file__).resolve().parent)

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
    """Helper to wrap asserts and log test JSON responses"""
    caller_data = get_caller_filename(2) # get the test name
    test_logger.info(f"{caller_data.get("caller_func_name")} Response: {response.json()}")
    assert response.status_code == expected_status

# helper to inject session changes
def change_session_details(session):
    session.headers.update({TRUE_HEADER: "My-Fake-Header"})

@pytest.fixture
def session_manager():
    """Fixture to manage session creation and shutdown"""
    session = requests.session()
    session.headers.update({TRUE_HEADER: TRUE_HEADER_RESPONSE})
    initialize_database(test_mode=True)
    yield {"session":session} 
    shutdown_sessions()

@pytest.fixture
def gen_good_data():
    """Fixture to generate valid user data"""
    # invalid usernames and passwords
    username = generate_random_username_valid() # 2 bytes(16 bits) random, 4 bits are 1 hexadecimal number, total 4 randoms
    password = f"test_password{os.urandom(2).hex()}" 
    yield {
        "username":username,
        "password":password,
    }

@pytest.fixture
def login_setup(session_manager, gen_good_data):
    session=session_manager["session"]
    valid_data = {"username":gen_good_data["username"],"password":gen_good_data["password"]}
    session.post(f"{API_URL}/api/signup",json=valid_data)
    session.post(f"{API_URL}/api/login",json=valid_data)
    yield {
        "session":session,
        "username":gen_good_data["username"]
    }

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
def test_signup(session_manager,gen_good_data):
    """Test to validate signup route logic.
    APIs tested: /api/check_username, /api/signup"""
    # extract from fixture
    session = session_manager["session"]
    # valid dummy user data
    signup_dummy_user_data = {"username":gen_good_data["username"],"password":gen_good_data["password"]}
    signup_check_data = {"username":gen_good_data["username"]}
    # check username availability
    signup_check_username = session.post(f"{API_URL}/api/check_username",json=signup_check_data)
    assertion_wrapper(signup_check_username,200)
    print("\nSignup username check response:",signup_check_username.json())
    # actual signup API hit
    signup_data = signup_dummy_user_data
    signup_request = session.post(f"{API_URL}/api/signup",json=signup_data)
    assertion_wrapper(signup_request,201)

# login test
def test_login(session_manager,gen_good_data):
    """Test to confirm login API.
    API Tested: /api/login"""
    session = session_manager["session"]
    login_data = {"username":gen_good_data["username"],"password":gen_good_data["password"]}
    session.post(f"{API_URL}/api/signup",json=login_data)
    login_request = session.post(f"{API_URL}/api/login",json=login_data)
    assertion_wrapper(login_request,200)
    session.get(f"{API_URL}/api/logout")

# auth test for delete action
def test_delete(login_setup):
    """Test to validate role-based authorisation for admin actions(Delete).
    API Tested: /api/admin/users-delete"""
    session = login_setup["session"]
    user_data = {"username":login_setup["username"]}
    delete_request = session.delete(f"{API_URL}/api/admin/users-delete",json=user_data)
    assertion_wrapper(delete_request,403)
    session.get(f"{API_URL}/api/logout")

# logout test for users
def test_logout(login_setup):
    """Test for confirmation of logout functionality.
    API Tested: /api/logout"""
    session = login_setup["session"]
    logout_request=session.get(f"{API_URL}/api/logout")
    assertion_wrapper(logout_request,200)

# empty data test for users
def test_empty_data(session_manager,gen_good_data):
    """Test for confirmation of logout functionality.
    API Tested: /api/logout"""
    session = session_manager["session"]
    signup_no_username = {"username":"","password":gen_good_data["password"]}
    signup_no_password = {"username":gen_good_data["username"],"password":""}
    signup_t1 = session.post(f"{API_URL}/api/signup",json=signup_no_username)
    assertion_wrapper(signup_t1,400)
    signup_t2 = session.post(f"{API_URL}/api/signup",json=signup_no_password)
    assertion_wrapper(signup_t2,400)

def test_bad_data_username(session_manager,gen_bad_data):
    """Test for bad username validation rule"""
    session = session_manager["session"]
    # invalid data signup checks
    bad_check_data_username = {"username":gen_bad_data["bad_username"]}
    bad_signup_check_username = session.post(f"{API_URL}/api/check_username",json=bad_check_data_username)
    assertion_wrapper(bad_signup_check_username,400) # reject bad username
    
def test_bad_data_password(session_manager,gen_bad_data):
    """Test for bad password validation rule"""
    session = session_manager["session"]
    username_2 = generate_random_username_valid()
    bad_check_data_password = {"username":username_2,"password":gen_bad_data["bad_password"]}
    bad_signup_check_password = session.post(f"{API_URL}/api/check_username",json=bad_check_data_password)
    assertion_wrapper(bad_signup_check_password,200) # accept valid username
    bad_data_username = {"username":username_2,"password":gen_bad_data["bad_password"]}
    bad_signup_request_password = session.post(f"{API_URL}/api/signup",json=bad_data_username)
    assertion_wrapper(bad_signup_request_password,400) # reject bad password

# try signup with fake header
def test_malicious_attacker_fake_header(session_manager,gen_good_data):
    session=session_manager["session"]
    change_session_details(session=session)
    user_data_hacker = {"username":gen_good_data["username"],"password":gen_good_data["password"]}
    signup_data_hacker = user_data_hacker
    signup_request_hacker = session.post(f"{API_URL}/api/signup",json=signup_data_hacker)
    assertion_wrapper(signup_request_hacker,403)

# try signup with unsafe username
def test_malicious_attacker_unsafe_name(session_manager,gen_good_data):
    session=session_manager["session"]
    user_data_hacker = {"username":"' OR 1=1 --","password":gen_good_data["password"]}
    signup_data_hacker = user_data_hacker
    signup_request_hacker = session.post(f"{API_URL}/api/signup",json=signup_data_hacker)
    assertion_wrapper(signup_request_hacker,400)

# try login with invalid token
def test_malicious_attacker_invalid_jwt(login_setup):
    session=login_setup["session"]
    # extract the JWT
    valid_jwt = session.cookies.get("access_token_cookie")
    # test_logger.debug(f"Length of valid_jwt:{len(valid_jwt)}")
    session.get(f"{API_URL}/api/logout") # logout
    # manually set the cookie back with extracted url domain
    domain = urlparse(API_URL).hostname
    session.cookies.set("access_token_cookie", valid_jwt, domain=domain)
    access_invalid_request = session.get(f"{API_URL}/api/user/view-notes")# try accessing protected route now 
    assertion_wrapper(access_invalid_request,401)
