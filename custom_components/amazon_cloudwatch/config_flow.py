"""Config flow for Amazon CloudWatch integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, SUPPORTED_REGIONS

import boto3
import botocore

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("aws_region"): vol.In(SUPPORTED_REGIONS),
        vol.Required("aws_access_key_id"): str,
        vol.Required("aws_secret_access_key"): str,
    }
)

def check_aws_credentials(region, access_key_id, secret_access_key):
    sts_client = boto3.client('sts',
                              region_name=region,
                              aws_access_key_id=access_key_id,
                              aws_secret_access_key=secret_access_key)
    return sts_client.get_caller_identity()


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # This only checks that the credentials are valid, not that they
    # can write to CloudWatch

    try:
        caller = await hass.async_add_executor_job(check_aws_credentials,
                                                   data["aws_region"],
                                                   data["aws_access_key_id"],
                                                   data["aws_secret_access_key"])
    except botocore.exceptions.ClientError:
        raise InvalidAuth

    # Return info that you want to store in the config entry.
    arn = caller["Arn"]
    return {"title": f"Amazon CloudWatch {arn}"}



class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Amazon CloudWatch."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
