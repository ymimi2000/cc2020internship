from locust import HttpLocust, TaskSet, task


class UserBehavior(TaskSet):

    @task(2)
    def index(self):
        self.client.get("/")

    @task(1)
    def profile(self):
        self.client.get("/forecast/?state=CA&region_type=state&region_id=CA")


class WebsiteUser(HttpLocust):

    task_set = UserBehavior
    min_wait = 5000
    max_wait = 15000
