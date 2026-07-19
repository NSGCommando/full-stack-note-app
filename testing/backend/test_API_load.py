import os, sys, logging, random
from pathlib import Path
from locust import HttpUser, between, task, events, SequentialTaskSet, TaskSet
root_path = Path(__file__).resolve().parents[2] # root/testing/backend/ThisFile ~ 2/1/0/file
if root_path not in sys.path:
    sys.path.append(str(root_path))
from backend.utils.backend_constants import CustomHeaders
from backend.utils.project_logger import get_project_logger
from backend.database.queries.query_handler import shutdown_sessions
from testing.backend.test_API import generate_random_username_valid

load_test_logger = get_project_logger(module_name="testing.backend.test_API_load",level=logging.DEBUG,log_dir=Path(__file__).resolve().parent)

TRUE_HEADER = CustomHeaders.CUSTOM_HEADER_FRONTEND.value
TRUE_HEADER_RESPONSE = CustomHeaders.CUSTOM_HEADER_FRONTEND_RESPONSE.value

class SetupTasks(SequentialTaskSet):
    """Class for User setup tasks (signup)"""
    def on_start(self) -> None:
        self.has_run = False

    @task
    def check_username(self)->None:
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
    def signup(self)->None:
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
    def stop(self)->None:
        self.has_run=True

class UserFlow(TaskSet): # With a TaskSet, I can set weightage to all tasks in the set
    def on_start(self)->None:
        self.login()
        self.notes_list = []

    def login(self)->None:
        assert isinstance(self.user, User)
        self.res_body = {"username":self.user.username,"password":self.user.password}
        with self.client.post("/api/login",json=self.res_body,catch_response=True) as response:
            if response.status_code != 200:
                response.failure(f"Signup failed: {response.status_code}")
            else:
                response.success()

    @task(1)
    def logout(self)->None:
        assert isinstance(self.user, User)
        self.random_note_body = None
        self.delete_note_body = None
        self.notes_list = []
        with self.client.get("/api/logout",catch_response=True) as response:
            if response.status_code!=200:
                response.failure(f"Logout failed: {response.status_code}")
            else:
                response.success()
                self.interrupt() # after logout, exit the current task set, the user will again choose the tast set and do a fresh login
                                 # This is needed else the user won't get the JWT to actually do anything

    @task(5)
    def add_note(self)->None:
        assert isinstance(self.user, User)
        self.random_note_body = {"note":f"random_note_{os.urandom(2).hex()}"}
        with self.client.post("/api/user/add-note", json=self.random_note_body,catch_response=True) as response:
            if response.status_code!=201:
                response.failure(f"Add Note failed: {response.status_code}")
            else:
                with self.client.get("/api/user/view-notes",catch_response=True) as notes_response:
                    if notes_response.status_code!=200:
                        notes_response.failure(f"View Notes failed: {notes_response.status_code}")
                    else:
                        self.notes_list = notes_response.json()["notes"] # response.json() is a dict in Python, 
                                                                         # which is not subscriptable (no dot access, like 'this.item'), 
                                                                         # so use key based access
                        notes_response.success()
                        response.success()
    
    @task(2)
    def delete_note(self)->None:
        assert isinstance(self.user, User)
        if not self.notes_list: return # don't try delete if there's no notes created by this user
        random_choice = random.choice(self.notes_list) # choose a random existing note to delete
        self.delete_note_body = {"note_id":random_choice["id"]}
        with self.client.delete("/api/user/notes-delete",json=self.delete_note_body, catch_response=True) as response:
            if response.status_code!=200:
                response.failure(f"Delete Random Note failed: {response.status_code}")
            else:
                self.notes_list.remove(random_choice) # Remove the note we just deleted from the user's view
                response.success()

class User(HttpUser):
    wait_time = between(3,6)
    tasks = [UserFlow]
    def on_start(self) -> None:
        """Setup the custom header for the user session"""
        self.client.headers.update({TRUE_HEADER: TRUE_HEADER_RESPONSE})
        self.username = generate_random_username_valid()
        self.password = f"test_password{os.urandom(2).hex()}"
        setup = SetupTasks(self) # Define the starter set of tasks - registration and signup
        setup.on_start()
        setup.check_username()
        setup.signup()
        setup.stop() # Setup tasks done and simulated user now ready, set the "has_run" flag to true to stop this running again

    @events.test_stop.add_listener
    def cleanup_database_engines(environment, **kwargs):
        """
        This runs ONCE on the Locust master process after the set
        test duration is over and all users have stopped
        """
        load_test_logger.info("\n[CLEANUP] Load test finished. Disposing cached engines...")
        try:
            shutdown_sessions() 
            load_test_logger.info("[CLEANUP] All test engines disposed successfully.")
        except Exception as e:
            load_test_logger.info(f"[CLEANUP] Error during engine disposal: {e}")