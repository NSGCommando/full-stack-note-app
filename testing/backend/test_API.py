import requests, unittest
import os, sys,string
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
if root_path not in sys.path:
    sys.path.append(root_path)
from backend.backend_constants import BackendPaths,CustomHeaders
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

        # setUp for attacker session
        self.hacker_session = requests.session()
        self.hacker_session.headers.update({TRUE_HEADER: "Fake-Header-Hacker"})
        initialize_database(test_mode=True)
        
    def tearDown(self):
        """Destructor hook, called after each test"""
        shutdown_sessions()

    def test_signup_login_auth_flow(self):
        # signup test
        self.username = generate_random_username_valid()
        self.password = f"test_password{os.urandom(2).hex()}"
        # invalid usernames and passwords
        self.bad_username = f"user_{os.urandom(2).hex()}"
        self.bad_password = f"test_password{os.urandom(5).hex()}"
        # valid dummy user data
        self.dummy_user_data = {"username":self.username,"password":self.password}
        check_data = {"username":self.dummy_user_data["username"]} # all body data need to be enclosed in {} with keys:values
        # signup test
        signup_check_username = self.session.post(f"{API_URL}/check_username",json=check_data)
        self.assertion_wrapper(signup_check_username,200)
        signup_data = self.dummy_user_data
        signup_request = self.session.post(f"{API_URL}/signup",json=signup_data)
        self.assertion_wrapper(signup_request,201)

        # login test
        login_data = self.dummy_user_data
        login_request = self.session.post(f"{API_URL}/login",json=login_data)
        self.assertion_wrapper(login_request,200)

        # auth test for delete action
        user_data = {"username":self.dummy_user_data['username']}
        delete_request = self.session.delete(f"{API_URL}/api/users",json=user_data)
        self.assertion_wrapper(delete_request,403)

        # logout test for users
        logout_request = self.session.get(f"{API_URL}/logout")
        self.assertion_wrapper(logout_request,200)

        # invalid data signup checks
        bad_check_data_username = {"username":self.bad_username}
        bad_signup_check_username = self.session.post(f"{API_URL}/check_username",json=bad_check_data_username)
        self.assertion_wrapper(bad_signup_check_username,400) # reject bad username
       
        self.username_2 = generate_random_username_valid()
        bad_check_data_password = {"username":self.username_2,"password":self.bad_password}
        bad_signup_check_password = self.session.post(f"{API_URL}/check_username",json=bad_check_data_password)
        self.assertion_wrapper(bad_signup_check_password,200) # accept valid username
        bad_data_username = {"username":self.username_2,"password":self.bad_password}
        bad_signup_request_password = self.session.post(f"{API_URL}/signup",json=bad_data_username)
        self.assertion_wrapper(bad_signup_request_password,400) # reject bad password

        # print custom responses to track test run
        print("\nSignup username check response:",signup_check_username.json())
        print("Signup response:",signup_request.json())
        print("Login response:",login_request.json())
        print("Delete response:",delete_request.json())
        print("Logout response:",logout_request.json())
        print("Bad Username Check Username response:",bad_signup_check_username.json())
        print("Bad Signup Check Password response:",bad_signup_request_password.json())

    def test_malicious_attacker(self):
        # try signup with fake header
        self.username = generate_random_username_valid()
        self.password = f"test_password{os.urandom(2).hex()}" # 2 bytes(16 bits) random, 4 bits are 1 hexadecimal number, total 4 randoms
        self.dummy_user_data = {"username":self.username,"password":self.password}
        signup_data = self.dummy_user_data
        signup_request = self.hacker_session.post(f"{API_URL}/signup",json=signup_data)
        self.assertion_wrapper(signup_request,403)

        # print custom responses to track test run
        print("Hacker Signup response:",signup_request.json())

if __name__ == "__main__":
    unittest.main()