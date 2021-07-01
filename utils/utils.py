from soco import SoCo
import soco
import time


def play_song(speaker, url, playtime):
    """
    Takes in the string of a speaker name and a playable .mp3 URL file or radio station.
    Injects the song into the playlist and plays it on the designated speaker.
    """

    try:
        #find all devices and set the seeked one
        devices = {device.player_name: device for device in soco.discover()}
        sp = devices[speaker]
        prev_queue = sp.get_queue()
        play_mode = sp.get_current_transport_info()

        if play_mode.get('current_transport_state') == 'PLAYING':
            # save previous settings
            prev_vol = sp.volume
            get_pos = int(sp.get_current_track_info().get(
                'playlist_position'))  # base is 1
            get_seek = sp.get_current_track_info().get('position')

            # play the song
            print('injecting and playing song...')
            sp.volume = 15
            sp.add_uri_to_queue(url, position=get_pos + 1)
            sp.next()
            sp.play()

            # set play time
            time.sleep(playtime)

            # get back to the old queue
            print('returning to old queue.')
            sp.clear_queue()
            sp.add_multiple_to_queue(prev_queue)
            sp.volume = prev_vol
            sp.play_from_queue(get_pos - 1)  # base is 0
            sp.seek(get_seek)

        else:
            print('playing song...')
            sp.volume = 15
            sp.play_uri(url)
            time.sleep(playtime)
            sp.pause()
            sp.clear_queue()
            sp.add_multiple_to_queue(prev_queue)

    except KeyError:
        print(f'speaker {speaker} not found')
