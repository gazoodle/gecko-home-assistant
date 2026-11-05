# Gecko Home Assistant


[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]

[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]

![installation_badge](https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=integration%20usage&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.gecko.total)
![Validate](https://github.com/gazoodle/gecko-home-assistant/actions/workflows/validate.yml/badge.svg)
![Lint](https://github.com/gazoodle/gecko-home-assistant/actions/workflows/lint.yml/badge.svg)

# Addressing Gecko email "Your in.touch 2 app is being retired"

In November 2026, Gecko Alliance sent an email around to all their in.touch2 customers
stating that their app would cease functioning on January 1st 2028.

This is obviously a concerning development from Gecko Alliance, but rest assured this
integration will continue to function long after the manufacturers have retired their own
app and its cloud service.

This support library [`geckolib`](https://github.com/gazoodle/geckolib) was built using the data contained in their SpaPackStruct.xml. 
This file describes the memory layout of the spa pack firmware. Because we have already got those
layouts any Spa that is currently working will remain working.

The risks for you are: If you get a newer firmware from Gecko, and their layout significantly
changes and is later than we have access to the SpaPackStruct then this could potentially
mean your spa cannot be controlled by this library any longer.

Sadly, this is already true for the latest hardware packs that use the in.touch3 system
because that offloads the pack shape to a cloud service that is opaque and inaccessible to
us.

I will continue to attempt to get access to the pack data from them hoping to continue
support for older devices but historically this has not been very successful. The latest
version that I have had is 40.0.0.0.

This integration & support library does not use, and has never used, their cloud service to 
provide the ability to control your spa. This functionality is local only.


# Version History

## v0.1.33
 - Bump geckolib to 1.0.16, which fixes the silent loss of the spa push subscription that
   left entities stale for hours while the spa still showed as connected
 - Add a "Last Data" diagnostic sensor showing when real spa data last arrived, which is the
   correct signal for any user staleness automation
 - Add a "Spa Resync" diagnostic button that re-reads spa state in place without reconnecting
 - Guard the event queue loop so one exception no longer stops event processing permanently
 - Guard button and select platform setup against the facade going away during a reload
 - Fix options flow crash on recent Home Assistant versions
   ([#233](https://github.com/gazoodle/gecko-home-assistant/issues/233))
 - Fix workflow branch filters so lint and validate actually run
 - Update devcontainer to latest & pull codex in ... because it's made it easy to iterate now.
 - Kudos to @DanSmith888, nice piece of work fixing these problems that I could never reproduce, thank you

## v0.1.32
 - Bump geckolib to 1.0.15

## v0.1.31
 - Bump geckolib to 1.0.14
 - Add Bain Ultra support, including chroma if present

## v0.1.30
 - Bump geckolib to 1.0.13
 - Add inMix synchro support

## v0.1.29
 - Bump geckolib to 1.0.11
 - Fix tardy updates to spa controls
 - inMix driver updates the whole inMix structure in one go - hopefully this will control the zones correctly.

## v0.1.28
 - Bump geckolib to 1.0.10
 - Handle TempNotValid error by making climate, water heater and current temperature sensors unavailable
 - Fix Error sensor that wasn't updating if the library error sensor changed state

## v0.1.27
 - Bump geckolib to 1.0.9
 - Fixed broken EcoMode swithc that 1.0.8 introduced ([#160](https://github.com/gazoodle/gecko-home-assistant/issues/160))
 - Added pump and blower sensors to show P<n> & BL device states because buttons use UdP<n> exclusively ([#159](https://github.com/gazoodle/gecko-home-assistant/issues/159))
 - Restore old min temperature, but use the max config data for min & max if available ([#149](https://github.com/gazoodle/gecko-home-assistant/issues/149))

## v0.1.26
 - Bump geckolib to 1.0.8
 - Mr.Steam basic support

## v0.1.25
 - Bump geckolib to 1.0.7
 - Get some sensors from Mr.Steam units hopefully

## v0.1.24
 - Bump geckolib to 1.0.6 to handle bubble generator issues
 - Fix platorm loading bug that caused errors in log file during start-up

## v0.1.23
 - Bump geckolib to fix DIV/0

## v0.1.22
 - Made platform load/unload more tolerant of runtime faults
 - Support basic inMix RGB zones. Need feedback on this. No lighting modes or synchro support yet.

## v0.1.21
 - Prevent various entities (such as reminder dates) from being included in scenes as this would make
   reminders a bit pointless. This was belt and braces really since the date platform doesn't support
   scene restore, but in doing this, there were other entities that were being used that would have
   potentially caused problems.

## v0.1.20
 - Support changing date for reminders. A simple button to reset was originally considered, but
   ended up being a date object that can be set which gives much better flexibility. You can
   write your own buttons now.

## v0.1.19
 - Update bug template to link to gecko-home-assistant issues rather than the blueprint
 - Rework pumps to use new clean library versions, now supports one, two and variable speed pumps
 - Expose water heater as a native water heater entity in addition to the climate one
 - Expose water care mode as a select in addition to the climate preset modes
 - Support light L120 as well as existing internal light
 - Add buttons for all keypad operations
 - Add support for changing keypad backlight colour

## Breaking Changes
 - Blower is now a fan, not a switch
 - Pump modes are no longer "HIGH", "LOW", "OFF", they are "HI", "LO", "OFF" or "ON"

## v0.1.18
 - Implement climate action async_set_hvac_mode so that the integration can be used in scenes

## v0.1.17
 - Add supoort for lock mode if it exists
 - Add support for standby mode
 - Add "Heating" binary sensor

## v0.1.16
 - Using better async patterns which should alleviate some CPU usage issues and connection problems.
 - Much faster integration setup, removed wait for full connection from the init loop.
 - Status sensor available immediately so initialization progress can be tracked.
 - Reconnect button available after full connection, or connection failure allowing retry without
   having to restart HA.
 - Added "Spa In Use" sensor that is ON if any pumps, blowers or lights are on.
 - Added support for external heat sources
 - This is a big change, so I'm releasing it now while I'm still available to fix issues quickly

## v0.1.15
 - During the tidy and delint phase, constants were imported from HA 2025 locations, so this
   is now a minimum requirement. hacs.json updated accordingly.

## v0.1.14
- Get validation & lint workflows running
- Expose temperature sensors for current temperature, set point temperature and real setpoint
  temperature which takes economy mode into consideration. These allow various automations to
  be written that otherwise would have to dig into the attributes of the climate control object
- Added 'Snapshot' button to dump data that might be useful in getting new spa features implemented

## v0.1.13
- Bump the version number!

## v0.1.12
- Removed warnings about light color modes
- Added French string table, thanks @claudegel
- Fixed ConfigType, thanks @grahamcraqer
- Use geckolib 0.4.16, it fixes some other HA warnings and issues
- Use Fan modes correctly, thanks @sicarriere
- Update docker container to use latest version from blueprint ... phew, that was 2 years of updates

_Component to integrate with [Gecko Spas](https://geckoalliance.com)._

**This component will set up the following platforms.**

Platform | Description
-- | --
`button` | Reconnect & snapshot buttons.
`binary_sensor` | Various on/off spa sensors.
`sensor` | Text/Enum spa sensors.
`switch` | Waterfalls
`fan` | Spa pumps, fans.
`light`  | Spa lights
`climate` | Spa water heater
`select` | External heating support
`water_heater` | An alternative way to set spa water temperature
`date` | Reminder reset support

## Example screen shot

![Screenshots][screenshotimg]

## Installation (HACS)

The preferred method to install is to use HACS.

## Installation (No HACS)

If you don't have/want HACS installed, you will need to manually install the integration

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `gecko`.
4. Download _all_ the files from the `custom_components/gecko/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Gecko"

## Using the snapshot functionality

The snapshot function allows you to generate a datablock that can be used during development and testing
to support new SPA features. To use, please open an issue on Github outlining what your requirements are.

Then, switch to the integration device page where you should find a "Snapshot" button in the "Diagnostics"
panel.

1. Place your spa into default state, i.e. powered up, but idle.
2. Press the "Snapshot" button
3. Activate whatever feature you are trying to provide functionality for.
4. Press the "Snapshot" button again.

Repeat steps 3 & 4 for as many times as necessary to capture all the states that your spa goes through
during you exercising the feature.

You should find this data in your log file but, for convenience, it's also in the persistent notification
panel on lovelace. Select the snapshot notification, expand the data block behind the "Click to expand"
label, and copy the data block (which begins ```{'Integration Version ...'```}).

Add this data as a reply to your issue on Github. One snapshot per reply please otherwise it might get
too busy. Annotate the reply with a statement of what your spa was doing at the snapshot time, e.g.
"Idle" or "After turning RGB light to Red".

[gecko-ha]: https://github.com/gazoodle/gecko-home-assistant
[commits-shield]: https://img.shields.io/github/commit-activity/y/gazoodle/gecko-home-assistant.svg?style=for-the-badge
[commits]: https://github.com/gazoodle/gecko-home-assistant/commits/master
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[screenshotimg]: screenshot.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/gazoodle/gecko-home-assistant.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-https://github.com/gazoodle-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/gazoodle/gecko-home-assistant.svg?style=for-the-badge
[releases]: https://github.com/gazoodle/gecko-home-assistant/releases