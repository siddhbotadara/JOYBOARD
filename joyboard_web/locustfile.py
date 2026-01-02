from locust import HttpUser, task, between

class JoyboardUser(HttpUser):
    # Simulate a user waiting 1 to 3 seconds between actions
    wait_time = between(1, 3)

    @task(1)
    def check_leaderboard(self):
        # Lower priority: Only some users check the leaderboard."""
        self.client.get("/leaderboard/") 

# Command - locust -f locustfile.py