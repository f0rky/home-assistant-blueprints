# Uber Eats Order Tracker - Home Assistant Blueprint

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/f0rky/home-assistant-blueprints)](https://github.com/f0rky/home-assistant-blueprints/releases)
[![GitHub license](https://img.shields.io/github/license/f0rky/home-assistant-blueprints)](https://github.com/f0rky/home-assistant-blueprints/blob/main/LICENSE)

This Home Assistant blueprint allows you to monitor your Uber Eats food delivery status and receive smart home notifications as your order progresses through different delivery stages. Never miss a food delivery again!

## Features

- Track Uber Eats order status in real-time
- Receive notifications on your TV when food is nearby or has arrived
- Flash lights when your delivery is approaching
- Turn on porch lights when delivery arrives
- Send mobile notifications with driver information and ETA
- Automatically clear tracking link when delivery is complete

## Installation Options

### Option 1: Using the Blueprint (Recommended)

The blueprint approach is the easiest way to get started and requires minimal setup.

#### Step 1: Install the Blueprint

1. In Home Assistant, go to **Configuration** → **Blueprints**
2. Click **Import Blueprint**
3. Paste the following URL:
   ```
   https://raw.githubusercontent.com/f0rky/home-assistant-blueprints/master/uber-eats-tracker/uber-eats-tracker-direct.yaml
   ```
4. Click **Preview** then **Import**

#### Step 2: Create an Input Helper

1. Go to **Configuration** → **Helpers**
2. Click **Add Helper**
3. Select **Text**
4. Name it "Uber Eats Tracking Link"
5. Set the maximum length to 255 characters
6. Choose an icon (like mdi:food-delivery)
7. Click **Create**

#### Step 3: Create the Automation Using the Blueprint

1. Go to **Configuration** → **Automations**
2. Click **Add Automation**
3. Click **Create automation from blueprint**
4. Select the **Uber Eats Order Tracker** blueprint
5. Configure the inputs:
   - **Uber Eats Tracking Link Input**: Select the input_text.uber_eats_tracking_link you created
   - **TV Media Player**: Select your TV media player entity
   - **Notification Lights**: Select lights to flash when order is nearby
   - **Porch Lights**: Select lights to turn on when delivery arrives
   - **Mobile Notification Device**: (Optional) Select your mobile device
6. Click **Save**

#### Step 4: Create Required Media Files

1. Create two simple notification images:
   - `/config/www/ubereats-nearby.png` - An image showing "Food delivery approaching"
   - `/config/www/ubereats-arrived.png` - An image showing "Food delivery arrived"

#### Step 5: Use the Automation

1. When you receive an Uber Eats order, copy the tracking link 
2. In Home Assistant, paste the link into the "Uber Eats Tracking Link" input helper
3. The automation will now monitor your delivery status and provide notifications

### Option 2: Using the Custom Component (Advanced)

For more advanced functionality, you can install the custom component.

#### Step 1: Install the Custom Component

1. Create the following directory structure in your Home Assistant config folder:
   ```
   custom_components/uber_eats/
   ```
2. Copy all files from the `custom_components/uber_eats/` directory in this repository to your Home Assistant installation

#### Step 2: Configure the Component

Add the following to your `configuration.yaml`:

```yaml
sensor:
  - platform: uber_eats
    name: My Uber Eats Order
    tracking_url: !secret uber_eats_tracking_url
    scan_interval:
      minutes: 1
```

Add to your `secrets.yaml`:
```yaml
uber_eats_tracking_url: "Your Uber Eats tracking URL here"
```

#### Step 3: Create Automations

Create automations for different delivery statuses:

```yaml
automation:
  - alias: "Uber Eats Order Nearby"
    trigger:
      platform: state
      entity_id: sensor.my_uber_eats_order
      to: "nearby"
    action:
      - service: light.turn_on
        target:
          entity_id: light.living_room
        data:
          flash: short
      - service: media_player.play_media
        target:
          entity_id: media_player.tv
        data:
          media_content_id: /local/ubereats-nearby.png
          media_content_type: image/png

  - alias: "Uber Eats Order Arrived"
    trigger:
      platform: state
      entity_id: sensor.my_uber_eats_order
      to: "arrived"
    action:
      - service: light.turn_on
        target:
          entity_id: light.porch_light
        data:
          brightness_pct: 100
      - service: media_player.play_media
        target:
          entity_id: media_player.tv
        data:
          media_content_id: /local/ubereats-arrived.png
          media_content_type: image/png
```

## Creating a Dashboard

Add this Lovelace card to your dashboard:

```yaml
type: entities
title: Uber Eats Order Tracking
entities:
  - entity: input_text.uber_eats_tracking_link
    name: Tracking Link
  - entity: sensor.my_uber_eats_order
    name: Order Status
  - type: attribute
    entity: sensor.my_uber_eats_order
    attribute: driver_name
    name: Driver
  - type: attribute
    entity: sensor.my_uber_eats_order
    attribute: eta
    name: ETA
  - type: attribute
    entity: sensor.my_uber_eats_order
    attribute: distance
    name: Distance
```

## Troubleshooting

If you encounter issues:

1. **No Status Updates**: Check that your tracking URL is correct and accessible
2. **Parsing Issues**: The component relies on parsing Uber's tracking page. If Uber changes their site, parsing might fail.
3. **Home Assistant Logs**: Check logs for any error messages from the uber_eats component

## Advanced Configuration

You can extend this setup with:

1. **Customized TTS Announcements**: Add text-to-speech notifications 
2. **Multiple Delivery Services**: Add similar components for other delivery services
3. **Geolocation Tracking**: Combine with zone triggers for more accurate notifications
4. **Dynamic Light Effects**: Change light colors based on the delivery status

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
