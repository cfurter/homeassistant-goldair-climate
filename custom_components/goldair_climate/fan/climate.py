"""
Goldair WiFi Fan device.
"""

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.components.climate.const import (
    ATTR_FAN_MODE,
    ATTR_HVAC_MODE,
    ATTR_PRESET_MODE,
    ATTR_SWING_MODE,
)
from homeassistant.const import ATTR_TEMPERATURE

from ..device import GoldairTuyaDevice
from .const import (
    ATTR_TIMER,
    COMPACT_FAN_MODES,
    COMPACT_PROPERTY_TO_DPS_ID,
    COMPACT_PRESET_MODE_TO_DPS_MODE,
    COMPACT_SWING_MODE_TO_DPS_MODE,
    FAN_MODES,
    HVAC_MODE_TO_DPS_MODE,
    PRESET_MODE_TO_DPS_MODE,
    PROPERTY_TO_DPS_ID,
    SWING_MODE_TO_DPS_MODE,
)

SUPPORT_FLAGS = (
    ClimateEntityFeature.FAN_MODE
    | ClimateEntityFeature.PRESET_MODE
    | ClimateEntityFeature.SWING_MODE
    | ClimateEntityFeature.TURN_ON
    | ClimateEntityFeature.TURN_OFF
)


class GoldairFan(ClimateEntity):
    """Representation of a Goldair WiFi fan."""

    def __init__(self, device):
        """Initialize the fan.
        Args:
            name (str): The device's name.
            device (GoldairTuyaDevice): The device API instance."""
        self._device = device

        self._support_flags = SUPPORT_FLAGS

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return self._support_flags

    @property
    def should_poll(self):
        """Return the polling state."""
        return True

    @property
    def name(self):
        """Return the name of the climate device."""
        return self._device.name

    @property
    def unique_id(self):
        """Return the unique id for this fan."""
        return self._device.unique_id

    @property
    def device_info(self):
        """Return device information about this fan."""
        return self._device.device_info

    @property
    def icon(self):
        """Return the icon to use in the frontend for this device."""
        return "mdi:fan"

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return self._device.temperature_unit

    @property
    def current_temperature(self):
        """Return the current temperature."""
        temperature = self._device.get_property(PROPERTY_TO_DPS_ID[ATTR_TEMPERATURE])
        if temperature is None:
            # This fan variant reports its temperature on DPS 19 instead of DPS 11.
            temperature = self._device.get_property("19")

        try:
            return float(temperature) if temperature is not None else None
        except (TypeError, ValueError):
            return None

    @property
    def available(self):
        """Return whether the device is currently reachable."""
        return self._device.get_property(PROPERTY_TO_DPS_ID[ATTR_HVAC_MODE]) is not None

    @property
    def hvac_mode(self):
        """Return current HVAC mode, ie Fan Only or Off."""
        dps_mode = self._device.get_property(PROPERTY_TO_DPS_ID[ATTR_HVAC_MODE])

        if dps_mode is not None:
            return GoldairTuyaDevice.get_key_for_value(HVAC_MODE_TO_DPS_MODE, dps_mode)
        else:
            return None

    @property
    def hvac_modes(self):
        """Return the list of available HVAC modes."""
        return list(HVAC_MODE_TO_DPS_MODE.keys())

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new HVAC mode."""
        dps_mode = HVAC_MODE_TO_DPS_MODE[hvac_mode]
        await self._device.async_set_property(
            PROPERTY_TO_DPS_ID[ATTR_HVAC_MODE], dps_mode
        )

    async def async_turn_on(self):
        """Turn the fan on."""
        await self.async_set_hvac_mode(HVACMode.FAN_ONLY)

    async def async_turn_off(self):
        """Turn the fan off."""
        await self.async_set_hvac_mode(HVACMode.OFF)

    @property
    def preset_mode(self):
        """Return current preset mode, ie Comfort, Eco, Anti-freeze."""
        preset_modes = (
            COMPACT_PRESET_MODE_TO_DPS_MODE
            if self._is_compact_fan
            else PRESET_MODE_TO_DPS_MODE
        )
        preset_dps_id = (
            PROPERTY_TO_DPS_ID[ATTR_FAN_MODE]
            if self._is_compact_fan
            else PROPERTY_TO_DPS_ID[ATTR_PRESET_MODE]
        )
        dps_mode = self._device.get_property(preset_dps_id)
        if dps_mode is not None:
            return GoldairTuyaDevice.get_key_for_value(
                preset_modes, dps_mode
            )
        else:
            return None

    @property
    def preset_modes(self):
        """Return the list of available preset modes."""
        if self._is_compact_fan:
            return list(COMPACT_PRESET_MODE_TO_DPS_MODE.keys())
        return list(PRESET_MODE_TO_DPS_MODE.keys())

    async def async_set_preset_mode(self, preset_mode):
        """Set new preset mode."""
        preset_modes = (
            COMPACT_PRESET_MODE_TO_DPS_MODE
            if self._is_compact_fan
            else PRESET_MODE_TO_DPS_MODE
        )
        preset_dps_id = (
            PROPERTY_TO_DPS_ID[ATTR_FAN_MODE]
            if self._is_compact_fan
            else PROPERTY_TO_DPS_ID[ATTR_PRESET_MODE]
        )
        dps_mode = preset_modes[preset_mode]
        await self._device.async_set_property(
            preset_dps_id, dps_mode
        )

    @property
    def swing_mode(self):
        """Return current swing mode: horizontal or off"""
        swing_modes = (
            COMPACT_SWING_MODE_TO_DPS_MODE
            if self._is_compact_fan
            else SWING_MODE_TO_DPS_MODE
        )
        swing_dps_id = (
            COMPACT_PROPERTY_TO_DPS_ID[ATTR_SWING_MODE]
            if self._is_compact_fan
            else PROPERTY_TO_DPS_ID[ATTR_SWING_MODE]
        )
        dps_mode = self._device.get_property(swing_dps_id)
        if dps_mode is not None:
            return GoldairTuyaDevice.get_key_for_value(swing_modes, dps_mode)
        else:
            return None

    @property
    def swing_modes(self):
        """Return the list of available swing modes."""
        if self._is_compact_fan:
            return list(COMPACT_SWING_MODE_TO_DPS_MODE.keys())
        return list(SWING_MODE_TO_DPS_MODE.keys())

    async def async_set_swing_mode(self, swing_mode):
        """Set new swing mode."""
        swing_modes = (
            COMPACT_SWING_MODE_TO_DPS_MODE
            if self._is_compact_fan
            else SWING_MODE_TO_DPS_MODE
        )
        swing_dps_id = (
            COMPACT_PROPERTY_TO_DPS_ID[ATTR_SWING_MODE]
            if self._is_compact_fan
            else PROPERTY_TO_DPS_ID[ATTR_SWING_MODE]
        )
        dps_mode = swing_modes[swing_mode]
        await self._device.async_set_property(
            swing_dps_id, dps_mode
        )

    @property
    def extra_state_attributes(self):
        """Return device values not represented by the climate entity."""
        if self._is_compact_fan:
            return {
                ATTR_TIMER: self._device.get_property(
                    COMPACT_PROPERTY_TO_DPS_ID[ATTR_TIMER]
                )
            }
        return {}

    @property
    def fan_mode(self):
        """Return current fan mode: 1-12 or 1-3 depending on the preset"""
        fan_dps_id = (
            PROPERTY_TO_DPS_ID[ATTR_PRESET_MODE]
            if self._is_compact_fan
            else PROPERTY_TO_DPS_ID[ATTR_FAN_MODE]
        )
        dps_mode = self._device.get_property(fan_dps_id)
        if self._is_compact_fan and dps_mode in COMPACT_FAN_MODES.values():
            return GoldairTuyaDevice.get_key_for_value(COMPACT_FAN_MODES, dps_mode)
        if (
            dps_mode is not None
            and self.preset_mode is not None
            and dps_mode in FAN_MODES[self.preset_mode].values()
        ):
            return GoldairTuyaDevice.get_key_for_value(
                FAN_MODES[self.preset_mode], dps_mode
            )
        else:
            return None

    @property
    def fan_modes(self):
        """Return the list of available fan modes."""
        if self._is_compact_fan:
            return list(COMPACT_FAN_MODES.values())
        if self.preset_mode is not None:
            return list(FAN_MODES[self.preset_mode].keys())
        else:
            return []

    async def async_set_fan_mode(self, fan_mode):
        """Set new fan mode."""
        if self._is_compact_fan:
            dps_mode = COMPACT_FAN_MODES[str(fan_mode)]
            await self._device.async_set_property(
                PROPERTY_TO_DPS_ID[ATTR_PRESET_MODE], dps_mode
            )
        elif self.preset_mode is not None:
            dps_mode = FAN_MODES[self.preset_mode][int(fan_mode)]
            await self._device.async_set_property(
                PROPERTY_TO_DPS_ID[ATTR_FAN_MODE], dps_mode
            )
        else:
            raise ValueError("Fan mode can only be set when a preset mode is set")

    @property
    def _is_compact_fan(self):
        return (
            self._device.get_property("19") is not None
            and self._device.get_property(PROPERTY_TO_DPS_ID[ATTR_SWING_MODE]) is None
        )

    async def async_update(self):
        await self._device.async_refresh()
