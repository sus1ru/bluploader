#! /usr/bin/env python3

"""NOTE: READ DOCUMENTATION BEFORE USAGE.

Usage:
    bluploader.py (-h | --help)
    bluploader.py upload [--media <media>]
    [--config <config>][--imgbb <imgbb> --bluapi <bluapi> --tmdb <tmdb> --torrentdir <torrentdir>]
    [--autotype <autotype> --userid <userid> --anon <anon>  --stream <stream> --txtoutput <txtoutpt> --autoupload <autoupload> --font <font> --compress <compress_png>]


    Options:
      -h --help     Show this screen.
     --media <media> can be a single file or directory
     --config ; -x <config> commandline overwrites config
     --imgbb <imgbb> imgbb api key
     --bluapi <bluapi> blutopia api key
     --tmdb <tmdb> tmdb api key
     --userid <userid> blutopia userid
     --torrentdir <torrentdir> where to save torrent files You can set to temp to save to a tempdir.
     --txtoutput <txtoutput> save info on upload, returns uguu.se link auto deletes in 24hours
     --autoupload <autotype> upload to blutopia yes or no
     --autotype <autotype> try to automate finding type of upload yes or no
     --stream <stream> is it stream friendly 0 for no, 1 for yes
     --anon <anon>  anon upload 0 for no, 1 for yes
     --font <font> font for mtn thumbnail
     --compress <compress_png> compress images requires oxipng yes or no


"""


import requests
from bs4 import BeautifulSoup
import subprocess
from docopt import docopt
from pathlib import Path
import json
import os
from guessit import guessit
from imdb import IMDb
ia = IMDb()
import pickle
import subprocess
import tempfile
import configparser
config = configparser.ConfigParser(allow_no_value=True)

#TODO
#mal


#torrentdir tempfolder
def get_mediainfo(path,output):
    output = open(output, "a+")
    media=subprocess.run(['mediainfo', path],stdout=output)


def createconfig(arguments):
    try:
        configpath=arguments.get('--config')
        config.read(configpath)

    except:
        print("something went wrong")
        return arguments


    if arguments['--imgbb']==None:
        arguments['--imgbb']=config['api']['imgbb']
    if arguments['--bluapi']==None:
        arguments['--bluapi']=config['api']['bluapi']
    if arguments['--tmdb']==None:
        arguments['--tmdb']=config['api']['tmdb']
    if arguments['--torrentdir']==None:
        arguments['--torrentdir']=config['general']['torrentdir']
    if arguments['--autotype']==None:
        arguments['--autotype']=config['general']['autotype']
    if arguments['--anon']==None:
        arguments['--anon']=config['general']['anon']
    if arguments['--stream']==None:
        arguments['--stream']=config['general']['stream']
    if arguments['--anon']==None:
        arguments['--anon']=config['general']['anon']
    if arguments['--userid']==None:
        arguments['--userid']=config['general']['userid']
    if arguments['--txtoutput']==None:
        arguments['--txtoutput']=config['general']['txtoutput']
    if arguments['--autoupload']==None:
        arguments['--autoupload']=config['general']['autoupload']
    if arguments['--media']==None:
        arguments['--media']=config['general']['media']
    if arguments['--font']==None:
        arguments['--font']=config['general']['font']
    if arguments['--compress']==None and config['general']['compress']=="yes":
        arguments['--compress']=config['general']['compress']
    return arguments


def createimages(path,basename,arguments):
    #uploading
    dir = tempfile.TemporaryDirectory()
    screenshot="mtn -f "+ arguments["--font"]+ " -o .png -w 0 -s 400 -I " +path +" -O " +dir.name
    os.system(screenshot)
    url='https://api.imgbb.com/1/upload?key=' + arguments['--imgbb']
    text=tempfile.NamedTemporaryFile()
    textinput= open(text.name,"w+")



    #delete largest pic
    max=0
    delete=""
    for filename in os.listdir(dir.name):
       filename=dir.name +'/'+filename
       temp=os.path.getsize(filename)
       if(temp>max):
            max=temp
            delete=filename
    os.remove(delete)
    os.chdir(dir.name)

    if arguments['--compress']=="=yes":
        for filename in os.listdir(dir.name):
            compress="oxipng -o 6 -r --strip safe "+ filename
            os.system(compress)



    for filename in os.listdir(dir.name):
       filename=dir.name+'/'+filename
       image=filename
       image = {'image': open(image,'rb')}
       upload=requests.post(url=url,files=image)
       upload=upload.json()['data']['url_viewer']
       upload=requests.post(url=upload)
       link = BeautifulSoup(upload.text, 'html.parser')
       link = link.find('input',{'id' :'embed-code-5'})
       link=link.attrs['value']+" "
       textinput.write(link)
    textinput.close()
    textoutput= open(text.name,"r")
    #text=textoutput.read()
    return textoutput.read()


def getBasedName(path):
    basename=Path(path).stem
    return basename
def setCat(format):
    if format=="Movie":
        return "1"
    if format=="TV":
        return "2"


