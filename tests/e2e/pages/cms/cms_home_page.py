import json

from pages.base_page import BasePage


class CmsHomePage(BasePage):
    def is_loaded(self):
        response = self.page.request.get(f"{self.base_url}/api/contentstore/v1/home/courses")
        assert response.status == 200

    def create_course(self, name, org, number, run):
        cookies = {c['name']: c['value'] for c in self.page.context.cookies()}
        response = self.page.request.post(
            f"{self.base_url}/course/",
            json={"org": org, "number": number, "display_name": name, "run": run},
            headers={
                "Accept": "application/json",
                "X-CSRFToken": cookies.get("csrftoken", ""),
            }
        )
        data = response.json()
        self.page.goto(self.base_url + data['url'])
        self.page.wait_for_url('**/course/**')
