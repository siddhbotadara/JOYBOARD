from locust import HttpUser, task, between

class JoyboardUser(HttpUser):
    # Simulate a user waiting 1 to 3 seconds between actions
    wait_time = between(1, 3)

    @task(3)
    def view_homepage(self):
        """High priority: Most users just visit the home page."""
        self.client.get("/")

    @task(1)
    def check_leaderboard(self):
        """Lower priority: Only some users check the leaderboard."""
        # Update this path to match your actual leaderboard URL
        self.client.get("/leaderboard/") 

    @task(2)
    def view_profile(self):
        """Medium priority: Checking stats."""
        # Replace with a real valid profile path if needed
        self.client.get("/dashboard/")