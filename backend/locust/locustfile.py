"""
Locust load tests for the Planting Optimisation Tool API.

Setup:
    cd backend
    just run-api
    just seed-users
    just load-test

Open http://localhost:8089 to configure and start the test.
Recommended starting config: 10 users, ramp-up 2/s.

Two user classes are defined:
    MixedWorkloadUser     - broad coverage of all read endpoints across roles
    HeavyConcurrentUser   - hammers the two most expensive bulk endpoints
                            simultaneously to stress test DB locking under load

Rate limiting:
    Recommendation and reporting endpoints are limited to 10 req/min per user
    (keyed by JWT sub). With 10 test users each holding a distinct JWT, the
    effective ceiling is 100 req/min before limits kick in. If 429s appear,
    reduce users or increase wait_time below.
"""

import random
import threading

from locust import HttpUser, between, task

# Credentials are created by seed_users.py. Each user picks one in round-robin order
# so concurrent users hold distinct JWTs and hit separate rate-limit buckets.
_USERS = [{"email": f"loadtest_{i:02d}@test.com", "password": "Loadtest123!"} for i in range(1, 11)]
_pool_lock = threading.Lock()
_pool_index = 0


def _next_credentials() -> dict:
    global _pool_index
    with _pool_lock:
        creds = _USERS[_pool_index % len(_USERS)]
        _pool_index += 1
    return creds


# Farm IDs present after `just populate`. IDs are not guaranteed sequential but
# random sampling across this range rarely misses; 404s are visible in Locust stats.
_FARM_ID_RANGE = range(1, 3203)


def _login(client, creds: dict) -> str | None:
    with client.post(
        "/auth/token",
        data={"username": creds["email"], "password": creds["password"]},
        catch_response=True,
        name="/auth/token (setup)",
    ) as resp:
        if resp.status_code == 200:
            return resp.json()["access_token"]
        resp.failure(f"Login failed {resp.status_code}: {resp.text}")
        return None


class MixedWorkloadUser(HttpUser):
    """
    Broad coverage of all read endpoints. Simulates the typical mix of officer
    and supervisor traffic across recommendations, reports, reference data, and
    admin operations.
    """

    wait_time = between(1, 5)

    def on_start(self):
        token = _login(self.client, _next_credentials())
        if not token:
            self.environment.runner.quit()
            return
        self.headers = {"Authorization": f"Bearer {token}"}
        self._farm_sample = random.sample(list(_FARM_ID_RANGE), 50)

        # Fetch species list once for use in tasks
        resp = self.client.get("/species/dropdown", headers=self.headers, name="/species/dropdown (setup)")
        self._species = [s["id"] for s in resp.json()] if resp.status_code == 200 else [1]

        # Fetch user list once to get a valid user ID
        resp = self.client.get("/users/", headers=self.headers, name="/users/ (setup)")
        self._user_ids = [u["id"] for u in resp.json()] if resp.status_code == 200 else [1]

    def _farm_id(self) -> int:
        return random.choice(self._farm_sample)

    @task(5)
    def get_single_recommendation(self):
        """Single farm recommendation - tests Redis cache on repeated hits."""
        self.client.get(
            f"/recommendations/{self._farm_id()}",
            headers=self.headers,
            name="/recommendations/[farm_id]",
        )

    @task(3)
    def get_sapling_estimation(self):
        """Sapling count for a farm - cached after first hit."""
        self.client.get(
            f"/sapling_estimation/{self._farm_id()}",
            headers=self.headers,
            name="/sapling_estimation/[farm_id]",
        )

    @task(2)
    def get_batch_recommendations(self):
        """10-farm batch recommendation run."""
        farm_ids = random.sample(self._farm_sample, 10)
        self.client.post(
            "/recommendations/batch",
            json=farm_ids,
            headers=self.headers,
            name="/recommendations/batch (10 farms)",
        )

    @task(2)
    def get_single_farm_report(self):
        """Single farm report - DB read of saved recommendations."""
        self.client.get(
            f"/reports/farm/{self._farm_id()}",
            headers=self.headers,
            name="/reports/farm/[farm_id]",
        )

    @task(2)
    def get_farm(self):
        """Single farm lookup."""
        self.client.get(
            f"/farms/{self._farm_id()}",
            headers=self.headers,
            name="/farms/[farm_id]",
        )

    @task(2)
    def get_current_user(self):
        """Token verification - runs get_current_user dependency."""
        self.client.get("/auth/users/me", headers=self.headers)

    @task(2)
    def get_farm_profile(self):
        """Environmental profile - first hit calls GEE, subsequent hits served from cache."""
        self.client.get(
            f"/profile/{self._farm_id()}",
            headers=self.headers,
            name="/profile/[farm_id]",
        )

    @task(1)
    def get_soil_textures(self):
        """Reference data lookup."""
        self.client.get("/soil-textures", headers=self.headers)

    @task(1)
    def get_all_farms_report(self):
        """All-farms JSON report - bulk DB read."""
        self.client.get("/reports/farms", headers=self.headers)

    @task(1)
    def get_users(self):
        """User list - admin read."""
        self.client.get("/users/", headers=self.headers)


class HeavyConcurrentUser(HttpUser):
    """
    Hammers the most expensive bulk endpoints back-to-back. Use a small number
    of these (2-3) alongside MixedWorkloadUser to simulate concurrent heavy
    processes contending on the DB.
    """

    wait_time = between(0.5, 2)

    def on_start(self):
        token = _login(self.client, _next_credentials())
        if not token:
            self.environment.runner.quit()
            return
        self.headers = {"Authorization": f"Bearer {token}"}
        self._farm_sample = random.sample(list(_FARM_ID_RANGE), 100)

        # Fetch feature count to build a valid AHP matrix
        resp = self.client.get("/species/features", headers=self.headers, name="/species/features (setup)")
        feature_count = len(resp.json()) if resp.status_code == 200 else 2
        self._ahp_matrix = [[1.0] * feature_count for _ in range(feature_count)]

        resp = self.client.get("/species/dropdown", headers=self.headers, name="/species/dropdown (setup)")
        self._species_ids = [s["id"] for s in resp.json()] if resp.status_code == 200 else [1]

    @task(3)
    def batch_recommendations_large(self):
        """25-farm batch - the most CPU/DB intensive single request in the system."""
        farm_ids = random.sample(self._farm_sample, 25)
        self.client.post(
            "/recommendations/batch",
            json=farm_ids,
            headers=self.headers,
            name="/recommendations/batch (25 farms)",
        )

    @task(1)
    def all_farms_report(self):
        """All-farms report JSON - run concurrently with batch recs to surface DB locking."""
        self.client.get("/reports/farms", headers=self.headers)

    @task(1)
    def all_farms_report_pdf(self):
        """All-farms PDF export - adds document generation overhead on top of DB load."""
        self.client.get("/reports/farms/export/pdf", headers=self.headers)

    @task(1)
    def ahp_calculate(self):
        """AHP weight calculation - admin computation, run under concurrent load."""
        self.client.post(
            "/ahp/calculate-and-save",
            json={"species_id": random.choice(self._species_ids), "matrix": self._ahp_matrix},
            headers=self.headers,
            name="/ahp/calculate-and-save",
        )
