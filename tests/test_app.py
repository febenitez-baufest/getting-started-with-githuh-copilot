from src.app import activities


def test_root_redirects_to_static_index(client):
    arrange_path = "/"

    act_response = client.get(arrange_path, follow_redirects=False)

    assert act_response.status_code in (302, 307)
    assert act_response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_structure(client):
    arrange_path = "/activities"

    act_response = client.get(arrange_path)
    assert_response_data = act_response.json()

    assert act_response.status_code == 200
    assert isinstance(assert_response_data, dict)
    assert len(assert_response_data) > 0
    first_activity = next(iter(assert_response_data.values()))
    assert "description" in first_activity
    assert "schedule" in first_activity
    assert "max_participants" in first_activity
    assert "participants" in first_activity


def test_signup_adds_participant(client):
    arrange_activity_name = "Chess Club"
    arrange_email = "new.student@mergington.edu"

    act_response = client.post(
        f"/activities/{arrange_activity_name}/signup",
        params={"email": arrange_email},
    )

    assert act_response.status_code == 200
    assert arrange_email in activities[arrange_activity_name]["participants"]


def test_signup_fails_when_activity_not_found(client):
    arrange_activity_name = "Nonexistent Club"
    arrange_email = "student@mergington.edu"

    act_response = client.post(
        f"/activities/{arrange_activity_name}/signup",
        params={"email": arrange_email},
    )

    assert act_response.status_code == 404
    assert act_response.json()["detail"] == "Activity not found"


def test_signup_fails_when_student_already_signed_up(client):
    arrange_activity_name = "Chess Club"
    arrange_email = "michael@mergington.edu"

    act_response = client.post(
        f"/activities/{arrange_activity_name}/signup",
        params={"email": arrange_email},
    )

    assert act_response.status_code == 400
    assert act_response.json()["detail"] == "Student already signed up for this activity"


def test_signup_fails_when_activity_is_full(client):
    arrange_activity_name = "Chess Club"
    arrange_activity = activities[arrange_activity_name]
    arrange_activity["participants"] = [
        f"student{index}@mergington.edu"
        for index in range(arrange_activity["max_participants"])
    ]
    arrange_email = "overflow.student@mergington.edu"

    act_response = client.post(
        f"/activities/{arrange_activity_name}/signup",
        params={"email": arrange_email},
    )

    assert act_response.status_code == 400
    assert act_response.json()["detail"] == "Activity is full"


def test_unregister_removes_existing_participant(client):
    arrange_activity_name = "Chess Club"
    arrange_email = "daniel@mergington.edu"

    act_response = client.delete(
        f"/activities/{arrange_activity_name}/participants",
        params={"email": arrange_email},
    )

    assert act_response.status_code == 200
    assert arrange_email not in activities[arrange_activity_name]["participants"]


def test_unregister_fails_when_activity_not_found(client):
    arrange_activity_name = "Unknown Club"
    arrange_email = "student@mergington.edu"

    act_response = client.delete(
        f"/activities/{arrange_activity_name}/participants",
        params={"email": arrange_email},
    )

    assert act_response.status_code == 404
    assert act_response.json()["detail"] == "Activity not found"


def test_unregister_fails_when_participant_not_signed_up(client):
    arrange_activity_name = "Chess Club"
    arrange_email = "not.signed@mergington.edu"

    act_response = client.delete(
        f"/activities/{arrange_activity_name}/participants",
        params={"email": arrange_email},
    )

    assert act_response.status_code == 404
    assert act_response.json()["detail"] == "Student not signed up for this activity"