# Discord bot
A discord bot who obeys me.

# Short presentation

This is a discord bot in python that does everything i tell it to do.
I added cool features to it:

**APIs**
wikipedia, translations, memes, insults

**Machine learning for vulgarity evaluations**
- accept all languages (check command)

**Music support (uses youtube-dl)**
- play music from youtube urls
- queue system
- rating system for skipping
- accepts playlists url
...
Soon:
- save playlists to reuse later

**Bank and games system**
- play rock/papers/scissors to win coins
- play heads or tails
Soon:
Casino system to play all types of games


**Admin commands (Need to install the project to use them and change config folder, see the section)**
- mute and kick people from voice channel (as long as wanted)
- ban, kick people
- promote, demote people
- clear chat
...


**Basic commands**
- say hi
- see top role, roles, permissions
- tell date, hour
...

**Sell your commands.**
- choose commands prices

**and lots of other things...**

**More info**
- Databases: mongodb, sqlite
- Hosted by heroku

# To use my bot in your server 

Go to:
*https://discord.com/api/oauth2/authorize?client_id=703347349623144549&permissions=8&scope=bot*

# To install the project to run your own bot

**Download python3.8 (Tested in 3.8.2)**
- Download from the official website (recommended): https://www.python.org/
OR
- Download with homebrew (for mac or windows) 
    - Go to homebrew website and download by typing their command: https://brew.sh/
    - Then download python3.8 by typing into terminal: brew install python3.8

**Make a folder to download the repo (use cd, ls, mkdir in linux) (optional)**
For instance to create a project in root:
- cd ~
- mkdir DiscordBot
- cd discordbot

**Download the repo by typing:**
- git clone https://github.com/MarcPartensky/discord-bot-esclave

**Go into the new repo by typing:**
- cd esclave

**Use a virtual environment in python (optional but highly recommended)**
To do so type:
- pip3.8 install virtualenv  #install virtualenv
- virtualenv esclave #create a virtual environment named esclave (you can name it however you want)
- source esclave/bin/activate #activate your virtual environment, to deactivate type 'deactivate'


**Download librairies by typing:**
- pip install requirements.txt (if using virtualenv)

OR
- pip3.8 install requirements.txt (if not using virtualenv, this will install packages globally in machine)


**You are almost good to go you just need to change credentials.py and config.py files to run your own discord bot**
to learn more: https://discordpy.readthedocs.io/en/latest/discord.html

you might need to change the 'masters' list with your own discord id to have admin commands

**Finally start the program by typing**
- python main.py (if using virtualenv)

OR
- python3.8 main.py (if not using virtualenv)

**Deactivate virtual environment after use (if using virtualenv) by typing:**
- deactivate

 
# Host your own bot version on Heroku for free
If you want to host the bot later on i recommand this tutorial video of tech with tim on youtube:

*https://www.youtube.com/watch?v=BPvg9bndP1U*


# Learn more about discord bots in python
Here are some good playlists to get started in discord bots in python:

- Playlist of Tech with Tim:
*https://www.youtube.com/watch?v=xdg39s4HSJQ&list=PLzMcBGfZo4-kdivglL5Dt-gY7bmdNQUJu*

- Playlist of Lucas:
*https://www.youtube.com/watch?v=nW8c7vT6Hl4&list=PLW3GfRiBCHOhfVoiDZpSz8SM_HybXRPzZ*
