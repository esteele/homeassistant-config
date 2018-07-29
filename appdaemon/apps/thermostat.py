import appdaemon.plugins.hass.hassapi as hass


class Thermostat(hass.Hass):

    def initialize(self):
        self.log("Initializing thermostat automation")
        evening_start_time = self.parse_time('21:00:00')
        self.log('Overnight low check will happen at %s' % evening_start_time)
        self.run_daily(self.weather_check, evening_start_time)
        self.listen_event(self.turn_on_heat, 'ios.notification_action_fired', actionName='TURN_ON_HEAT')

    @property
    def heat_status(self):
        return self.get_state('climate.living_room') == 'heat'

    @property
    def overnight_low(self):
        temp = self.get_state(
            'sensor.dark_sky_daily_low_apparent_temperature_1')
        return float(temp)

    def weather_check(self, *args):
        """ Send a notification if the overnight temperature will be below 50 degrees
            and the heat is not turned on.
        """
        if self.overnight_low < 50.0 and not self.heat_status:
            self.log("Overnight low is expected to be %s, heat is %s. Triggering alert." % (self.overnight_low, self.heat_status))
            message = "Tonight's temperature is forecast to be %s˚, but the heat is currently off." % self.overnight_low
            title = "Brrr!"

            devices = ['eric_iphone', 'pam_iphone']
            for device in devices:
                self.call_service("notify/ios_%s" % device,
                                  message=message,
                                  title=title,
                                  data={'push': {'category': 'OVERNIGHT_HEATING'}})

            self.call_service("persistent_notification/create",
                              message=message,
                              title=title,
                              notification_id="weather-furnace")
        else:
            self.log("Overnight low is expected to be %s, heat is %s. Skipping alert." % (self.overnight_low, self.heat_status))

    def turn_on_heat(self, *args):
        self.log("Got iOS response. Turning on heat.")
        self.call_service("climate/set_operation_mode",
                          entity_id="climate.living_room",
                          operation_mode="heat")
