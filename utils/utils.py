from soco import SoCo, snapshot
import soco
import time
import os
import datetime as dt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ssl
import smtplib


def play_song(speaker, url, playtime):
    """
    Takes in the string of a speaker name and a playable .mp3 URL file or radio station.
    Injects the song into the playlist and plays it on the designated speaker.
    """

    try:
        #find all devices and set the seeked one
        devices = {device.player_name: device for device in soco.discover()}
        sp = devices[speaker]
        uri = sp.avTransport.GetMediaInfo([("InstanceID", 0)]).get('CurrentURI')
        meta = sp.avTransport.GetMediaInfo([("InstanceID", 0)]).get('CurrentURIMetaData')
        play_mode = sp.get_current_transport_info()

        if play_mode.get('current_transport_state') == 'PLAYING':
            prev_vol = sp.volume
            if any(x in uri for x in ['radio', 'stream']):
                print('handling radio interruption.')
                # handle radio stations differently, they don't have .next()
                sp.volume = 25
                sp.play_uri(url)
                time.sleep(playtime)
                sp.stop()
                # sp.clear_queue()
                sp.volume = prev_vol
                sp.play_uri(uri, meta=meta)
                print('restored old radio state.')

            else:
                print('handling queue interruption.')
                prev_queue = sp.get_queue()
                play_mode = sp.get_current_transport_info()
                # save previous settings
                get_pos = int(sp.get_current_track_info().get('playlist_position')) # base is 1
                print(f'current queue pos: {get_pos}')
                get_seek = sp.get_current_track_info().get('position')
                print(f'current title pos: {get_seek}')

                # play the song
                print('injecting and playing song...')
                sp.volume = 25
                sp.play_uri(url)

                # set play time
                time.sleep(playtime)
                sp.stop()
                # sp.clear_queue()

                # get back to the old queue
                print('returning to old queue.')
                # sp.add_multiple_to_queue(prev_queue)
                sp.volume = prev_vol
                sp.play_from_queue(get_pos-1) # base is 0
                sp.seek(get_seek)
                print('restored old queue state.')

        else:
            print('playing song...')
            prev_queue = sp.get_queue()
            sp.volume = 25
            sp.play_uri(url)
            time.sleep(playtime)
            if any(x in uri for x in ['radio', 'stream']):
                print('restoring radio to player without playing.')
                sp.play_uri(uri)
                sp.stop()
            else:
                print('restoring old queue to player.')

    except KeyError:
        print(f'speaker {speaker} not found')


def send_email(homename, sender_email, receiver_email, password, port, signature, person, message, debug):
    """
    Compiles an Email with the email.mime library and sends it through a Google Mail smtp server.
    Takes in variables for the mail content [homename (str), lvl_results (dict), signature (str)]
    and settings to send the email [sender_email, receiver_email, password, port]
    There is a debug argument to test the email function despite a trigger isn't reached.
    """
    print('send email was called.')
    # check, if there is alert level 2 was reached in the checkpoints
    print('data was requested via mail')
    # init msg
    init = f"<p>{message}</p>"

    # Record the MIME types of text/html.
    text = MIMEMultipart('alternative')
    text.attach(MIMEText(init + signature, 'html', _charset="utf-8"))

    # compile email msg
    now = dt.datetime.now().strftime("%y-%m-%d %H:%M")
    msg = MIMEMultipart('mixed')

    # avoid automized email ruling by subject when testing
    if debug:
        msg['Subject'] = f"Klingelnachricht von {person} um {now}"
    else:
        msg['Subject'] = f"Klingelnachricht von {person} -TEST- {now}"
    msg['From'] = f'{homename} <{sender_email}>'
    msg['To'] = ','.join(receiver_email)

    # add all parts to msg
    msg.attach(text)

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

    print(f'successfully sent email to {receiver_email}')
