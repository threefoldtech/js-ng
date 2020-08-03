from locust import HttpUser, task, between


class QuickstartUser(HttpUser):
    wait_time = between(5, 9)

    @task
    def index_page(self):
        self.client.get("https://localhost/admin/#/", verify=False)
        # self.client.get("/world")

    @task
    def list_alerts(self):
        self.client.post("https://localhost/admin/actors/alerts/list_alerts", verify=False)

    @task
    def list_alerts_gedis(self):
        self.client.post("http://localhost:8000/admin/alerts/list_alerts", verify=False)

    # @task(3)
    # def view_item(self):
    #     item_id = random.randint(1, 10000)
    #     self.client.get(f"/item?id={item_id}", name="/item")

    # def on_start(self):
    #     print("test start")
    #     # self.client.post("/login", {"username": "foo", "password": "bar"})
