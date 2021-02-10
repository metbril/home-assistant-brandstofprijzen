# United Consumers Brandstofprijzen for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/metbril/home-assistant-brandstofprijzen/)

Home Assistant component for fuel prices from [United Consumers](https://www.unitedconsumers.com/brandstofprijzen/).

![](./assets/logo.png)

## Installation

## HACS (Recommended)

This integration can be added to [HACS](https://hacs.xyz/) as a custom (non-default) repository.

Assuming you have already installed and configured HACS, follow these steps:

1. Navigate to the HACS integrations page at `http://<your-home-assistant>:8123/hacs/integrations`.
2. Click the 3 vertical dots menu in the top right corner.
3. Choose 'Custom repositories'
4. Enter the name of this repository (`https://github.com/metbril/home-assistant-brandstofprijzen/`) in the text field in the dialog.
5. Choose 'Integration' from the Category list in the dialog.
6. Click 'Add'. The repository will now be added to your HACS.
7. Click the 'x' to close the dialog.
8. The integration is now visible. Click 'Install', and click 'Install' again.
9. Ready! Now continue with the configuration.

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
      - super
      - super_mlv
      - premium_benzines
      - premium_diesels
      - blueone95
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

## Legal notice

All product names, trademarks and registered trademarks in (the images in) this repository, are property of their respective owners. All images in this repository are used by the project for identification purposes only.
