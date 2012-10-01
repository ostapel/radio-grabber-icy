import os, sys
import urllib
import urllib2
import re
import time
import traceback
import logging
import time
import getopt

config_txt = "config_grabber.txt"
save_path = 'd:\\temp\\mp3\\'
url = 'http://online-radioroks.tavrmedia.ua:8000/RadioROKS_256'

class RequestRadio:
    def __init__(self, url, attempts = 10):
        self.url = url
        self.attempts = attempts
        self.request = ''
        self.header = 'Icy-MetaData'
        self.header_index = 1
        self.mpstreeam = ''
        self.icy_int = 0
        self.data = ''
        self.radio_station_name = ''

    def show_info(self):
        log_both("Save to dir: {0}".format(save_path))
        log_both("Opening stream: {0}".format(url))

    def send_request(self):
        global save_path
        isSent = False
        for attempt in range(1, self.attempts):
            msg = "Sending request , attempt %d ..." % (attempt)
            print msg
            logging.debug(msg)
            try:
                self.request = urllib2.Request(url)
                self.request.add_header(self.header, self.header_index)
                opener = urllib2.build_opener()
                self.data=opener.open(self.request)
                self.icy_int = int(self.data.headers.getheader("icy-metaint"))
                radio_name = self.data.headers.getheader("icy-name")
                self.radio_station_name = strip_spec_symbols(radio_name)
                log_both("Radiostation name: {0}".format(radio_name))
                logging.warning("icy_int is %d", self.icy_int)
                isSent = True
                set_save_path(self.radio_station_name)
                self.show_info()
                createDirIfNeed(save_path)
                break
            except:
                logging.debug(traceback.format_exc())
                print traceback.format_exc()
                timeout = 10
                for time_wait in range(1, timeout):
                    log_both("Next attempt in {0} s...".format(timeout - time_wait))
                    time.sleep(1)

    def read_data(self, size):
        return self.data.read(size)

def init_logging():
    logging.basicConfig( filename='radio_grabber.log', format='%(asctime)s:%(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
    logging.info('Starting radio grabber')

def log_both(string):
    logging.info(string)
    print(string)

def set_save_path(radiostation_name):
    global save_path
    if radiostation_name not in save_path:
        save_path = os.path.join(save_path, radiostation_name)
        log_both("Allocating new folder for stream: {0}".format(save_path))

def main(argv):
    global url
    global save_path
    song = ""
    file = ""
    current_song = ""
    counter = 0
    char_len = 0
    init_logging()
    sys.stdout.encoding
    try:
      opts, args = getopt.getopt(argv,"u:s:",["url=","savedir="])
    except getopt.GetoptError:
      print 'radiograbebr.py -u <url> -s <save dir>'
      sys.exit(2)
    for opt, arg in opts:
      if opt in ('-u', '-url'):
        log_both("URL of radio: {0}".format(arg))
        url = arg
      elif opt in ("-s", "-savedir"):
         save_path = arg

    requestRadio = RequestRadio(url)
    requestRadio.send_request()
    while True:
        mpstream = ''
        try:
            mpstream = requestRadio.read_data(requestRadio.icy_int)
            char_len = requestRadio.read_data(1)
            logging.info("Char with metadata length is: [%s]", char_len)
        except:
            logging.debug(traceback.format_exc())
        if not char_len:
            logging.warning("!!! Char length is 0 !!!")
            requestRadio.send_request()
            mpstream += requestRadio.read_data(requestRadio.icy_int)
            char_len = requestRadio.read_data(1)
            logging.info("Char with metadata length is: [%s]", char_len)
        if char_len and char_len.__len__() > 0:
            num_byte_length = ord(char_len)
            logging.debug("Length is %d", num_byte_length)
            if num_byte_length > 0:
                length=num_byte_length * 16
                logging.info("\nReading %d bytes of metadata\n" , length)
                song = requestRadio.read_data(length)
                if song != current_song:
                    if file:
                        file.close()
                    song_title = splitSongTitle(song)
                    fullpath_file = getFullPath(song_title)
                    if not os.path.isfile(fullpath_file):
                        file = open(fullpath_file, 'wb')
                    else:
                        logging.info("File [%s] already exists, skipping...", fullpath_file)
                        print "File already exists, skipping it...\n"
                else:
                    logging.info("Still the same song...Skipping...\n")
                current_song = song

        try:
            if file:
                file.write(mpstream)
        except Exception:
            logging.debug(traceback.format_exc())

def createDirIfNeed(path, createNew = True):
    folders=[]
    while 1:
        path,folder=os.path.split(path)

        if folder!="":
            folders.append(folder)
        else:
            if path!="":
                folders.append(path)
            break

    folders.reverse()
    path_to_create = folders[0]
    for folder in folders[1:]:
        path_to_create = os.path.join(path_to_create, folder)
        if not os.path.isdir(path_to_create):
            os.mkdir(path_to_create)
            logging.info("Creating path %s", path_to_create)

def getFullPath(song):
    logging.info(song)
    print("Song: " + song)
    fullpath = os.path.join(save_path, song)
    fullpath_file = ''
    fullpath_file = fullpath + '.mp3'
    log_both("Capturing to:\n" + fullpath_file)
    return fullpath_file

def splitSongTitle(song):
    song_no_head = song[13:]
    song = strip_spec_symbols(song_no_head)
    logging.debug("Raw: " + song)
    song_stripped = song.replace("\\x00", "").strip()
    song = song_stripped.decode('string_escape', errors='ignore')
    st_return = song.decode('utf-8', errors='ignore').replace(u'\u0456', u'i').replace(u'\u0406', u'i')
    return st_return

def strip_spec_symbols(name):
    s = repr(name)
    song =  re.sub(r'["\'@=;&:%$|!~/\.]', '', s)
    return song

if __name__ == '__main__':
    main(sys.argv[1:])
