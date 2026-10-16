import httpx
from config.settings import settings
from typing import List, Dict, Any


class IntervalsClient:
    def __init__(self):
        self.base_url = settings.INTERVALS_BASE_URL
        self.auth = ("API_KEY", settings.INTERVALS_API_KEY)
        self.athlete_id = settings.INTERVALS_ATHLETE_ID

    async def get_wellness(self, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Fetch wellness data for the specified date range."""
        url = f"{self.base_url}/athlete/{self.athlete_id}/wellness"
        params = {"oldest": start_date, "newest": end_date}

        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, auth=self.auth, params=params)
            response.raise_for_status()
            return response.json()


