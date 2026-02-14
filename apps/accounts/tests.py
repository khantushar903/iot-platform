from rest_framework.test import APITestCase


class AuthFlowTests(APITestCase):
    def test_register_login_me_flow(self):
        # Register
        res = self.client.post(
            "/api/accounts/register/",
            {"username": "testuser1", "password": "pass12345"},
            format="json",
        )
        self.assertEqual(res.status_code, 201)

        # Login (JWT)
        res = self.client.post(
            "/api/auth/login/",
            {"username": "testuser1", "password": "pass12345"},
            format="json",
        )
        self.assertEqual(res.status_code, 200)
        access = res.data.get("access")
        self.assertTrue(access)

        # Call protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        res = self.client.get("/api/accounts/me/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data["username"], "testuser1")

    def test_me_requires_auth(self):
        res = self.client.get("/api/accounts/me/")
        self.assertEqual(res.status_code, 401)
