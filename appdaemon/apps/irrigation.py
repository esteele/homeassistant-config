import appdaemon.plugins.hass.hassapi as hass

class Irrigation(hass.Hass):

    def initialize(self):
        self.log("Initializing irrigation automation")

        self.listen_state(self.irrigation_turned_on,
                          'switch.irrigation_switch',
                          old='off',
                          new='on',
                          minutes=60)

    def irrigation_turned_on(self, entity_id, attribute, old, new, kwargs):
        minutes = kwargs.get('minutes')
        self.log(
            "Turned on {0}. {1} minutes and counting...".format(entity_id, minutes))
        self.run_in(
            self._turn_off_with_timer, minutes * 60, entity_id=entity_id)

    def _turn_off_with_timer(self, *args):
        # TODO: This seems silly, but I can't seem to call turn_off directly
        # and pass through the entity id.
        entity_id = args[0]['entity_id']
        self.log('Turning off {0}'.format(entity_id))
        self.turn_off(entity_id)
