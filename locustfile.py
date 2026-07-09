from locust import HttpUser, task, between

class CatalogueUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def view_catalog(self):
        """Simulate a user hitting the home page of the Streamlit catalog app."""
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0"
        }
        self.client.get("/", headers=headers)

    @task(1)
    def check_health(self):
        """Simulate browser or load-balancer checking app health."""
        self.client.get("/_stcore/health")
