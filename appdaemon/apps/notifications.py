import appdaemon.appapi as appapi
from string import Template
import datetime
from utils import sonos_notify


class MorningAnnouncement(appapi.AppDaemon):

    def initialize(self):
        self.listen_state(self.morning_start_up,
                          'switch.kitchen_table_switch',
                          old='off',
                          new='on',
                          constrain_start_time='07:00:00',
                          constrain_end_time='09:00:00')

        # self.run_in(self.morning_start_up, 15)

    def morning_start_up(self, *args):
        """ Play the morning announcement over the kitchen sonos speakers.
        """
        self.log('triggering morning announcement')
        message = Template("Good morning. $date $weather $school")
        message = message.safe_substitute(date=self.today_date(),
                                          weather=self.weather_summary(),
                                          school=self.school_summary())
        self.log(message)
        sonos_notify(self, message=message, output_entity='media_player.kitchen')

    def _play_music(self, *args):
        self.log('triggering music')
        self.call_service('media_player/select_source',
                          entity_id='media_player.kitchen',
                          source='Classical AM')

    def today_date(self):
        """ Get today's date in the format "Tuesday, May 2nd"
        """
        def suffix(d):
            return 'th' if 11<=d<=13 else {1: 'st',2:'nd',3:'rd'}.get(d%10, 'th')

        def custom_strftime(format, t):
            return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))

        return custom_strftime("It's %A %B {S}.", datetime.datetime.now())

    def weather_summary(self):
        """ Get the day's simplified forecast: general weather, high, low temps
        """
        weather = {
            'low': int(float(self.get_state(
                'sensor.dark_sky_daily_low_apparent_temperature'))),
            'high': int(float(self.get_state(
                'sensor.dark_sky_daily_high_apparent_temperature'))),
        }
        # Clean up the weather forecast so it makes sense when read aloud.
        summary = self.get_state('sensor.dark_sky_hourly_summary')
        summary = summary.replace('cloudy ', 'cloudy skies ')
        summary = summary.replace('Clear ', 'clear skies ')
        summary = summary.replace('1 in.', '1 inch')
        summary = summary.replace('in.', 'inches')
        weather['summary'] = summary
        forecast = Template("Today's forecast calls for $summary, with a high of $high and a low of $low.")
        # self.log(forecast.safe_substitute(weather))
        return forecast.safe_substitute(weather)

    def school_summary(self):
        """ Get the school day from Google Calendar, use that to look up school specials
        """
        message = ''
        if self.get_state('calendar.is_school_day1') == 'on':
            message = "Today at school, day one. Molly has gym. Emma has library and technology."
        elif self.get_state('calendar.is_school_day2') == 'on':
            message = "Today at school, day two. Molly has art class. Emma has music class."
        elif self.get_state('calendar.is_school_day3') == 'on':
            message = "Today at school, day three. Molly has music class. Emma has gym."
        elif self.get_state('calendar.is_school_day4') == 'on':
            message = "Today at school, day four. Molly has gym. Emma has art class."
        elif self.get_state('calendar.is_school_day5') == 'on':
            message = "Today at school, day five. Molly has art class. Emma has music class."
        elif self.get_state('calendar.is_school_day6') == 'on':
            message = "Today at school, day six. Molly has music class and library. Emma has gym."

        return message
