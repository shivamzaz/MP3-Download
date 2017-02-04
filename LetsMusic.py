#!/usr/bin/python

from __future__ import print_function
import os
import sys
import re
import readline
import eyed3
from bs4 import BeautifulSoup
import requests
# Version compatiblity
import sys
if (sys.version_info > (3, 0)):
    from urllib.request import urlopen
    from urllib.parse import quote_plus as qp
    raw_input = input
else:
    from urllib2 import urlopen
    from urllib import quote_plus as qp


def extract_videos(html):
    """
    Parses given html and returns a list of (Title, Link) for
    every movie found.
    """
    soup = BeautifulSoup(html, 'html.parser')
    pattern = re.compile(r'/watch\?v=')
    found = soup.find_all('a', 'yt-uix-tile-link', href=pattern)
    return [(x.text.encode('utf-8'), x.get('href')) for x in found]

def grab_albumart(search=''):
    search = qp(search)
    site = "https://www.google.com/search?site=&tbm=isch&source=hp&biw=1112&bih=613&q="+search+"&oq=backst&gs_l=img.3.0.0l10.1011.3209.0.4292.8.7.1.0.0.0.246.770.0j3j1.4.0..3..0...1.1.64.img..3.5.772.KyXkrVfTLT4#tbm=isch&q=back+street+boys+I+want+it+that+way"
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
    req = requests.get(site, headers=hdr)

    content = str(req.content)
    end =  content.find('jpg')
    start= content[:end].rfind('http')

    return content[start:end+3]


def list_movies(movies):
    for idx, (title, _) in enumerate(movies):
        yield '[{}] {}'.format(idx, title.decode('utf-8').encode(sys.stdout.encoding))


def search_videos(query):
    """
    Searches for videos given a query
    """
    response = urlopen('https://www.youtube.com/results?search_query=' + query)
    return extract_videos(response.read())

def query_and_download(search, has_prompts=True, is_quiet=False):
    """
    Queries the internet for given lyrics and downloads them into the current working directory.
    If has_prompts is False, will download first available song.
    If is_quiet is True, will run beautiful-soup in quiet mode. Prompts will also automatically be turned
                         off in quiet mode. This is mainly so that instantmusic can be run as a background process.
    Returns the title of the video downloaded from.
    """
    if not is_quiet:
        print('Searching...')

    available = search_videos(search)

    if not is_quiet:
        if not available:
            print('No results found matching your query.')
            sys.exit(2) # Indicate failure using the exit code
        else:
            if has_prompts:
                print('Found:', '\n'.join(list_movies(available)))

    # We only ask the user which one they want if prompts are on, of course
    if has_prompts and not is_quiet:
        choice = ''
        while choice.strip() == '':
            choice = raw_input('Pick one: ')
        title, video_link = available[int(choice)]

        prompt = raw_input('Download "%s"? (y/n) ' % title)
        if prompt != 'y':
            sys.exit()
    # Otherwise, just download the first in available list
    else:
        title, video_link = available[0]


    command_tokens = [
        'youtube-dl',
        '--extract-audio',
        '--audio-format mp3',
        '--audio-quality 0',
        '--output \'%(title)s.%(ext)s\'',
        'http://www.youtube.com/' + video_link]

    if is_quiet:
        command_tokens.insert(1, '-q')

    command = ' '.join(command_tokens)


    # Youtube-dl is a proof that god exists.
    if not is_quiet:
        print('Downloading')
    os.system(command)
    
    #Fixing id3 tags
    try:
        print ('Fixing id3 tags')
        list_name = title.split('-')
        artist=list_name[0]
        track_name = list_name[1]
        album_name=''
        try:
            try:
                audiofile = eyed3.load((title+'.mp3'))
            except:
                audiofile = eyed3.load((title+'.m4a')) 

            url = 'http://www.google.com/search?q='+qp(title)
            req = requests.get(url)
            response = req.content
            result=response
            link_start=result.find('http://www.metrolyrics.com')
            link_end=result.find('html',link_start+1)
            link = result[link_start:link_end+4]
            lyrics_html = link
            a = requests.get(lyrics_html)
            print (lyrics_html)
            html_doc=  a.content
            soup = BeautifulSoup(html_doc, 'html.parser')
            try:
                album_name = soup.find(id = "album-name-link").text
            except:
                print ('Cant get album name')
            try:
                raw_lyrics= (soup.findAll('p', attrs={'class' : 'verse'}))
                paras=[]
                test1=unicode.join(u'\n',map(unicode,raw_lyrics))

                test1= (test1.replace('<p class="verse">','\n'))
                test1= (test1.replace('<br/>',' '))
                test1 = test1.replace('</p>',' ')
                print (test1)
                audiofile.tag.lyrics.set(u''+test1 )
            except:
                print ('cant get lyrics')           


        except Exception as e: 
            print(e)
            print ('error getting album and lyrics')



        print (artist,track_name,album_name)
        artist=artist[:artist.find('[')].strip()
        track_name=track_name[:track_name.find('[')].strip()
        album_name=album_name[:album_name.find('[')].strip()

        audiofile.tag.artist=unicode(artist)
        audiofile.tag.title=unicode(track_name)
        audiofile.tag.album =unicode(album_name)

        search =  title[:-4]
        print ('Downloaidng album art..')
        image_link= grab_albumart(search)
        str = title
        str = unicode(str, errors='replace')
        title = str.encode('utf8')
        print ('Fixing '+title)
        eyed3.log.setLevel("ERROR")
        if audiofile.tag is None:
            audiofile.tag = eyed3.id3.Tag()
            audiofile.tag.file_info = eyed3.id3.FileInfo("foo.id3")
        response = requests.get(image_link).content
        imagedata = response

        audiofile.tag.images.set(0,imagedata,"image/jpeg",u"Album Art")
        audiofile.tag.save()
        print ('Fixed')
    except Exception as e: 
        print(e)
        print ('couldnt get album art')

    return title

