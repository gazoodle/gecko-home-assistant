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
`button` | Reconnect button.
`binary_sensor` | Various on/off spa sensors.
`sensor` | Text/Enum spa sensors.
`switch` | Waterfalls.
`fan` | Spa pumps, fans.
`light`  | Spa lights
`climate` | Spa water heater

## Example screen shot

![Screenshots][screenshotimg]

{% if not installed %}
## Installation

1. Click install.
2. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Gecko".

{% endif %}

## Configuration is done in the UI

<!---->

***

[gecko-ha]: https://github.com/gazoodle/gecko-home-assistant
[commits-shield]: https://img.shields.io/github/commit-activity/y/gazoodle/gecko-home-assistant.svg?style=for-the-badge
[commits]: https://github.com/gazoodle/gecko-home-assistant/commits/master
[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[screenshotimg]: https://github.com/gazoodle/gecko-home-assistant/blob/main/screenshot.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/gazoodle/gecko-home-assistant.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-gazoodle%40hash.fyi-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/gazoodle/gecko-home-assistant.svg?style=for-the-badge
[releases]: https://github.com/gazoodle/gecko-home-assistant/releases
