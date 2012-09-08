import os, sys
import urllib
import urllib2
import re
import time
import traceback
import logging

config_txt = "config_grabber.txt"
save_path = 'd:\\temp\\mp3\\'
url = 'http://online-radioroks.tavrmedia.ua:8000/RadioROKS_256'

def init_logging():
    logging.basicConfig( filename='radio_grabber.log', format='%(asctime)s:%(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
    logging.info('Starting radio grabber')

def read_config():
    if os.path.isfile(config_txt):
        file_conf = open(config_txt, "r")
        if file_conf:
            url = file_conf.readline()
            save_path = file_conf.readline()
            file_conf.close()

def main():
    song = ""
    file = ""
    current_song = ""
    counter = 0
    init_logging()
    read_config()
    sys.stdout.encoding
    logging.info("Save to dir: %s", save_path)
    print("Save to dir: %s" % save_path)
    logging.info("Opening stream: %s",  url)
    print("Opening stream: %s" % url)
    createDirIfNeed(save_path)
    request = urllib2.Request(url)
    request.add_header('Icy-MetaData','1')
    opener = urllib2.build_opener()
    data=opener.open(request)
    icy_int = int(data.headers.getheader("icy-metaint"))
    if icy_int == 0:
        logging.warning("icy_int is 0")
        return
    while True:
        mpstream = ''
        try:
            mpstream = data.read(icy_int)
            char_len = data.read(1)
            logging.info("Char with metadata length is: [%s]", char_len)
        except Exception:
            logging.debug(traceback.format_exc())
        if not char_len:
            logging.warning("!!! Char len is 0 !!!")
            request = urllib2.Request(url)
            request.add_header('Icy-MetaData','1')
            opener = urllib2.build_opener()
            data=opener.open(request)
            icy_int = int(data.headers.getheader("icy-metaint"))
            mpstream += data.read(icy_int)
            char_len = data.read(1)
            logging.info("Char with metadata length is: [%s]", char_len)
        if char_len and char_len.__len__() > 0:
            num_byte_length = ord(char_len)
            logging.debug("Length is %d, icy_int is %d", num_byte_length, int(data.headers.getheader("icy-metaint")))
            if num_byte_length > 0:
                len=num_byte_length * 16
                logging.info("\nReading %d bytes of metadata\n" , len)
                song = data.read(len)
                if song != current_song:
                    if file:
                        file.close()
                    song_title = splitSongTitle(song)
                    fullpath_file = getFullPath(song_title)
                    file = open(fullpath_file, 'wb')
                else:
                    logging.info("Still the same song...Skipping...")
                current_song = song

        try:
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
    logging.info("Capturing to:\n" + fullpath_file)
    print("Capturing to \n" + fullpath_file)
    return fullpath_file

def splitSongTitle(song):
    song_no_head = song[13:]
    s = repr(song_no_head)
    song =  re.sub(r'["\'@=;&:%$|!~/\.]', '', s)
    logging.debug("Raw: " + song)
    song_stripped = song.replace("\\x00", "").strip()
    song = song_stripped.decode('string_escape', errors='ignore')
    st_return = song.decode('utf-8', errors='ignore').replace(u'\u0456', u'i')
    return st_return
##    .decode("utf-8")

if __name__ == '__main__':
    main()
