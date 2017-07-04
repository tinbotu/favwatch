# TwitterFavWatcher

## Overview

this is a bot that quickly detect the Favoritting of someone's Twitter account, and post it to a Slack and/or Lingr
![seq](https://github.com/tinbotu/favwatch/blob/media/seq.gif)


## Description

### how to work

1. Get someone's twitter favoritting via Twitter REST API
1. Take diff previous one
1. Post new one to Slack or Lingr via bot API


## Requirements

- Your Twitter account (<https://dev.twitter.com>)
- Notitication destination:: Slack or Lingr
- Python 3
    - venv
    - peewee
    - tweepy


## how to setup

1. clone this repo to some your directory

   ```sh
    $ mkdir -p ~/workspace
    $ git clone https://github.com/tinbotu/favwatch.git
   ```

1. copy configration file from a skeleton file

   ```sh
   $ cp settings.yml.skel settings.yml
   ```

1. CREATE YOUR TWITTER APP
    1. Go <https://apps.twitter.com/>
    2. Login or Join 
    3. Click **Create New App**
    4. Fill in the form
    5. Go to **Permissions** tab
    6. Set access to **read only**
    7. Go to **Keys and Access Tokens** tab
    8. Copy these to settings.yml ::  **Consumer Key, Consumer Secret, Access Token, Acces Token Secret**


4. setup your Webhook to your Slack (if necessary)
    1. Go https://YOUR_TEAM.slack.com/apps/A0F7XDUAZ-incoming-webhooks
    2. Click **Add Configration**
    3. Choose a channel or create, Click **Add Incoming WebHooks integration**
    4. Copy **Webhook URL** to settings.yml


5. setup your Lingr bot (if necessary)
    1. Go <http://lingr.com/developer>
    2. Click **create a new bot**
    3. Fill in the form and click **Create**
    4. Copy **Secret** to settings.yml
    5. Go http://lingr.com/room/YOUR_ROOM/manage_bots and click **invite a new bot**, invite bot created above


### first run

```sh
$ make setup
$ make run
```
at the first run, all recent favorites will post (such many). only difference will be posted from the next time.


## Author

Akira KUMAGAI <kumaguy@gmail.com>


## License

MIT
