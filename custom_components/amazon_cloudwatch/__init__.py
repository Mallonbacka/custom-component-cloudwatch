"""The Amazon CloudWatch integration."""
from __future__ import annotations
import logging
import boto3

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def create_cloudwatch_client(entry: ConfigEntry):
   return boto3.client("cloudwatch",
                       region_name=entry.data["aws_region"],
                       aws_access_key_id=entry.data["aws_access_key_id"],
                       aws_secret_access_key=entry.data["aws_secret_access_key"])

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Amazon CloudWatch from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    service = await hass.async_add_executor_job(create_cloudwatch_client, entry)
    hass.data[DOMAIN][entry.entry_id] = service

    def put_metric_data(call: ServiceCall) -> None:
       payload = {
           "Namespace": call.data["namespace"],
           "MetricData": [{
               "MetricName": call.data["metric_name"],
               "Value": call.data["value"],
           }],
       }

       hass.data[DOMAIN][entry.entry_id].put_metric_data(**payload)

    hass.services.async_register(DOMAIN, "put_metric_data", put_metric_data)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, []):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
