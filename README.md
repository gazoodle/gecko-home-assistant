# gecko-home-assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]

_Component to integrate with [Gecko Spas][gecko-ha]._

**This component will set up the following platforms.**

Platform | Description
-- | --
`binary_sensor` | Various on/off spa sensors.
`sensor` | Text/Enum spa sensors.
`switch` | Waterfalls
`fan` | Spa pumps, fans.
`light`  | Spa lights
`climate` | Spa water heater

<!-- ![example][exampleimg]) -->

## Installation (HACS)

The preferred method to install is to use HACS. This repo should be available in the default list, but
this is currently in progress, so you might need to add https://github.com/gazoodle/gecko-home-assistant
as a custom repo. See https://hacs.xyz/docs/faq/custom_repositories for details.

## Installation (No HACS)

If you don't have/want HACS installed, you will need to manually install the integration

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `gecko`.
4. Download _all_ the files from the `custom_components/gecko/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Gecko"

Using your HA configuration directory (folder) as a starting point you should now also have this:

```text
custom_components/gecko/.translations/en.json
custom_components/gecko/__init__.py
custom_components/gecko/binary_sensor.py
custom_components/gecko/climate.py
custom_components/gecko/config_flow.py
custom_components/gecko/const.py
custom_components/gecko/light.py
custom_components/gecko/manifest.json
custom_components/gecko/sensor.py
custom_components/gecko/switch.py
```

## Configuration is done in the UI

<!---->

***

[gecko-ha]: https://github.com/gazoodle/gecko-home-assistant
[commits-shield]: https://img.shields.io/github/commit-activity/y/gazoodle/gecko-home-assistant.svg?style=for-the-badge
[commits]: https://github.com/gazoodle/gecko-home-assistant/commits/master
[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/gazoodle/gecko-home-assistant.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-gazoodle%40hash.fyi-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/gazoodle/gecko-home-assistant.svg?style=for-the-badge
[releases]: https://github.com/gazoodle/gecko-home-assistant/releases
