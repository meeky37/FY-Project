import random
from locust import HttpUser, task, between

# Defining sets of API parameters, so we can be realistic and vary the requests like real users.
entity_ids = [2, 4, 42, 482, 664, 169, 1371, 83, 53, 143, 2, 1371, 320, 143, 33]
entity_article_id_pairs = [(169, 22376), (1195, 2211), (241, 1958), (1371, 21099), (2, 26162),
                           (143, 21276), (53, 498), (83, 177)]
start_end_days = [(0, 14), (14, 180)]


class ProminentProfilesUser(HttpUser):
    wait_time = between(5, 15)  # Time between HTTP requests

    @task
    def visit_home_page(self):
        self.client.get("/")

    @task
    def visit_about_page(self):
        self.client.get("/about")

    @task
    def visit_reset_password_page(self):
        self.client.get("/reset-password")

    @task
    def visit_sign_up_page(self):
        self.client.get("/sign-up")

    @task
    def visit_menu_page(self):
        self.client.get("/menu")

    @task
    def visit_entity_page(self):
        entity_id = random.choice(entity_ids)
        self.client.get(f"/entity/{entity_id}")

    @task
    def visit_article_page(self):
        """Simulates visiting Article View"""
        article_id = random.choice(entity_article_id_pairs)
        self.client.get(f"/article/{article_id[0]}/{article_id[1]}")

    # API Load Test Calls
    @task
    def overall_sentiments_api(self):
        """Simulates visiting Entity View"""
        entity_id = random.choice(entity_ids)
        days = random.choice(start_end_days)
        self.client.get(f"/django/profiles_app/overall_sentiments/exp/"
                        f"{entity_id}/?endDay={days[1]}&startDay={days[0]}")

    @task
    def entity_dropdown_population_api(self):
        """Simulates population of dropdown"""
        self.client.get(f"/django/profiles_app/entities")

    @task
    def entity_name_api(self):
        entity_id = random.choice(entity_ids)
        self.client.get(f"/django/profiles_app/entity_name/{entity_id}/")

    @task
    def trending_entities_api(self):
        """Simulates visiting Home View"""
        self.client.get(f"/django/profiles_app/get_trending_entities/")

    @task
    def bing_entity_name_api(self):
        entity_id = random.choice(entity_ids)
        self.client.get(f"/django/profiles_app/bing_entities/mini/{entity_id}/")
