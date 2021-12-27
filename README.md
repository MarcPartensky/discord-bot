[![Docker](https://github.com/MarcPartensky/discord-bot/actions/workflows/docker-push.yml/badge.svg)](https://github.com/MarcPartensky/discord-bot/actions/workflows/docker-push.yml)

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

### Make a mongo account with a mongo cluster (100% Free)
[guide](https://docs.atlas.mongodb.com/tutorial/create-atlas-account)
[register](https://account.mongodb.com/account/register)
[youtube tutorial](https://www.youtube.com/watch?v=KKyag6t98g8)

### Make a .env file
Make a .env file with the following parameters.

```.env
DISCORD_TOKEN=
DISCORD_CLIENT_ID=
DISCORD_MONGO_CLUSTER=
DISCORD_MONGO_USERNAME=
DISCORD_MONGO_PASSWORD=
DISCORD_BOT_PORT=
DISCORD_BOT_HOST=
```

Other parameters can be added in the .env file but are not required.

```.env
WOLFRAM_ALPHA_ID=
FACEBOOK_MAIL=
FACEBOOK_PASSWORD=
FACEBOOK_MAIL_2=
FACEBOOK_PASSWORD_2=
FACEBOOK_MAIL_MISCORD=
FACEBOOK_PASSWORD_MISCORD=
MISCORD_DASHBOARD_USERNAME=
MISCORD_DASHBOARD_PASSWORD=
PYGITHUB_TOKEN=
GITHUB_TOKEN=
CAPTCHA_WEBSITE_KEY=
CAPTCHA_SECRET_KEY=
LEEKWARS_USERNAME=
```

## Option 1 :Run with Docker

### Then run:

```sh
docker run --env-file .env marcpartensky/discord-bot
```

Stop with:
```sh
docker stop discord-bot
```

Clean with:
```sh
docker container rm discord-bot
```

## Option 2: Build the docker image with docker-compose once the source code is cloned
```
docker-compose up -d discord-bot-prod --remove-orphans --build
```

## Option 3: Build it yourself

**Download python3.8 (Tested in 3.8.2)**
- Download from the official website (recommended): https://www.python.org/

OR
- Download with homebrew for Mac
    - Go to homebrew website and download by typing their command: https://brew.sh/
    - Then download python3.8 by typing into terminal: brew install python3.8

OR
- Download with apt for linux in ubuntu

OR
- Download with chocolatey in windows

**Download the repo by typing:**
- git clone https://github.com/MarcPartensky/discord-bot

**Go into the new repo by typing:**
- cd discord-bot

**Use a virtual environment in python (optional but highly recommended)**
To do so type:
- pip3.8 install virtualenv  # install virtualenv
- virtualenv -p python3.8 venv # create a virtual environment named `venv`
- source venv/bin/activate # activate your virtual environment, to deactivate type 'deactivate'


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
