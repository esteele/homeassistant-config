import appdaemon.appapi as appapi
import json

#
# Owntracks functionality
#
# Args:
#   refresh_minutes
#   devices


class Owntracks(appapi.AppDaemon):

    def initialize(self):
        self.log("Initializing location automation")
        repeat = float(self.args['refresh_minutes']) * 60.0
        self.run_every(self.update_location, self.datetime(), repeat)
        self.listen_event(self.update_location, event='ha_started')
        self.update_location()

    def update_location(self, *args):
        devices = self.split_device_list(self.args['devices'])
        # payload = {'_type': 'cmd',
        #            'action': 'reportLocation'}

        for device in devices:
            self.log("Triggering location update for {0}".format(device))
            # topic = 'owntracks/{0}/{0}/cmd'.format(device)
            # self.call_service('mqtt/publish',
            #                   topic=topic,
            #                   payload=json.dumps(payload))

            # self.call_service("notify/ios_{0}".format(device),
            #                   message="request_location_update")
