#! bin/python
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 sts=4 ff=unix ft=python expandtab

import datetime
import requests
import sys
import signal
import time
import traceback
import json
import yaml
import hashlib
import tweepy
import peewee
import emoji


from FavwatchLogModel import (
    favwatch_log,
    FavLog,
)


class Config(object):
    """ Read configration from a file and retain """
    _filename = "settings.yml"
    _settings = None

    @property
    def settings(self):
        if self._settings is not None:
            return self._settings
        with open(self._filename, "rb") as fp:
            self._settings = yaml.safe_load(fp)
        return self._settings


class TwitterFavWatch(Config):
    """ Get the user's twitter favorites and retrive diff with persistence """
    dry_run = False
    api = None

    def __init__(self, sqlite_file='favwatch_log.sqlite') -> None:
        auth = tweepy.OAuthHandler(self.settings["twitter"]["consumer_key"], self.settings["twitter"]["consumer_secret"])
        auth.set_access_token(self.settings["twitter"]["access_token"], self.settings["twitter"]["access_token_secret"])
        self.api = tweepy.API(auth, timeout=15)
        favwatch_log.initialize(peewee.SqliteDatabase(sqlite_file, journal_mode='WAL'))
        favwatch_log.create_tables([FavLog], True)

    def get_favorites(self, targets: list) -> list:
        newfav = list()

        for target in targets:
            try:
                fav = self.api.favorites(target, count=200)

                if len(fav) > 0:
                    fav.reverse()
                    newfav.extend(self.get_new_favorites_and_save(target_screen_name=target, fav=fav))
            except (tweepy.error.TweepError, ):
                traceback.print_exc()

        return newfav

    def fav_exists(self, target_screen_name: str, id_str: str) -> bool:
        exists = None
        try:
            FavLog.get(FavLog.fav_by_screen_name == target_screen_name and FavLog.id_str == id_str)
            exists = True
        except peewee.DoesNotExist:
            exists = False
        return exists

    def get_new_favorites_and_save(self, target_screen_name: str, fav: list) -> list:
        newfav = list()
        for f in fav:
            with favwatch_log.transaction():
                if not self.fav_exists(target_screen_name, f.id_str):
                    s = FavLog(
                        fav_by_screen_name=target_screen_name,
                        screen_name=f.user.screen_name,
                        name=f.user.name,
                        text=f.text,
                        id_str=f.id_str,
                        fav_created_at=f.created_at)
                    s.save()
                    f.fav_by_screen_name = target_screen_name
                    newfav.append(f)

            if not self.dry_run:
                favwatch_log.commit()
            else:
                favwatch_log.rollback()

        return newfav

    def get_api_limit(self) -> dict:
        # {'limit': 75, 'remaining': 41, 'reset': 1498754760}
        try:
            return self.api.rate_limit_status()['resources']['favorites']['/favorites/list']
        except:
            return {}



class PostLingr(Config):
    """ Post a message to Lingr """
    _endpoint_url = "http://lingr.com/api/room/say"
    dry_run = False

    def __init__(self) -> None:
        pass

    def build_say_payload(self, room: str, bot: str, text: str, apikey: str) -> dict:
        # some emoji confuse lingr
        try:
            demojed = emoji.demojize(text)
        except:
            demojed = text

        return {
            'room': room,
            'bot': bot,
            'text': demojed,
            'bot_verifier': hashlib.sha1(bot.encode("ascii") + apikey.encode("ascii")).hexdigest(),
        }

    def say(self, message: str) -> bool:
        if not self.settings.get("lingr") or not self.settings["lingr"].get("enabled"):
            return False
        if type(message) is not str:
            return False
        payload = self.build_say_payload(
            room=self.settings["lingr"]["room"],
            bot=self.settings["lingr"]["bot_id"],
            text=message,
            apikey=self.settings["lingr"]["bot_secret"]
        )
        if not self.dry_run:
            r = requests.post(self._endpoint_url, data=payload, timeout=30)
            return (r.status_code == requests.codes.ok)
        return False


class PostSlack(Config):
    """ Post a message to Slack WebHook """
    dry_run = False

    def build_say_payload(self, channel: str, text: str) -> str:
        return json.dumps({
            'channel': channel,
            'text': text,
        })

    def say(self, message: str) -> bool:
        if not self.settings.get("slack") or not self.settings["slack"].get("enabled"):
            return False
        if type(message) is not str:
            return False
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        payload = "payload=" + self.build_say_payload(channel=self.settings["slack"]["slack_channel"], text=message)
        if not self.dry_run:
            r = requests.post(self.settings["slack"]["slack_webhook_url"], headers=headers, data=payload, timeout=30)
            return (r.status_code == requests.codes.ok)

        return False



class Run(Config):
    """ runner """
    verbose = False

    def terminate_handler(self, signal, frame):
        sys.exit(0)

    def __init__(self) -> None:
        if sys.platform != 'win32':
            signal.signal(signal.SIGINT, self.terminate_handler)
        if self.settings["global"].get("verbose"):
            self.verbose = True
        self.lingr = PostLingr()
        self.slack = PostSlack()


    def run(self) -> None:
        timestamp_str = datetime.datetime.now().strftime('%H:%M:%S')
        targets = self.settings["global"]["targets"]
        fav = TwitterFavWatch()

        try:
            newfavs = fav.get_favorites(targets)

            if self.verbose:
                remain = fav.get_api_limit()
                print("%d (%d sec)" % (remain.get("remaining"), time.time()-int(remain.get("reset"))))

            for i in newfavs:
                f = ("%s %s likes: %s @%s %s https://twitter.com/%s/status/%s" %
                     (timestamp_str, i.fav_by_screen_name, i.user.name, i.user.screen_name, i.text, i.user.screen_name, i.id_str))
                print(f)
                self.lingr.say(f)
                self.slack.say(f)
        except (requests.exceptions.ConnectTimeout, ):
            print("%s Timeout" % timestamp_str)

        except:
            print(timestamp_str)
            traceback.print_exc()
            if not self.settings["global"]["continue_with_ignore_exception"]:
                raise

        # print(".", end="")
        wait_sec = self.settings["twitter"]["wait_sec"] * len(self.settings["global"]["targets"])
        time.sleep(wait_sec)



if __name__ == '__main__':
    r = Run()
    print("hit Ctrl-c to exit.")
    while True:
        r.run()

    sys.exit(1)
