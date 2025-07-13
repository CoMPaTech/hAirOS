# Ubiquiti AirOS Custom Component for Home Assistant

**:warning::warning::warning:Read the [release notes](https://github.com/CoMPaTech/hAirOS/releases) before upgrading, in case there are BREAKING changes! :warning: :warning: :warning:**

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/CoMPaTech/hAirOS/)
[![CodeFactor](https://www.codefactor.io/repository/github/CoMPaTech/hAirOS/badge)](https://www.codefactor.io/repository/github/CoMPaTech/hAirOS)
[![HASSfest](https://github.com/CoMPaTech/hAirOS/workflows/Validate%20with%20hassfest/badge.svg)](https://github.com/CoMPaTech/hAirOS/actions)
[![Generic badge](https://img.shields.io/github/v/release/CoMPaTech/hAirOS)](https://github.com/CoMPaTech/hAirOS)

[![CodeRabbit.ai is Awesome](https://img.shields.io/badge/AI-orange?label=CodeRabbit&color=orange&link=https%3A%2F%2Fcoderabbit.ai)](https://coderabbit.ai)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=CoMPaTech_hAirOS&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=CoMPaTech_hAirOS)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=CoMPaTech_hAirOS&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=CoMPaTech_hAirOS)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=CoMPaTech_hAirOS&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=CoMPaTech_hAirOS)

## Requirements

Only tested/confirmed with AirOS 8 on:

- [x] Nanostation 5AC (LOCO5AC) by @CoMPaTech
- [x] PowerBeam 5AC gen2 by @exico91

## Installation

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=CoMPaTech&repository=hAirOShAirOhAirOSntegrations)

## Configuration

Configure this integration the usual way, requiring your username (`ubnt`), password and IP address of the AirOS device.

## What it provides

In the current state it retrieves some information and should display the 'other device connected', connection mode, SSID and both actual data being transferred and the maximum capacity.

## State: BETA

Even though available does not mean it's stable yet, the HA part is solid but the class used to interact with the API is in need of improvement (e.g. better overall handling). This might also warrant having the class available as a module from pypi.

## How to install?

- Use [HACS](https://hacs.xyz)
- Navigate to the `Integrations` page and use the three-dots icon on the top right to add a custom repository.
- Use the link to this page as the URL and select 'Integrations' as the category.
- Look for `AirOS` in `Integrations` and install it!

### How to add the integration to HA Core

For each device you will have to add it as an integration.

- [ ] In Home Assistant click on `Configuration`
- [ ] Click on `Integrations`
- [ ] Hit the `+` button in the right lower corner
- [ ] Search or browse for 'Ubiquiti AirOS' and click it
- [ ] Enter your details

### Is it tested?

It works on my bike and Home Assistant installation :) Let me know if it works on yours!

[![SonarCloud](https://sonarcloud.io/images/project_badges/sonarcloud-black.svg)](https://sonarcloud.io/summary/new_code?id=CoMPaTech_hAirOS)

And [Home-Assistant Hassfest](https://github.com/home-assistant/actions) and [HACS validation](https://github.com/hacs/action)
