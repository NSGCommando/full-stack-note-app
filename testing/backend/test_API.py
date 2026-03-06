import requests, unittest
import os, sys,string
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if root_path not in sys.path:
    sys.path.append(root_path)
from backend.backend_constants import CustomHeaders
from backend.database_init import initialize_database
from backend.query_handler import shutdown_sessions
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

class TestAPI(unittest.TestCase):
    # helper to wrap assert call and print response body in case of failure
    def assertion_wrapper(self, response,expected_status:int):
        try:
            self.assertEqual(response.status_code,expected_status)
        except AssertionError as e:
            print("Response:",response.json())
            raise e

    def setUp(self): # standard naming for "unittest"
        self.session = requests.session()
        self.session.headers.update({TRUE_HEADER: TRUE_HEADER_RESPONSE})
        # invalid usernames and passwords
        self.bad_username = f"user_{os.urandom(2).hex()}"
        self.bad_password = f"test_password{os.urandom(5).hex()}"
        # setUp for attacker session
        self.hacker_session = requests.session()
        self.hacker_session.headers.update({TRUE_HEADER: "Fake-Header-Hacker"})
        initialize_database(test_mode=True)
        
    def tearDown(self):
        """Destructor hook, called after each test"""
        shutdown_sessions()

    # signup test
    def test_signup(self):
        signup_username = generate_random_username_valid()
        signup_password = f"test_password{os.urandom(2).hex()}"
        # valid dummy user data
        signup_dummy_user_data = {"username":signup_username,"password":signup_password}
        signup_check_data = {"username":signup_dummy_user_data["username"]}
        signup_check_username = self.session.post(f"{API_URL}/check_username",json=signup_check_data)
        self.assertion_wrapper(signup_check_username,200)
        print("\nSignup username check response:",signup_check_username.json())
        signup_data = signup_dummy_user_data
        signup_request = self.session.post(f"{API_URL}/signup",json=signup_data)
        self.assertion_wrapper(signup_request,201)
        print("\nSignup response:",signup_request.json())

    # login test
    def test_login(self):
        username = generate_random_username_valid()
        password = f"test_password{os.urandom(2).hex()}"
        login_data = {"username":username,"password":password}
        self.session.post(f"{API_URL}/signup",json=login_data)
        login_request = self.session.post(f"{API_URL}/login",json=login_data)
        self.assertion_wrapper(login_request,200)
        print("\nLogin response:",login_request.json())
        self.session.get(f"{API_URL}/logout")

    # auth test for delete action
    def test_delete(self):
        username = generate_random_username_valid()
        password = f"test_password{os.urandom(2).hex()}"
        login_data = {"username":username,"password":password}
        self.session.post(f"{API_URL}/signup",json=login_data)
        self.session.post(f"{API_URL}/login",json=login_data)
        user_data = {"username":username}
        delete_request = self.session.delete(f"{API_URL}/api/users",json=user_data)
        self.assertion_wrapper(delete_request,403)
        print("\nDelete response:",delete_request.json())
        self.session.get(f"{API_URL}/logout")

    # logout test for users
    def test_logout(self):
        username = generate_random_username_valid()
        password = f"test_password{os.urandom(2).hex()}"
        login_data = {"username":username,"password":password}
        self.session.post(f"{API_URL}/signup",json=login_data)
        self.session.post(f"{API_URL}/login",json=login_data)
        logout_request=self.session.get(f"{API_URL}/logout")
        self.assertion_wrapper(logout_request,200)
        print("\nLogout response:",logout_request.json())

    def test_bad_data_username(self):
        """Test for bad username validation rule"""
        # invalid data signup checks
        bad_check_data_username = {"username":self.bad_username}
        bad_signup_check_username = self.session.post(f"{API_URL}/check_username",json=bad_check_data_username)
        self.assertion_wrapper(bad_signup_check_username,400) # reject bad username
        print("\nBad Username Check Username response:",bad_signup_check_username.json())
       
    def test_bad_data_password(self):
        """Test for bad password validation rule"""
        self.username_2 = generate_random_username_valid()
        bad_check_data_password = {"username":self.username_2,"password":self.bad_password}
        bad_signup_check_password = self.session.post(f"{API_URL}/check_username",json=bad_check_data_password)
        self.assertion_wrapper(bad_signup_check_password,200) # accept valid username
        bad_data_username = {"username":self.username_2,"password":self.bad_password}
        bad_signup_request_password = self.session.post(f"{API_URL}/signup",json=bad_data_username)
        self.assertion_wrapper(bad_signup_request_password,400) # reject bad password
        print("\nBad Signup Check Password response:",bad_signup_request_password.json())

    def test_malicious_attacker(self):
        # try signup with fake header
        self.username_hacker = generate_random_username_valid()
        self.password_hacker = f"test_password{os.urandom(2).hex()}" # 2 bytes(16 bits) random, 4 bits are 1 hexadecimal number, total 4 randoms
        self.user_data_hacker = {"username":self.username_hacker,"password":self.password_hacker}
        signup_data_hacker = self.user_data_hacker
        signup_request_hacker = self.hacker_session.post(f"{API_URL}/signup",json=signup_data_hacker)
        self.assertion_wrapper(signup_request_hacker,403)

        # print custom responses to track test run
        print("\nHacker Signup response:",signup_request_hacker.json())

if __name__ == "__main__":
    unittest.main()