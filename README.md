# United Consumers Brandstofprijzen for Home Assistant

Home Assistant component for fuel prices from [United Consumers](https://www.unitedconsumers.com/brandstofprijzen/).

## Installation

TODO

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
