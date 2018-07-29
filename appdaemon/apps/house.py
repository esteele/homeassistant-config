import csv
import appdaemon.plugins.hass.hassapi as hass
from lighting import Lighting

class House(Lighting):

    def initialize(self):
        # self.listen_state(self.turn_off_all,
        #                   'switch.kitchen_island_switch_3_0',
        #                   old='on',
        #                   new='off')
        # self.listen_state(self.morning_start_up,
        #                   'switch.kitchen_table_switch_5_0',
        #                   old='off',
        #                   new='on',
        #                   constrain_start_time='07:00:00',
        #                   constrain_end_time='10:00:00')

        self.listen_event(self.unlock_front_door, 'ios.notification_action_fired', actionName='UNLOCK_FRONT_DOOR')
        self.listen_event(self.unlock_rear_door, 'ios.notification_action_fired', actionName='UNLOCK_REAR_DOOR')
        self.listen_event(self.lock_all_doors, 'ios.notification_action_fired', actionName='LOCK_ALL_DOORS')
        self.listen_event(self.turn_on_babysitter_mode, 'ios.notification_action_fired', actionName='TURN_ON_BABYSITTER_MODE')

        self.listen_state(self.arrived_home, 'binary_sensor.eric_home', old='not_home', new='home')
        self.listen_state(self.nobody_home, 'group.family', old='home', new='not_home')
        self.listen_state(self.nobody_home, 'group.family', old='on', new='off')


        self.listen_state(self.mailbox_opened, 'binary_sensor.mailbox_sensor', old='off', new='on')

        # self.ask_lighting_pref()
        # import datetime
        # time = datetime.datetime.now()
        # self.run_every(self.ask_lighting_pref, time, 15 * 60)
        # self.listen_event(self.log_yes_light, 'ios.notification_action_fired', actionName='LOG_YES_LIGHT')
        # self.listen_event(self.log_no_light, 'ios.notification_action_fired', actionName='LOG_NO_LIGHT')

        self.listen_state(self.turn_off_rear_lights,
                          'lock.door_rear_locked',
                          old='unlocked',
                          new='locked')

        self.listen_state(self.turn_on_rear_lights,
                          'lock.door_rear_locked',
                          old='locked',
                          new='unlocked',
                          constrain_start_time=self.evening_start,
                          constrain_end_time=self.morning_start)

        self.listen_state(self.notify_unlocked,
                          'lock.door_rear_locked',
                          old='locked',
                          new='unlocked')

        self.listen_state(self.notify_unlocked,
                          'lock.door_front_locked',
                          old='locked',
                          new='unlocked')


    @property
    def is_babysitter_mode(self):
        babysitter_mode = self.get_state('input_boolean.babysitter_mode')
        value = babysitter_mode == 'on'
        self.log('Babysitter mode: {0}'.format(value))
        return value

    @property
    def front_door_lock_status(self):
        return self.get_state('lock.door_front_locked')

    @property
    def rear_door_lock_status(self):
        return self.get_state('lock.door_rear_locked')

    def arrived_home(self, *args):
        self.log('Someone just arrived home, so I\'m sending a notification')
        message = "The front door is currently %s.\nThe rear door is currently %s" % (self.front_door_lock_status, self.rear_door_lock_status)
        title = "Welcome Home"

        if self.front_door_lock_status == 'unlocked' and self.rear_door_lock_status == 'unlocked':
            category = 'welcome_home_ready'
        elif self.front_door_lock_status == 'unlocked' and self.rear_door_lock_status == 'locked':
            category = 'welcome_home_rear_only'
        elif self.front_door_lock_status == 'locked' and self.rear_door_lock_status == 'unlocked':
            category = 'welcome_home_front_only'
        elif self.front_door_lock_status == 'locked' and self.rear_door_lock_status == 'locked':
            category = 'welcome_home_both_doors'
        self.log(category)
        device = 'eric_iphone'
        self.call_service("notify/ios_%s" % device,
                          message=message,
                          title=title,
                          data={'push': {'category': category}})


    def unlock_front_door(self, *args):
        self.log("Got iOS response. Unlocking front door.")
        self.call_service("lock/unlock",
                          entity_id="lock.door_front_locked")

    def unlock_rear_door(self, *args):
        self.log("Got iOS response. Unlocking rear door.")
        self.call_service("lock/unlock",
                          entity_id="lock.door_rear_locked")


    def nobody_home(self, *args):
        if not self.is_babysitter_mode and (self.front_door_lock_status != 'locked' or self.rear_door_lock_status != 'locked'):
            self.log('Nobody\'s home so I\'m sending a warning')
            message = "No one is currently at home, but one or more doors are unlocked."
            title = "Nobody home"
            # devices = ['eric_iphone', 'pam_iphone']
            device = 'eric_iphone'
            # for device in devices:
            self.call_service("notify/ios_%s" % device,
                              message=message,
                              title=title,
                              data={'push': {'category': 'nobody_home'}})


    def lock_all_doors(self, *args):
        self.log("Got iOS response. Locking all doors")
        self.call_service("lock/lock",
                          entity_id="group.all_locks")

    def turn_on_babysitter_mode(self, *args):
        self.log("Got iOS response. Turning on babysitter mode")
        self.call_service("input_boolean/turn_on",
                          entity_id="input_boolean.babysitter_mode")

    def mailbox_opened(self, *args):
        self.log('The mailbox was opened. Sending notification')
        device = 'eric_iphone'
        # for device in devices:
        self.call_service("notify/ios_%s" % device,
                          message='Mailbox opened',
                          title='Mailbox opened',
                          data={'push': {'category': 'mailbox_opened'}})


    # def ask_lighting_pref(self, *args):
    #     elevation = self.get_state('sensor.sun_elevation')
    #     if float(elevation) < 0.0 :
    #         self.log_interior_lighting_preferences(True)
    #     else:
    #         device = 'eric_iphone'
    #         # for device in devices:
    #         self.call_service("notify/ios_%s" % device,
    #                           message='Ideally, should the interior lights be on right now?',
    #                           title='Lighting survey',
    #                           data={'push': {'category': 'lighting_logger'}})


    # def log_yes_light(self, *args):
    #     self.log_interior_lighting_preferences(True)

    # def log_no_light(self, *args):
    #     self.log_interior_lighting_preferences(False)

    # def log_interior_lighting_preferences(self, should_light):
    #     with open('/share/lights.csv', 'a') as f:
    #         cloud_cover = self.get_state('sensor.dark_sky_cloud_coverage')
    #         visibility = self.get_state('sensor.dark_sky_visibility')
    #         elevation = self.get_state('sensor.sun_elevation')
    #         azimuth = self.get_state('sensor.sun_azimuth')
    #         w = csv.writer(f)
    #         w.writerow([cloud_cover, visibility, elevation, azimuth, should_light])

    # Keypad Lock
    # Locked with Keypad by user 0
    # Manually Locked by Key Cylinder or Inside thumb turn

    def notify_unlocked(self, entity_id, *args):
        # self.log(str(args))
        # state = self.get_state(entity_id, 'all')
        # status = state['lock_status']
        # friendly_name = state['friendly_name']
        # notification = self.get_state(entity_id, 'notification')
        status = self.get_state(entity=entity_id, attribute='lock_status')
        friendly_name = self.get_state(entity=entity_id, attribute='friendly_name')
        self.log('A door was unlocked, so I\'m sending a notification')
        self.call_service('notify/ios_eric_iphone',
                          message=status,
                          title='%s unlocked' % friendly_name,
                          data={'push': {'category': 'DOOR_LOCKS'}})

    def turn_off_rear_lights(self, *args):
        lock_type = self.get_state(entity='lock.door_rear_locked', attribute='notification')
        if lock_type == 'Manual Lock':
            self.log('The rear door was manually locked, so I\'m turning off the rear lights')
            self.turn_off('switch.backyard_lights_switch')

    def turn_on_rear_lights(self, *args):
        action = self.get_state(entity='lock.door_rear_locked', attribute='notification')
        if action == 'Manual Unlock':
            self.log('The rear door was manually unlocked, so I\'m turning on the rear lights')
            self.turn_on('switch.backyard_lights_switch')
