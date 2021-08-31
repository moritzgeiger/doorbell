from soco import SoCo
import soco
import time
from dotenv import load_dotenv, find_dotenv
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
            sp.volume = 25
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
            sp.volume = 25
            sp.play_uri(url)
            time.sleep(playtime)
            sp.pause()
            sp.clear_queue()
            sp.add_multiple_to_queue(prev_queue)

    except KeyError:
        print(f'speaker {speaker} not found')


def send_email(homename, sender_email, receiver_email, password, port, signature, message, debug):
    """
    Compiles an Email with the email.mime library and sends it through a Google Mail smtp server.
    Takes in variables for the mail content [homename (str), lvl_results (dict), signature (str)]
    and settings to send the email [sender_email, receiver_email, password, port]
    There is a debug argument to test the email function despite a trigger isn't reached.
    """
    print('send email was called.')
    # check, if there is alert level 2 was reached in the checkpoints
    if debug: #or an email was received:
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
            msg['Subject'] = f"-Nachricht von Tuerklingel {now}"
        else:
            msg['Subject'] = f"-Nachricht von Tuerklingel -TEST- - {now}"
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
    else:
        print(f'There was no request via email.')
        print('Exit function without sending mail.')
