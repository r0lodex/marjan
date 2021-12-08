from chalice.test import Client
from app import app

def test_send():
    with Client(app, stage_name="x") as client:
        response = client.lambda_.invoke(
            "send",
            client.events.generate_cw_event(
                source="",
                detail_type="",
                detail="",
                resources=""
            ),
        )
        print(response.payload)
        assert len(response.payload) > 1
