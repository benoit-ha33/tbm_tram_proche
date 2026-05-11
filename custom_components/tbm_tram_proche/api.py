import math
from datetime import datetime, timezone
import aiohttp

ACCOUNT_KEY = "opendata-bordeaux-metropole-flux-gtfs-rt"
BASE_URL = "https://bdx.mecatran.com/utw/ws/siri/2.0/bordeaux"


class TBMApi:
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session

    async def fetch_json(self, endpoint: str, params: dict | None = None):
        params = params or {}
        params["AccountKey"] = ACCOUNT_KEY

        async with self.session.get(
            f"{BASE_URL}/{endpoint}.json",
            params=params,
            headers={"Accept": "application/json"},
            timeout=20,
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def get_stop_points(self):
        return await self.fetch_json("stoppoints-discovery")

    async def get_stop_monitoring(self, stop_ref: str):
        return await self.fetch_json(
            "stop-monitoring",
            {
                "MonitoringRef": stop_ref,
                "PreviewInterval": "PT60M"            },
        )

    async def get_general_messages(self):
        return await self.fetch_json("general-message")


def distance_m(lat1, lon1, lat2, lon2):
    radius = 6371000
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)

    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def walking_minutes(distance):
    if distance is None:
        return None

    return max(1, round(distance / 80))


def parse_iso_datetime(value: str | None):
    if not value:
        return None

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def minutes_until(value: str | None):
    dt = parse_iso_datetime(value)

    if not dt:
        return None

    now = datetime.now(timezone.utc)
    delta = dt.astimezone(timezone.utc) - now

    return max(0, round(delta.total_seconds() / 60))


def delay_minutes(aimed: str | None, expected: str | None):
    aimed_dt = parse_iso_datetime(aimed)
    expected_dt = parse_iso_datetime(expected)

    if not aimed_dt or not expected_dt:
        return 0

    delay = expected_dt.astimezone(timezone.utc) - aimed_dt.astimezone(timezone.utc)

    return max(0, round(delay.total_seconds() / 60))