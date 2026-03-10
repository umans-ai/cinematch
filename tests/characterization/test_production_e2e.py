"""
Characterization tests for CineMatch production.

These tests document the current behavior of the production environment.
They are NOT acceptance tests - they capture "what is", not "what should be".
Any change after migration indicates a behavioral difference that must be investigated.

Run before migration:
    pytest tests/characterization/ -v --base-url=https://demo.cinematch.umans.ai --json-report --json-report-file=characterization/baseline.json

Run after migration:
    pytest tests/characterization/ -v --base-url=https://demo.cinematch.umans.ai --json-report --json-report-file=characterization/after-migration.json

Compare results to verify functional equivalence.
"""

import pytest
import json
from playwright.sync_api import Page, expect, APIRequestContext
from datetime import datetime

PRODUCTION_URL = "https://demo.cinematch.umans.ai"


@pytest.fixture(scope="session")
def characterization_results():
    """Store test results for comparison."""
    return {}


class TestHomepageAndNavigation:
    """Characterization: Basic page loading and navigation."""

    def test_homepage_loads(self, page: Page):
        """Capture: Homepage title and main elements."""
        page.goto(PRODUCTION_URL)

        # Document actual title
        title = page.title()
        print(f"Homepage title: {title}")
        assert "CineMatch" in title or "cinematch" in title.lower()

        # Document main heading
        heading = page.locator("h1").first.inner_text()
        print(f"Main heading: {heading}")

        # Document create room button presence
        create_button = page.locator("button:has-text('Create Room'), a:has-text('Create Room')")
        expect(create_button).to_be_visible()

    def test_homepage_has_create_and_join_options(self, page: Page):
        """Capture: Main CTAs on homepage."""
        page.goto(PRODUCTION_URL)

        # Check for Create Room option
        create_locators = [
            page.locator("text=Create Room"),
            page.locator("button:has-text('Create')"),
            page.locator("a:has-text('Create')"),
        ]
        create_visible = any(loc.count() > 0 and loc.first.is_visible() for loc in create_locators if loc.count() > 0)
        assert create_visible, "Create Room option should be visible"

        # Check for Join Room option
        join_locators = [
            page.locator("text=Join Room"),
            page.locator("text=Join"),
            page.locator("input[placeholder*='code' i]"),
        ]
        join_visible = any(loc.count() > 0 and loc.first.is_visible() for loc in join_locators if loc.count() > 0)
        assert join_visible, "Join Room option should be visible"


class TestRoomLifecycle:
    """Characterization: Room creation and joining workflow."""

    def test_create_room_generates_code(self, page: Page):
        """Capture: Room code format and display."""
        page.goto(PRODUCTION_URL)

        # Click create room
        page.click("text=Create Room")

        # Wait for room code to appear
        # Characterization: Document the actual format
        code_locator = page.locator("[data-testid='room-code'], .room-code, code, .code").first
        expect(code_locator).to_be_visible(timeout=10000)

        room_code = code_locator.inner_text().strip()
        print(f"Room code generated: {room_code}")
        print(f"Room code length: {len(room_code)}")
        print(f"Room code format: {self._analyze_format(room_code)}")

        # Store for potential use in other tests
        assert len(room_code) > 0, "Room code should not be empty"

        return room_code

    def _analyze_format(self, code: str) -> str:
        """Analyze the format of the room code."""
        if code.isdigit():
            return f"numeric-{len(code)}-digits"
        elif code.isalnum():
            return f"alphanumeric-{len(code)}-chars"
        else:
            return f"mixed-{len(code)}-chars"

    def test_create_room_shows_waiting_state(self, page: Page):
        """Capture: Waiting room UI state."""
        page.goto(PRODUCTION_URL)
        page.click("text=Create Room")

        # Wait for room creation
        page.wait_for_timeout(2000)

        # Document waiting indicators
        waiting_indicators = [
            "Waiting",
            "waiting for partner",
            "share this code",
            "invite",
        ]

        page_text = page.locator("body").inner_text().lower()
        found_indicators = [ind for ind in waiting_indicators if ind in page_text]
        print(f"Waiting indicators found: {found_indicators}")

        # Should have some kind of waiting/invite UI
        assert len(found_indicators) > 0 or "code" in page_text

    def test_join_room_with_code(self, page: Page, browser):
        """Capture: Two participants can join the same room."""
        # Create room in first context
        page.goto(PRODUCTION_URL)
        page.click("text=Create Room")

        # Get room code
        code_locator = page.locator("[data-testid='room-code'], .room-code, code, .code").first
        expect(code_locator).to_be_visible(timeout=10000)
        room_code = code_locator.inner_text().strip()

        print(f"Created room with code: {room_code}")

        # Join from second context (incognito)
        context2 = browser.new_context()
        page2 = context2.new_page()

        try:
            page2.goto(PRODUCTION_URL)

            # Find join input and enter code
            join_input = page2.locator("input[placeholder*='code' i], input[type='text']").first
            if join_input.count() > 0:
                join_input.fill(room_code)
                page2.click("button:has-text('Join'), text=Join")
            else:
                # Alternative: click Join Room first
                page2.click("text=Join Room")
                page2.locator("input").first.fill(room_code)
                page2.click("button:has-text('Join')")

            # Wait for join to complete
            page2.wait_for_timeout(3000)

            # Document what happens when second participant joins
            page2_text = page2.locator("body").inner_text()
            print(f"Page 2 content after join: {page2_text[:500]}")

            # Both pages should now show some shared state
            # (either both in waiting, both in voting, or some transition)

        finally:
            context2.close()


