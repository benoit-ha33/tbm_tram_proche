import logging
from datetime import timedelta

from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.core import HomeAssistant

from .api import TBMApi, distance_m, minutes_until, delay_minutes, walking_minutes
from .const import TRAM_COLORS, TRAM_LINE_MAPPING, MAX_DISTANCE_METERS

_LOGGER = logging.getLogger(__name__)


class TBMCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant):
        super().__init__(
            hass,
            _LOGGER,
            name="TBM Tram Proche",
            update_interval=timedelta(seconds=60),
        )
        self.api = TBMApi(async_get_clientsession(hass))

    async def _async_update_data(self):
        latitude = self.hass.config.latitude
        longitude = self.hass.config.longitude

        stops_raw = await self.api.get_stop_points()
        stops = self._extract_stops(stops_raw)

        for stop in stops:
            stop["distance"] = round(
                distance_m(latitude, longitude, stop["lat"], stop["lon"])
            )

        nearby_stops = [
            stop
            for stop in sorted(stops, key=lambda stop: stop["distance"])
            if stop["distance"] <= MAX_DISTANCE_METERS
        ]

        alerts_raw = None

        try:
            alerts_raw = await self.api.get_general_messages()
            _LOGGER.warning("TBM DEBUG ALERTS RAW: %s", alerts_raw)
        except Exception as error:
            _LOGGER.warning("TBM DEBUG ALERTS ERROR: %s", error)

        for stop in nearby_stops:
            monitoring_ref = stop.get("area_ref") or stop.get("ref")
            monitoring_raw = await self.api.get_stop_monitoring(monitoring_ref)
            departures = self._extract_departures(monitoring_raw)

            if departures:
                stop["monitoring_ref"] = monitoring_ref

                distance = stop["distance"]

                return {
                    "status": "OK",
                    "nearest_stop": stop,
                    "distance": distance,
                    "walking_minutes": walking_minutes(distance),
                    "departures": departures,
                    "alerts_raw": alerts_raw,
                }

        nearest = nearby_stops[0] if nearby_stops else None
        distance = nearest["distance"] if nearest else None

        return {
            "status": "Aucun passage trouvé",
            "nearest_stop": nearest,
            "distance": distance,
            "walking_minutes": walking_minutes(distance),
            "departures": [],
            "alerts_raw": alerts_raw,
        }

    def _extract_stops(self, data):
        results = []

        def get_value(value):
            if isinstance(value, dict):
                return value.get("value") or value.get("Value")
            return value

        def walk(obj):
            if isinstance(obj, dict):
                if "StopPointRef" in obj and "Location" in obj:
                    loc = obj.get("Location", {})

                    lat = loc.get("latitude") or loc.get("Latitude")
                    lon = loc.get("longitude") or loc.get("Longitude")

                    stop_ref = get_value(obj.get("StopPointRef"))
                    area_ref = get_value(obj.get("StopAreaRef"))
                    stop_name = get_value(obj.get("StopName")) or "Arrêt inconnu"

                    lines_raw = obj.get("Lines", [])
                    lines = []

                    if isinstance(lines_raw, list):
                        for line in lines_raw:
                            line_value = get_value(line)

                            if line_value:
                                parts = str(line_value).split(":")
                                raw_line = parts[-2] if len(parts) >= 3 else str(line_value)
                                lines.append(TRAM_LINE_MAPPING.get(raw_line, raw_line))

                    if lat is not None and lon is not None and stop_ref:
                        results.append(
                            {
                                "ref": stop_ref,
                                "area_ref": area_ref,
                                "name": stop_name,
                                "lat": float(lat),
                                "lon": float(lon),
                                "lines": lines,
                            }
                        )

                for value in obj.values():
                    walk(value)

            elif isinstance(obj, list):
                for item in obj:
                    walk(item)

        walk(data)
        return results

    def _extract_departures(self, data):
        visits = []

        def get_value(value):
            if isinstance(value, dict):
                return value.get("value") or value.get("Value")

            if isinstance(value, list) and value:
                return get_value(value[0])

            return value

        def walk(obj):
            if isinstance(obj, dict):
                if "MonitoredVehicleJourney" in obj:
                    journey = obj["MonitoredVehicleJourney"]
                    call = journey.get("MonitoredCall", {})

                    line_ref = get_value(journey.get("LineRef")) or ""
                    parts = str(line_ref).split(":")
                    raw_line = parts[-2] if len(parts) >= 3 else str(line_ref)
                    line = TRAM_LINE_MAPPING.get(raw_line, raw_line)

                    destination = (
                        get_value(journey.get("DestinationName"))
                        or "Destination inconnue"
                    )

                    aimed = (
                        get_value(call.get("AimedDepartureTime"))
                        or get_value(call.get("AimedArrivalTime"))
                    )

                    expected = (
                        get_value(call.get("ExpectedDepartureTime"))
                        or get_value(call.get("ExpectedArrivalTime"))
                        or aimed
                    )

                    departure_status = (
                        get_value(call.get("DepartureStatus"))
                        or get_value(call.get("ArrivalStatus"))
                        or ""
                    )

                    cancellation = (
                        get_value(call.get("Cancellation"))
                        or get_value(call.get("Cancelled"))
                        or False
                    )

                    minutes = minutes_until(expected)
                    delay = delay_minutes(aimed, expected)

                    cancelled = str(cancellation).lower() == "true" or str(
                        departure_status
                    ).lower() in ["cancelled", "canceled"]

                    if minutes is not None:
                        visits.append(
                            {
                                "line": line,
                                "raw_line": raw_line,
                                "destination": destination,
                                "minutes": minutes,
                                "delay": delay,
                                "status": departure_status,
                                "cancelled": cancelled,
                                "aimed_time": aimed,
                                "expected_time": expected,
                                "color": TRAM_COLORS.get(line, "#FFFFFF"),
                            }
                        )

                for value in obj.values():
                    walk(value)

            elif isinstance(obj, list):
                for item in obj:
                    walk(item)

        walk(data)
        visits.sort(key=lambda x: x["minutes"])
        return visits