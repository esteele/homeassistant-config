import appdaemon.plugins.hass.hassapi as hass
import time

def clean_list_param(param):
    return [p.strip() for p in param.split()]


def sonos_restore(kwargs):
    app = kwargs.get('app')
    app.log('Restoring normal Sonos operation')
    # app.log(str(kwargs))
    app.call_service("media_player/sonos_restore", with_group=True)
    volume = kwargs.get('volume')
    if volume is not None:
        app.call_service("media_player/volume_set",
                         entity_id=kwargs.get('output_entity'),
                         volume_level=volume)


def sonos_notify(app, message='', output_entity=''):
    """ Speak a notification message over one or more Sonos speakers.
        Resume prior state when done.
    """
    app.log('Playing notification on %s' % output_entity)
    try:
        volume = float(app.get_state(output_entity, 'volume_level'))
    except TypeError:
        volume = 40.0
    app.call_service("media_player/sonos_snapshot", with_group=True)

    app.call_service("media_player/play_media",
                     media_content_id="https://www.dropbox.com/s/qxm77j0kez4l55y/a-ubuntu%20Positive.ogg?dl=1",
                     entity_id=output_entity,
                     media_content_type='music')
    app.call_service("media_player/volume_set",
                     entity_id=output_entity,
                     volume_level=0.35)
    # XXX: This should really be handled by a timer, but it seems like a short
    # enough time to not be that big of a deal WRT threading.
    time.sleep(3)
    app.call_service("tts/google_say",
                     entity_id=output_entity,
                     language="en-uk",
                     message=message)
    # And sleep again to let the notification sound move through the queue.
    time.sleep(3)
    duration = app.get_state(output_entity, "media_duration") or 20
    if duration is not None:
        duration += 3
    app.log('Normal Sonos operation will be restored in %s seconds' % duration)
    app.run_in(sonos_restore, duration, app=app, volume=volume, output_entity=output_entity)


    # to_send = {'app':app,'output_entity':output_entity, 'message':message, 'volume': volume}
    # app.run_in(_say, 5, **to_send)
