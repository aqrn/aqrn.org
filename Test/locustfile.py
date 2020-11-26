import random as rnd

from locust import HttpUser, HttpLocust, TaskSet, task, between


class LoadTest(HttpUser):
    wait_time = between(1, 2)

    @task
    def try_zip(self):
        for i in range(10):
            zip = rnd.randint(10000, 99999)
            with self.client.get(f'/{zip}', catch_response=True, name='/[id]') as response:
                if response.status_code == 200:
                        response.success()
                else:
                    response.failure(f'status code is {response.status_code}')