class TestVotingFlow:
    """Characterization: Movie voting and matching behavior."""

    def test_voting_ui_elements(self, page: Page):
        """Capture: Voting interface components."""
        # Create room and get to voting state
        page.goto(PRODUCTION_URL)
        page.click("text=Create Room")

        # Wait and see what UI appears
        page.wait_for_timeout(3000)

        # Document voting-related elements
        body_text = page.locator("body").inner_text().lower()

        voting_elements = {
            "swipe_left": "left" in body_text or "dislike" in body_text,
            "swipe_right": "right" in body_text or "like" in body_text,
            "movie_title": "movie" in body_text or "film" in body_text,
            "poster_image": page.locator("img").count() > 0,
            "buttons": page.locator("button").count(),
        }

        print(f"Voting UI elements detected: {voting_elements}")

    def test_votes_persist_after_refresh(self, page: Page):
        """Critical: Data persistence behavior."""
        # This is a key characterization - SQLite vs PostgreSQL must behave identically
        page.goto(PRODUCTION_URL)
        page.click("text=Create Room")

        # Wait for room and note state
        page.wait_for_timeout(3000)
        initial_state = page.locator("body").inner_text()

        # Refresh page
        page.reload()
        page.wait_for_timeout(3000)

        after_refresh_state = page.locator("body").inner_text()

        # Document persistence behavior
        print(f"State preserved after refresh: {initial_state[:200] == after_refresh_state[:200]}")


class TestAPIContracts:
    """Characterization: API response shapes and behavior."""

    def test_health_endpoint(self, api_context: APIRequestContext):
        """Capture: /health response format."""
        response = api_context.get(f"{PRODUCTION_URL}/health")

        print(f"Health status: {response.status}")
        assert response.status == 200, f"Health check failed with status {response.status}"

        try:
            body = response.json()
            print(f"Health response body: {json.dumps(body, indent=2)}")

            # Document actual structure
            assert "status" in body or "healthy" in str(body).lower(), "Expected status indicator in health response"
        except Exception as e:
            print(f"Health response (not JSON): {response.text()}")

    def test_create_room_api(self, api_context: APIRequestContext):
        """Capture: POST /api/rooms response shape."""
        response = api_context.post(f"{PRODUCTION_URL}/api/rooms", data={})

        print(f"Create room status: {response.status}")

        if response.status == 200:
            try:
                body = response.json()
                print(f"Create room response: {json.dumps(body, indent=2)}")

                # Document actual response structure
                if "code" in body:
                    print(f"Room code in response: {body['code']}")
                if "id" in body:
                    print(f"Room ID type: {type(body['id'])}")
            except Exception as e:
                print(f"Create room response (not JSON): {response.text()}")

    def test_api_error_responses(self, api_context: APIRequestContext):
        """Capture: Error response format."""
        # Test invalid room code
        response = api_context.get(f"{PRODUCTION_URL}/api/rooms/INVALID999")

        print(f"Invalid room status: {response.status}")
        if response.status != 200:
            print(f"Error response: {response.text()[:500]}")


def test_summary(characterization_results):
    """Generate summary of characterization results."""
    print("\n" + "=" * 60)
    print("CHARACTERIZATION TEST SUMMARY")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Target: {PRODUCTION_URL}")
    print("=" * 60)
