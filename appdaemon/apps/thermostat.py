import appdaemon.appapi as appapi


class Thermostat(appapi.AppDaemon):

    def initialize(self):
        self.log("Initializing thermostat automation")
        evening_start_time = self.parse_time('21:00:00')
        self.log('Overnight low check will happen at %s' % evening_start_time)
        self.run_daily(self.weather_check, evening_start_time)
        # self.weather_check()
        self.listen_event(self.turn_on_heat, 'ios.notification_action_fired', actionName='TURN_ON_HEAT')
        # self.call_service("persistent_notification/create",
        #                   message='test',
        #                   title='test',
        #                   notification_id="weather-furnace")

        # entity_id = 'persistent_notification.weatherfurnace'
        # import homeassistant.remote as remote
        # api = remote.API('home.esteele.net', 'TNy9L73spRj7yih83kDEotTm32T9B7')
        # remote.remove_state


    @property
    def heat_status(self):
        return self.get_state('climate.living_room') == 'heat'

    @property
    def overnight_low(self):
        temp = self.get_state(
            'sensor.dark_sky_daily_low_apparent_temperature_1')
        return float(temp)

    def weather_check(self, *args):
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

        # Clear persistent notification
        # 'persistent_notification.weatherfurnace'

#     def initialize(self):
#         self.log("Initializing thermostat automation")
#         repeat = float(self.args['refresh_minutes']) * 60.0
#         # self.run_once(self.get_current_program, self.datetime(), repeat)
#         self.listen_event(self.get_current_program, "appd_started")

#     def get_current_program(self, event_name, other, again):
#         auth_code = '5YiTCtIhDlad9fdCo4ZoR92mkMhcyDDo'
#         token = 'la8xl4io1owgo4FbHlodZh6aiJK6BY21'
#         key = '26vRoLFZze8AEfM3gPBmhV8MjnASjutT'
#         redirect_uri = 'https://home.esteele.net'

#         # {"AUTHORIZATION_CODE": "5YiTCtIhDlad9fdCo4ZoR92mkMhcyDDo", "ACCESS_TOKEN": "la8xl4io1owgo4FbHlodZh6aiJK6BY21", "API_KEY": "26vRoLFZze8AEfM3gPBmhV8MjnASjutT", "REFRESH_TOKEN": "NTdMobeE34ptMEmttcj83WcbVMoPrPrH"}
#         # curl -s -H 'Content-Type: text/json' -H 'Authorization: Bearer ACCESS_TOKEN' 'https://api.ecobee.com/1/thermostat?format=json&body=\{"selection":\{"selectionType":"registered","selectionMatch":"","includeRuntime":true\}\}'

#         import json
#         import requests

#         # 'https://api.ecobee.com/authorize?response_type=code&client_id=APP_KEY&redirect_uri=YOUR_SERVER_URI&scope=SCOPE"
#         auth_url = 'https://api.ecobee.com/token?grant_type=refresh_token&refresh_token=%s&client_id=%s' % (token, key)
#         # auth_url = 'https://api.ecobee.com/token?grant_type=authorization_code&code=%s&client_id=%s' % (auth_code, key)
#         auth_response = requests.post(auth_url)
#         import pdb; pdb.set_trace( )

#         payload = {"selection": {"selectionType": "registered", "selectionMatch": "", "includeRuntime": True, "includeEvents": True, 'includeProgram': True}}
#         headers = {'Content-Type': 'text/json', 'Authorization': 'Bearer %s' % token}
#         url = 'https://api.ecobee.com/1/thermostat?format=json&body=%s' % json.dumps(payload)
#         requests.get(url, headers=headers).json()

#         import pdb; pdb.set_trace( )
