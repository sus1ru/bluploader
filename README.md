Requirements:
    Python3
    requests
    BeautifulSoup
    docopt
    guessit
    IMDb
    pickle
    configparser
    dottorrent
    dottorrent-cli

mtn:https://gitlab.com/movie_thumbnailer/mtn 
binaries avalible 

mediainfo





    
   
    
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
