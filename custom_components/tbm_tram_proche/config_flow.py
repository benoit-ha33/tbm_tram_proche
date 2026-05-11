import voluptuous as vol
from homeassistant import config_entries

class TBMTramProcheConfigFlow(config_entries.ConfigFlow, domain="tbm_tram_proche"):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        return self.async_create_entry(title="TBM Tram Proche", data={})
