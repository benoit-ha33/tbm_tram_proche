from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

DOMAIN = "tbm_tram_proche"


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            TBMNearestStopSensor(coordinator),
            TBMDistanceSensor(coordinator),
            TBMAllDeparturesSensor(coordinator),
            TBMIphoneSummarySensor(coordinator),
        ]
    )


class TBMNearestStopSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "TBM Arrêt tram proche"
        self._attr_unique_id = "tbm_tram_proche_nearest_stop"
        self._attr_icon = "mdi:tram"

    @property
    def native_value(self):
        stop = self.coordinator.data.get("nearest_stop")
        return stop["name"] if stop else None

    @property
    def extra_state_attributes(self):
        return self.coordinator.data.get("nearest_stop") or {}


class TBMDistanceSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "TBM Distance arrêt tram"
        self._attr_unique_id = "tbm_tram_proche_distance"
        self._attr_native_unit_of_measurement = "m"
        self._attr_icon = "mdi:map-marker-distance"

    @property
    def native_value(self):
        return self.coordinator.data.get("distance")


class TBMAllDeparturesSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "TBM Prochains passages"
        self._attr_unique_id = "tbm_tram_proche_all_departures"
        self._attr_icon = "mdi:tram"

    @property
    def entity_picture(self):
        return "/local/tbm_tram_proche_images/tbm_logo.png"

    def _grouped_destinations(self):
        departures = self.coordinator.data.get("departures", [])
        grouped = []

        for departure in departures:
            key = f"{departure.get('line')}|{departure.get('destination')}"
            existing = next((item for item in grouped if item["key"] == key), None)

            departure_item = {
                "minutes": departure.get("minutes"),
                "delay": departure.get("delay"),
                "status": departure.get("status"),
                "cancelled": departure.get("cancelled"),
                "expected_time": departure.get("expected_time"),
                "aimed_time": departure.get("aimed_time"),
                "is_last": False,
            }

            if existing:
                existing["times"].append(departure_item)
            else:
                grouped.append(
                    {
                        "key": key,
                        "line": departure.get("line"),
                        "destination": departure.get("destination"),
                        "color": departure.get("color"),
                        "times": [departure_item],
                    }
                )

        for item in grouped:
            item["times"] = item["times"][:3]

        return grouped

    @property
    def native_value(self):
        return len(self._grouped_destinations())

    @property
    def extra_state_attributes(self):
        return {
            "departures": self._grouped_destinations(),
            "stop": self.coordinator.data.get("nearest_stop", {}).get("name"),
            "distance": self.coordinator.data.get("distance"),
            "walking_minutes": self.coordinator.data.get("walking_minutes"),
            "alerts_raw": self.coordinator.data.get("alerts_raw"),
        }


class TBMIphoneSummarySensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)

        self._attr_name = "TBM Résumé iPhone"
        self._attr_unique_id = "tbm_tram_proche_iphone_summary"
        self._attr_icon = "mdi:cellphone"

    def _grouped_departures(self):
        departures = self.coordinator.data.get("departures", [])
        grouped = []

        for departure in departures:
            line = departure.get("line")
            destination = departure.get("destination")
            minutes = departure.get("minutes")
            delay = departure.get("delay") or 0
            cancelled = departure.get("cancelled")

            if minutes is None:
                continue

            key = f"{line}-{destination}"
            existing = next((item for item in grouped if item["key"] == key), None)

            if cancelled:
                time_label = "Annulé"
            else:
                time_label = "Approche" if minutes <= 2 else f"{minutes}m"

                if delay >= 2:
                    time_label += f"+{delay}"

            if existing:
                existing["times"].append(time_label)
            else:
                grouped.append(
                    {
                        "key": key,
                        "line": line,
                        "destination": destination,
                        "times": [time_label],
                    }
                )

        return grouped[:2]

    @property
    def native_value(self):
        grouped = self._grouped_departures()

        if not grouped:
            return "Aucun tram"

        first = grouped[0]
        times = " / ".join(first["times"][:2])

        return f"{first['line']} {first['destination']} · {times}"

    @property
    def extra_state_attributes(self):
        stop = self.coordinator.data.get("nearest_stop", {}).get("name")
        distance = self.coordinator.data.get("distance")
        walking = self.coordinator.data.get("walking_minutes")
        grouped = self._grouped_departures()

        line_1 = ""
        line_2 = ""

        if len(grouped) >= 1:
            first = grouped[0]
            line_1 = f"{first['line']} {first['destination']} · {' / '.join(first['times'][:2])}"

        if len(grouped) >= 2:
            second = grouped[1]
            line_2 = f"{second['line']} {second['destination']} · {' / '.join(second['times'][:2])}"

        return {
            "stop": stop,
            "distance": distance,
            "walking_minutes": walking,
            "line_1": line_1,
            "line_2": line_2,
        }