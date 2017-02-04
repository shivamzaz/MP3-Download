# forthwith download any song!

> This is so cool!

## Installation by [Pip](http://pip.readthedocs.org/en/stable/installing/)
For Python 2.7

```bash
$ sudo pip install LetsMusic
```

For Python 3.4

```bash
$ sudo pip3 install LetsMusic
```

### Note:
You would also need `libav` to download in `.mp3` format.

#### On Mac Os X
##### Installation by [Brew](https://brew.sh)
```bash
 $ brew install libav
 ```
 
#### On Ubuntu 

```bash
 $ sudo apt-get install libav-tools 
```
#### On Windows
>[See this](https://github.com/yask123/Instant-Music-Downloader/issues/19) 

## Usage

```bash
$ LetsMusic 
```

```zsh
>> Enter songname/ lyrics/ artist.. or whatever

i tried so hard and got so far 

>>Downloaded Linkin Park - In The End
```

```zsh
>> Enter songname/ lyrics/ artist.. or whatever

another turning point a fork stuck in the road

>>Downloaded Green Day - Good Riddance
```

```zsh
>> Enter songname/ lyrics/ artist.. or whatever

yeh hosla kaise jhuke

>>Downloaded Yeh Hausla Kaise Jhuke - Salim-Sulaiman
```
### Options

```
❯ LetsMusic -h                                                   
usage: LetsMusic [-h] [-p] [-q] [-s SONG [SONG ...]]
                    [-l SONGLIST [SONGLIST ...]] [-f FILE [FILE ...]]

Instantly download any song!

optional arguments:
  -h, --help            show this help message and exit
  -p                    Turn off download prompts
  -q                    Run in quiet mode. Automatically turns off prompts.
  -s SONG [SONG ...]    Download a single song.
  -l SONGLIST [SONGLIST ...]
                        Download a list of songs, with lyrics separated by a
                        comma (e.g. "i tried so hard and got so far, blackbird
                        singing in the dead of night, hey shawty it's your
                        birthday).
  -f FILE [FILE ...]    Download a list of songs from a file input. Each line
                        in the file is considered one song.
```

