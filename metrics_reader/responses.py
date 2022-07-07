from typing import Optional


def bracelet_not_found(bracelet_id: Optional[str]) -> dict:
    return dict(
        statusCode=404,
        headers={
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET"
        },
        body=f"Bracelet not found ({bracelet_id})"
    )
