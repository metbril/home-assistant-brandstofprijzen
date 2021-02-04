# United Consumers Brandstofprijzen for Home Assistant

Home Assistant component for fuel prices from [United Consumers](https://www.unitedconsumers.com/brandstofprijzen/).

## Installation

## HACS (Recommended)

HACS installation is not yet available, but it's on my TODO list.

## Manual

1. Copy directory `brandstofprijzen` to your `<config dir>/custom_components` directory.
2. Configure Home Assistant.
3. Restart Home Assistant.

Please note that you need to also manually update the component with newer versions in the future.

## Configuration

Minimal configuration:

```yaml
sensor:
  - platform: brandstofprijzen
```

Default configuration:

```yaml
sensor:
  - platform: brandstofprijzen
    monitored_variables:
      - euro95
      - diesel
      - lpg
    icon: mdi:gas-station
    unit_of_measurement: €/L
    prefix: Adviesprijs
    scan_interval:
        hours: 1
```

## Usage

TODO

## Changelog

All notable changes to this project will be documented in the [changelog](./CHANGELOG.md).

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
