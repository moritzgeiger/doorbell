from flask import Flask, render_template, abort
from soco import SoCo
import soco
from threading import Thread

# DATA
from utils.data import GUESTS
from utils.utils import play_song

# EXT
speaker = 'Office'
url = 'https://storage.googleapis.com/bank_price_pdfs/klingelstreich.mp3'

app = Flask(__name__)
app.config["DEBUG"] = True

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', items=GUESTS)


@app.route('/ring/<key>')
def ring(key):
    guest = GUESTS.get(key)
    if not guest:
        abort(404)

    # get all players
    thread = Thread(target=play_song, kwargs={'speaker': speaker,
                                              'url':url,
                                              'playtime':5})
    print(f'starting thread for job: {thread.name}')
    thread.start()

    return render_template('action.html', items=guest)

## run app
if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0', port=8090, debug=True)
