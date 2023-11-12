# Amazon CloudWatch custom component for Home Assistant

A custom component which adds a service to report custom metric values to
Amazon CloudWatch from Home Assistant.

This was first built to get alerts _if Home Assistant crashes_ or
there is a power outage, but you can send any numeric data and create
alerts on them.

## Before you start

You'll need an 'Access Key ID' and a 'Secret Access Key' to set the
integration up. It's strongly recommended to create a user that can
only write to CloudWatch metrics, rather than using root account
credentials.

## Setup

First, install the custom integration using [HACS](https://hacs.xyz/):

1. Add the integration using HACS
1. Restart Home Assistant

[![Open your Home Assistant instance and open the CloudWatch custom component repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Mallonbacka&repository=custom-component-cloudwatch)

Then add a new integraion:

1. Go to **Settings**, then **Devices & Services**
1. Click **Add Integration**
1. Select 'Amazon CloudWatch' from the list
1. Enter your AWS region, access key ID and secret access key

## Usage

You can now report data to CloudWatch by calling the service, like this:

```
service: amazon_cloudwatch.put_metric_data
data:
  namespace: home_assistant
  metric_name: operational
  value: 1
```

This reports a single value of 1 to the metric named `operational`, in the
`home_assistant` namespace. This would be useful to get an alert if it's
not checked in for a number of minutes.

Using templates is also supported:

```
service: amazon_cloudwatch.put_metric_data
data:
  namespace: home_assistant
  metric_name: temperature
  value: "{{ state_attr("weather.forecast_home", "temperature") }}"
```

Here, the `temperature` attribute of the default `forecast_home` entity
is reported to a metric named `temperature`.

## Costs

The following is true at the time of writing, but check the [AWS Pricing
Calculator](https://calculator.aws/) for yourself to be sure.

Amazon CloudWatch has a free tier, but beyond this, the call used to record
the data is chargable. Take care to ensure you're not making too many
requests.

In most regions, one metric updated once per minute should cost around $0.75
per month, while updating every second increases this to $27.30 per month.

Alarms and notifications about the values are billed separately.

## Contributions, support, etc.

This was originally intended for personal use, but I'm happy to try and help
anyone who wants to use or extend it. Open an issue to discuss problems, wishes
or ideas.

## Credits

The scripts and GitHub workflows were taken from the [integration_blueprint](https://github.com/ludeeus/integration_blueprint) template.
