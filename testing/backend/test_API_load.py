import os, sys
from pathlib import Path
from locust import HttpUser, between, task, events, SequentialTaskSet
root_path = Path(__file__).resolve().parents[2] # root/testing/backend/ThisFile ~ 2/1/0/file
if root_path not in sys.path:
    sys.path.append(str(root_path))
from backend.utils.backend_constants import CustomHeaders
from backend.database.queries.query_handler import shutdown_sessions
from testing.backend.test_API import generate_random_username_valid

TRUE_HEADER = CustomHeaders.CUSTOM_HEADER_FRONTEND.value
TRUE_HEADER_RESPONSE = CustomHeaders.CUSTOM_HEADER_FRONTEND_RESPONSE.value

class SetupTasks(SequentialTaskSet):
    """Class for User setup tasks (signup)"""
    def on_start(self) -> None:
        self.has_run = False

    @task
    def check_username(self):
        """Test /check_username API"""
        if self.has_run:
            return
        assert isinstance(self.user, User)
        # check name availability if not signed up
        with self.client.post("/api/check_username",json={"username":self.user.username},catch_response=True) as response:
            if response.status_code!=200:
                response.failure(f"Username validation failed: {response.status_code}")
            else:
                response.success() 

    @task
    def signup(self):
        """Test complete user signup and login-logout flow"""
        if self.has_run:
            return
        assert isinstance(self.user, User)
        self.res_body = {"username":self.user.username,"password":self.user.password}
        with self.client.post("/api/signup", json=self.res_body, catch_response=True) as response:
            if response.status_code != 201:
                response.failure(f"Signup failed: {response.status_code}")
            else:
                response.success()
    
    @task
    def stop(self):
        self.has_run=True

class UserFlow(SequentialTaskSet):
    @task
    def login(self):
        assert isinstance(self.user, User)
        self.res_body = {"username":self.user.username,"password":self.user.password}
        with self.client.post("/api/login",json=self.res_body,catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Signup failed: {response.status_code}")
            else:
                response.success()

    @task
    def logout(self):
        assert isinstance(self.user, User)
        with self.client.get("/api/logout",catch_response=True) as response:
            if response.status_code!=200:
                response.failure(f"Logout failed: {response.status_code}")
            else:
                response.success()

class User(HttpUser):
    wait_time = between(3,6)
    tasks = [UserFlow]
    def on_start(self) -> None:
        """Setup the custom header for the user session"""
        self.client.headers.update({TRUE_HEADER: TRUE_HEADER_RESPONSE})
        self.username = generate_random_username_valid()
        self.password = f"test_password{os.urandom(2).hex()}"
        setup = SetupTasks(self)
        setup.on_start()
        setup.check_username()
        setup.signup()
        setup.stop()

    @events.test_stop.add_listener
    def cleanup_database_engines(environment, **kwargs):
        """
        This runs ONCE on the Locust master process after the set
        test duration is over and all users have stopped
        """
        print("\n[CLEANUP] Load test finished. Disposing cached engines...")
        try:
            shutdown_sessions() 
            print("[CLEANUP] All test engines disposed successfully.")
        except Exception as e:
            print(f"[CLEANUP] Error during engine disposal: {e}")