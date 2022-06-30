from typing import Optional


def bracelet_not_found(bracelet_id: Optional[str]) -> dict:
    return dict(
        statusCode=404,
        body=f"Bracelet not found ({bracelet_id})"
    )
