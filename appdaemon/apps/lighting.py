import appdaemon.appapi as appapi


class Lighting(appapi.AppDaemon):
    def initialize(self):
        self.log('Initializing lighting base class')
        self.fluxer = None
        self.fluxing_active = True
        self.listen_state(self.turn_fluxing_on,
                          'group.living_room_overheads',
                          old='off',
                          new='on')
        self.listen_state(self.turn_fluxing_off,
                          'group.living_room_overheads',
                          old='on',
                          new='off')
        self.listen_state(self.set_foyer_level,
                          'light.foyer',
                          old='off',
                          new='on')

    @property
    def is_babysitter_mode(self):
        babysitter_mode = self.get_state('input_boolean.babysitter_mode')
        value = babysitter_mode == 'on'
        self.log('Babysitter mode: {0}'.format(value))
        return value

    @property
    def is_occoupied(self):
        family_status = self.get_state('group.family') == 'home' or self.get_state('group.family') == 'on'
        return family_status or self.is_babysitter_mode

    # @property
    # def is_flux_mode(self):
    #     return self.get_app("flux").is_flux_mode

    # def turn_fluxing_on(self, *args):
    #     self.log('turn_fluxing_on')
    #     self.get_app("flux").turn_fluxing_on()

    # def turn_fluxing_off(self, *args):
    #     self.log('turn_fluxing_off')
    #     self.get_app("flux").turn_fluxing_off()

    @property
    def morning_start(self):
        return "06:00:00"

    @property
    def morning_start_time(self):
        return self.parse_time(self.morning_start)

    @property
    def morning_end(self):
        return self.day_start

    @property
    def morning_end_time(self):
        return self.day_start_time

    @property
    def day_start(self):
        return "sunrise + 01:00:00"

    @property
    def day_start_time(self):
        return self.parse_time(self.day_start)

    @property
    def day_end(self):
        return self.evening_start

    @property
    def day_end_time(self):
        return self.evening_start_time

    @property
    def evening_start(self):
        return "sunset - 01:00:00"

    @property
    def evening_start_time(self):
        return self.parse_time(self.evening_start)

    @property
    def evening_end(self):
        return self.late_night_start

    @property
    def evening_end_time(self):
        return self.late_night_start_time

    @property
    def late_night_start(self):
        return "23:00:00"

    @property
    def late_night_start_time(self):
        # self.log(str(self.late_night_start))
        return self.parse_time(str(self.late_night_start))

    @property
    def late_night_end(self):
        return self.morning_start

    @property
    def late_night_end_time(self):
        return self.morning_start_time

    @property
    def is_morning(self):
        return self.now_is_between(self.morning_start, self.morning_end)

    @property
    def is_day(self):
        return self.now_is_between(self.day_start, self.day_end)

    @property
    def is_evening(self):
        return self.now_is_between(self.evening_start, self.evening_end)

    @property
    def is_late_night(self):
        return self.now_is_between(self.late_night_start, self.late_night_end)

    @property
    def is_flux_mode(self):
        return self.get_state('input_boolean.flux_lights') == 'on'

    def turn_fluxing_on(self, *args):
        self.log('turn_fluxing_on')
        if self.is_flux_mode:
            self.fluxing_active = True
            # self.turn_on('switch.fluxer')
            self.fluxer = self._flux_lights(*args)

    def _flux_lights(self, *args):
        if self.fluxing_active:
            self.call_service('switch/fluxer_update')
            self.fluxer = self.run_in(self._flux_lights, 30)

    def turn_fluxing_off(self, *args):
        self.log('turn_fluxing_off')
        # self.turn_off('switch.fluxer')
        # self.log('cancelling timer')
        self.fluxing_active = False
        # if self.fluxer is None:
        #     self.log('Fluxer not set')
        #     return
        # self.log(self.fluxer)
        # time, interval, kwargs = self.info_timer(self.fluxer)
        # self.log('%s/%s/%s' % (time, interval, kwargs))

        try:
            self.cancel_timer(self.fluxer)
            self.log('Flux timer cancelled')
        except AttributeError:
            self.log('Fluxer not found, skipping')
        # time, interval, kwargs = self.info_timer(self.fluxer)
        # self.log('%s/%s/%s' % (time, interval, kwargs))

    def set_foyer_level(self, *args):
        self.log('setting foyer lighting level')
        if self.is_late_night:
            level = 255 * 0.5
        else:
            level = 255 * .75
        self.turn_on('light.foyer', brightness=level)


class Porch(Lighting):

    LIGHT_NAME = 'light.front_porch'
    # LIGHT_NAME = 'switch.icicle_lights_switch'

    def initialize(self):
        self.log("Initializing porch lighting automation")
        self.log("Porch lights will be active from %s to %s" % (self.evening_start_time, self.evening_end_time))
        self.run_daily(self.activate, self.evening_start_time)
        self.run_daily(self.deactivate, self.evening_end_time)

    def activate(self, event_name):
        self.log("Turning on light {0}".format(self.LIGHT_NAME))
        self.turn_on(self.LIGHT_NAME)

    def deactivate(self, event_name):
        self.log("Turning off light {0}".format(self.LIGHT_NAME))
        self.turn_off(entity_id=self.LIGHT_NAME)


class Lantern(Lighting):

    def initialize(self):
        self.log('Initializing lantern switch')
        self.listen_state(self.activate,
                          'group.living_room_overheads',
                          old='off',
                          new='on')
        self.listen_state(self.deactivate,
                          'group.living_room_overheads',
                          old='on',
                          new='off')

    def deactivate(self, *args):
        self.log('deactivating lantern')
        self.turn_off('switch.lantern_switch')

    def activate(self, *args):
        self.log('activating lantern')
        self.turn_on('switch.lantern_switch')


