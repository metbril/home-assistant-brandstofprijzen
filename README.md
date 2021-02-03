# United Consumers Brandstofprijzen for Home Assistant

Home Assistant component for fuel prices from United Consumers

## Installation

TODO

## Configuration

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
