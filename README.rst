=================
TwitterFavWatcher
=================


Overview
========

this is a bot that quickly detect the Favoritting of someone's Twitter account, and post it to the chat.


Description
===========

how to work
-----------

1. Get someone's twitter favoritting via Twitter REST API
2. Take diff previous one
3. Post new one to Slack or Lingr via bot API


Requirements
============

- Your Twitter account (dev.twitter.com)
- Notitication destination:: Slack or Lingr
- Python 3

  - venv
  - peewee
  - tweepy


how to setup
============

1. clone this repo to some directory
2. % cp settings.yml.skel settings.yml
3. CREATE YOUR TWITTER APP
4. setup your Webhook to your Slack
5. setup your Lingr bot (optional)
6. edit settings.yml and those apikeys
7. % make setup
8. % make run


Author
======

Akira KUMAGAI <kumaguy@gmail.com>


License
=======

MIT



