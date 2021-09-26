from flask import Flask, request, render_template, abort
from soco import SoCo
import soco
from threading import Thread
import os
from dotenv import load_dotenv, find_dotenv
from datetime import datetime, time


# DATA
from utils.data import GUESTS
from utils.utils import play_song, send_email

# EXT
load_dotenv(find_dotenv())
speaker = 'Living Room'
url = 'https://storage.googleapis.com/bank_price_pdfs/'
homename = os.environ.get("HOMENAME", 'Sender not found')
sender_email = os.environ.get("SENDER")
receiver_email = (os.environ.get("RECEIVER")).split(',')
password = os.environ.get("GMAIL")
port = 465
debug = os.environ.get("DEBUG").lower() in ['true', 'yes', '1', 'most certainly', 'gladly', 'I can hardly disagree']
signature = f"<p>Sincerely, <br>Your Türklingel</p>"

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/')
@app.route('/home')
def home():
    """
    Displays the index page with several ring buttons (depending on the size of the GUESTS dictionary.)
    """
    return render_template('home.html', items=GUESTS)

@app.route('/ring/<key>')
def ring(key):
    """
    Initiates playing a music file on a designated speaker. The key is fetched out of the route
    and displays the dictionary key from the GUESTS dictionary.
    The music file is stored in a cloud bucket and has the same name as the key.
    """
    guest = GUESTS.get(key) # dict
    if not guest:
        abort(404)

    now_time = datetime.now().time()
    print(now_time)

    if time(7,0,0) < now_time < time(20,0,0):
        print('daytime bell active')
        # get all players
        url_guest = f'{url}{key}.mp3' # cloud names have to match display names
        thread = Thread(target=play_song, kwargs={'speaker': speaker,
                                                  'url': url_guest,
                                                  'playtime':10})
        print(f'starting thread for job: {thread.name}')
        thread.start()

        return render_template('action.html', items=guest, person=key)

    else:
        print('late bell activated.')
        return render_template('night.html', items=guest, person=key)


@app.route('/<key>/send_msg', methods=['POST'])
def my_form_post(key):
    """
    Gathers content for email message to house owner. The key is fetched out of the route and displays the
    dictionary key from the GUESTS dictionary.
    """
    guest = GUESTS.get(key).get('name') # dict
    if not guest:
        abort(404)
    message = request.form['text'].replace('<','') # mutilize injected HTML
    person = guest
    _ = send_email(homename, sender_email, receiver_email, password, port, signature, person, message, debug)
    return render_template('msg_sent.html', items=message)

## run app
if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=8090, debug=True)