def create_upload_form(arguments,path):
    print(path)
    output=tempfile.NamedTemporaryFile(suffix='.txt')
    basename=getBasedName(path)
    torrentpath=tempfile.NamedTemporaryFile()
    torrent=create_torrent(path,basename,arguments,torrentpath)
    if Path(path).is_dir():
        path = str(next(Path(path).glob('*/')))
    imdbid = getimdb(path)
    format = setType(path,arguments)


    tmdbid=IMDBtoTMDB(imdbid.movieID,format,arguments)

    form = {'imdb' : imdbid.movieID,
            'name' : getTitle(path),
            'description' : createimages(path,basename,arguments),
            'category_id' : setCat(format),
            'tmdb': tmdbid,
            'type_id': setTypeID(path,arguments),
            'resolution_id' : setResolution(path),
            'user_id' : arguments["--userid"],
            'anonymous' : arguments["--anon"],
            'stream'    : arguments["--stream"],
            'sd'        : is_sd(path),
            'tvdb'      : '0',
            'igdb'  : '0' ,
            'mal' : '0'

            }




    #send temp paste
    if arguments['--txtoutput']=="yes":
        mediapath=tempfile.NamedTemporaryFile()
        media=get_mediainfo(path,mediapath.name)
        with open(output.name, 'w') as f:
            for key, value in form.items():
                f.write('%s:\n\n%s\n\n' % (key, value))

        with open(output.name, 'a+') as outfile:
            outfile.write('%s:\n\n' % ('media:'))
            #Open each file in read mode
            with open(mediapath.name) as infile:
                outfile.write(infile.read())

        output = {'file': open(output.name,'r')}
        post=requests.post(url="https://uguu.se/api.php?d=upload-tool",files=output)
        print(post.text)

    if arguments["--autoupload"]=="yes":
        torrent = {'torrent': open(torrent,'rb')}
        torrenturl="https://blutopia.xyz/api/torrents/upload?api_token=" + arguments["--bluapi"]
        upload=requests.post(url=torrenturl,files=torrent, data=form)
        print(upload.text)



def create_torrent(path,basename,arguments,torrentpath):
   if arguments["--torrentdir"]=="temp":
       torrent= "dottorrent -p -t https://blutopia.xyz/announce/9a054cbdee59fe2f129cf5f07e9bd65b "+ path +"  "+ torrentpath.name
       output=torrentpath.name
   else:
       torrent= "dottorrent -p -t https://blutopia.xyz/announce/9a054cbdee59fe2f129cf5f07e9bd65b "+ path +" "+arguments["--torrentdir"]
       output= '/home/main/Downloads/Seeding/Torrents/' + basename + '.torrent'
   os.system(torrent)
   return output

def IMDBtoTMDB(imdbid,format,arguments):

  url="https://api.themoviedb.org/3/find/tt" + str(imdbid) +"?api_key="  +arguments['--tmdb']+"e&language=en-US&external_source=imdb_id"
  list=requests.get(url)
  if(format=="TV"):
       format='tv_results'
  if(format=="Movie"):
       format='movie_results'
  print(url)


  id=list.json()[format]
  id=id[0]
  id=id['id']
  return id




def getimdb(path):
   details=guessit(path)
   title = details['title']
   if 'year' in details:
        title = "{} {}".format(title, details['year'])
   results = IMDb().search_movie(title)
   if len(results) == 0:
        print("Unable to find imdb")
        id = input("Enter imdb just what comes after tt: ")
        id=IMDb().get_movie(id)
   else:
       id=IMDb().search_movie(title)[0]
   return id














def getTitle(path):
    basename=os.path.basename(path)
    basename=os.path.splitext(basename)[0]
    basename=basename.replace("."," ")
    return basename

def setTypeID(path,arguments):
    if arguments["--autotype"]=="yes":
        details=guessit(path)
        source = details['source']
        remux=details.get('other')


        if (source=="Blu-ray" or source=="HD-DVD" or source=="Ultra HD Blu-ray") and remux==None:
            source = '1'
        elif (source=="Blu-ray" or source=="HD-DVD" or source=="Ultra HD Blu-ray") and remux!=None:
            source = '3'
        elif (source=="Web" or source=="HD-DVD" or source=="Ultra HD Blu-ray") and remux!=None:
            source = '4'
        elif source=="Analog HDTV" or source=="HDTV" or source=="Ultra HDTV" or source=="TV":
            source = '6'
    else:
        print(path,"\n")
        print("FULL_DISC = '1' REMUX = '3' ENCODE = '12' WEBDL = '4' WEBRIP= '5' HDTV= '6'","\n")
        source = input("Enter your Number ")
    return source


def setResolution(path):
   details=guessit(path)
   resolution = details['screen_size']
   if resolution=="2160p":
        resolution="1"
   elif resolution=="1080p":
        resolution="2"
   elif resolution=="1080i":
       resolution="3"
   elif resolution=="720p":
       resolution="5"
   elif resolution=="576p":
       resolution="6"
   elif resolution=="576i":
       resolution="7"
   elif resolution=="480p":
       resolution="8"
   elif resolution=="480i":
       resolution="9"
   elif resolution=="8640p":
       resolution="10"
   elif resolution=="4320p":
      resolution="11"
   else:
      resolution="10"
   return resolution

def is_sd(path):
    details=guessit(path)
    resolution = details['screen_size']
    if resolution=="2160p" or resolution=="1080p" or resolution=="1080i" or resolution=="720p" or resolution=="8640p" or resolution=="4320p":
      resolution="0"
    else:
      resolution="1"
    return resolution



def setType(path,arguments):
    if arguments["--autotype"]=="yes":
        details=guessit(path)
        format = details['type']
        if(format=="episode"):
            format = 'TV'
        else:
            format = 'Movie'
    else:
        print(path,"\n")
        print("What type of file are you uploading","\n")
        format = input("Enter TV or Movie: ")
    return format




if __name__ == '__main__':
    arguments = docopt(__doc__, version='Blu Uploader')
    if arguments['upload']:
        arguments=createconfig(arguments)
        if os.path.isdir(arguments['--media'])==False:
            create_upload_form(arguments,arguments['--media'])
            quit()
        for entry in os.scandir(arguments['--media']):
            path=arguments['--media']+entry.name
            print(path)
            create_upload_form(arguments,path)