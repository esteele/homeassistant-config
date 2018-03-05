import appdaemon.appapi as appapi


class HueUpdates(appapi.AppDaemon):

    def initialize(self):
        self.listen_event(self.show_notification,
                          "sensor.hue_update_available",
                          old=False,
                          new=True)
        self.listen_event(self.hide_notification,
                          "sensor.hue_update_available",
                          old=True,
                          new=False)

    def show_notification(self):
        self.log('Hue update available')

    def hide_notification(self):
        self.log('No Hue update available')