def search_uses_flags(argstring, *flags):
    """
    Check if the given flags are being used in the command line argument string
    """
    for flag in flags:
        if (argstring.find(flag) != 0):
            return True
    return False

def main():
    """
    Run the program session
    """
    argument_string = ' '.join(sys.argv[1:])
    search = ''

    # No command-line arguments
    if not sys.argv[1:]:
        # We do not want to accept empty inputs :)
        while search == '':
            search = raw_input('Enter songname/ lyrics/ artist.. or whatever\n> ')
        search = qp(search)
        downloaded = query_and_download(search)

    # Command-line arguments detected!
    else:
        # No flags at all are specified
        if not search_uses_flags(argument_string, '-s', '-i', '-f', '-p', '-q'):
            search = qp(' '.join(sys.argv[1:]))
            downloaded = query_and_download(search)

        # No input flags are specified
        elif not search_uses_flags(argument_string, '-s', '-i', '-f'):
            # Default to -s
            lyrics = argument_string.replace('-p', '').replace('-q', '')
            search = qp(lyrics)
            downloaded = query_and_download(search, not search_uses_flags('-p'), search_uses_flags('-q'))

        # Some input flags are specified
        else:
            # Lots of parser-building fun!
            import argparse
            parser = argparse.ArgumentParser(description='Instantly download any song!')
            parser.add_argument('-p', action='store_false', dest='has_prompt', help="Turn off download prompts")
            parser.add_argument('-q', action='store_true', dest='is_quiet', help="Run in quiet mode. Automatically turns off prompts.")
            parser.add_argument('-s', action='store', dest='song', nargs='+', help='Download a single song.')
            parser.add_argument('-l', action='store', dest='songlist', nargs='+', help='Download a list of songs, with lyrics separated by a comma (e.g. "i tried so hard and got so far, blackbird singing in the dead of night, hey shawty it\'s your birthday).')
            parser.add_argument('-f', action='store', dest='file', nargs='+', help='Download a list of songs from a file input. Each line in the file is considered one song.')

            # Parse and check arguments
            results = parser.parse_args()

            song_list = []
            if results.song:
                song_list.append(qp(' '.join(results.song)))

            if results.songlist:
                songs = ' '.join(results.songlist)
                song_list.extend([qp(song) for song in songs.split(',')])

            if results.file:
                with open(results.file[0], 'r') as f:
                    songs = f.readlines()
                    # strip out any empty lines
                    songs = filter(None, (song.rstrip() for song in songs))
                    # strip out any new lines
                    songs = [qp(song.strip()) for song in songs if song]
                    song_list.extend(songs)

            prompt = True if results.has_prompt else False
            quiet = True if results.is_quiet else False

            downloads = []
            for song in song_list:
                downloads.append(query_and_download(song, prompt, quiet))

            print('Downloaded: %s' % ', '.join(downloads))

if __name__ == '__main__':
    main()
