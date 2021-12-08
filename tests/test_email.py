from chalice.test import Client
from app import app

def test_notify():
    with Client(app, stage_name="x") as client:
        response = client.lambda_.invoke(
            "notify",
            client.events.generate_cw_event(
                source="",
                detail_type="",
                detail="",
                resources=""
            ),
        )
        print(response.payload)

        assert isinstance(response.payload, str)