class MovieTime(Lighting):

    def initialize(self):
        self.log("Initializing movie time automation")

        # trigger = 'media_player.apple_tv'
        self.trigger = 'binary_sensor.media_center_state'

        self.repeat_handler = None

        self.listen_state(self.start_movie_time_delayed,
                          self.trigger,
                          old='off',
                          new='on')
        self.listen_state(self.end_movie_time,
                          self.trigger,
                          old='on',
                          new='off')

        self.listen_state(self.movie_playing,
                          'media_player.apple_tv',
                          new='playing')
        self.listen_state(self.movie_paused,
                          'media_player.apple_tv',
                          old='playing',
                          new='paused')

        self.listen_state(self.end_movie_time,
                          'input_boolean.movie_lighting',
                          old='on',
                          new='off')

        self.listen_state(self.start_movie_time,
                          'input_boolean.movie_lighting',
                          old='off',
                          new='on')

    @property
    def movie_time_enabled(self):
        return self.get_state('input_boolean.movie_lighting') == 'on'

    @property
    def media_center_active(self):
        value = self.get_state(self.trigger) == 'on'
        self.log('media_center_active %s' % str(value))
        return value

    def start_movie_time(self, *args):
        if self.movie_time_enabled and self.media_center_active and (self.is_evening or self.is_late_night):
            self.log("Starting movie time")
            self.turn_fluxing_off()
            self.turn_on('scene.movie_paused')
            # self.repeat_handler = self.run_in(self.start_movie_time, 30)

    def start_movie_time_delayed(self, *args):
        # Add a delay to cover fluctuations in power level as media center elements start up.
        self.run_in(self.start_movie_time, 5)

    def movie_playing(self, *args):
        if self.movie_time_enabled and self.media_center_active and (self.is_evening or self.is_late_night):
            self.log('movie playing')
            self.turn_on('scene.movie_playing')

    def movie_paused(self, *args):
        self.log('%s|%s|%s' % (self.movie_time_enabled, self.media_center_active,  (self.is_evening or self.is_late_night)))
        if self.movie_time_enabled and self.media_center_active and (self.is_evening or self.is_late_night):
            self.log('movie paused')
            self.turn_on('scene.movie_paused')

    def end_movie_time(self, trigger, change, current, previous, *args):
        # Check playing state again, so we can reuse this method for the input_boolean.movie_lighting toggle
        if not self.media_center_active and (self.is_evening or self.is_late_night):
            self.log("Ending movie time")
            self.turn_fluxing_on()
            self.turn_on('scene.bright')
            # if self.repeat_handler is not None:
            #     self.cancel_timer(self.repeat_handler)


class Away(Lighting):

    def initialize(self):
        self.log("Initializing away state automation")

        self.listen_state(
            self.set_house_away, 'group.family', old='home', new='not_home')
        self.listen_state(
            self.set_house_away, 'group.family', old='on', new='off')

        self.listen_state(
            self.set_house_home, 'group.family', old='not_home', new='home')
        self.listen_state(
            self.set_house_home, 'group.family', old='off', new='on')


        self.run_daily(
            self.set_house_evening, self.evening_start_time)

        self.run_daily(
            self.set_house_night, self.evening_end_time)

    def turn_on_lights_with_timer(self, entity_id, minutes=10, *args):
        self.turn_on(entity_id)
        self.log(
            "Turned on {0}. {1} minutes and counting...".format(entity_id, minutes))

        self.run_in(
            self._turn_off_light_with_timer, minutes * 60, entity_id=entity_id)

    def _turn_off_light_with_timer(self, *args):
        # TODO: This seems silly, but I can't seem to call turn_off directly
        # and pass through the entity id.
        entity_id = args[0]['entity_id']
        self.log('Turning off {0}'.format(entity_id))
        self.turn_off(entity_id)

    def set_house_evening(self, *args):
        if self.get_state('input_boolean.lights_evening') == 'on':
            self.log("Turning on evening lighting")
            # self.turn_on('group.living_room')
            self.turn_on('scene.bright')

    def set_house_night(self, *args):
        if not self.is_occoupied:
            self.log("Turning off evening lighting")
            self.turn_off('group.living_room')

    def set_house_away(self, *args):
        self.log("Setting house to away mode")
        if not self.is_babysitter_mode:
            # interior
            self.turn_off('group.downstairs_lights')
            self.turn_off('group.upstairs_lights')
            self.turn_off('switch.fountain_switch')
            self.turn_off('group.christmas_lights')

            # thermostat
            self.call_service('climate/set_away_mode', away_mode=True)

        # exterior
        self.turn_off('switch.backyard_lights_switch')
        # self.turn_off('switch.fountain_switch_2')
        # self.turn_off('switch.irrigation_switch_6')

    def set_house_home(self, *args):
        self.log('Setting house to home mode')

        # thermostat
        self.call_service('climate/set_away_mode', away_mode=False)

        if self.is_evening:
            # interior
            self.turn_on('group.kitchen')
            self.turn_on('light.foyer')
            self.turn_on('light.front_porch')
            # exterior
            self.turn_on_lights_with_timer(
                entity_id='switch.backyard_lights_switch')

            if not self.is_babysitter_mode:
                self.turn_on('scene.bright')
                self.turn_on('light.dining_room')
                # self.turn_on('group.living_room')

        if self.is_late_night:
            self.turn_on_lights_with_timer(
                entity_id='switch.backyard_lights_switch')
            self.turn_on_lights_with_timer(
                entity_id='light.front_porch')
            self.turn_on('light.foyer')
            self.turn_on('switch.kitchen_island_switch')
