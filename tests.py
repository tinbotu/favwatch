#!bin/python
# -*- coding: utf-8 -*-
# vim: ts=4 sw=4 sts=4 ff=unix ft=python expandtab

import unittest
import datetime
import os
import tweepy
import peewee

from favwatch import (
    TwitterFavWatch,
    PostLingr,
    PostSlack,
)

from FavwatchLogModel import (
    favwatch_log,
    FavLog,
)


class TestTwitterFavWatch(unittest.TestCase):
    target_screen_name = ["Twitter"]
    database = "tmp.sqlite"
    fav = None

    def setUp(self):
        self.c = TwitterFavWatch(self.database)

    def tearDown(self):
        os.remove(self.database)

    def test__get_favorites(self):
        fav = self.c.get_favorites(self.target_screen_name)
        fav2 = self.c.get_favorites(self.target_screen_name)
        self.assertEqual(fav2, [])
        for t in fav:
            self.assertIsInstance(t.text, str)
            self.assertIsInstance(t.created_at, datetime.datetime)
            self.assertEqual(t.id, int(t.id_str))

        self.assertTrue(self.c.fav_exists(self.target_screen_name[0], fav[0].id_str))

    def test_get_api_limit(self):
        limit = self.c.get_api_limit()
        self.assertIsInstance(limit, dict)
        self.assertGreater(limit["reset"], 1)


class TestPostLingr(unittest.TestCase):
    room = 'lingr'
    bot = 'botname'
    text = '本文'
    bot_secret = 'xlfRmrQS64WGIY0c18qNO9LLUzX'
    calculated_bot_verifier = 'ed4914cc299846a41c84beebb89e3b8c6ce02c5b'

    def setUp(self):
        self.l = PostLingr()

    def test_build_say_payload(self):
        payload = self.l.build_say_payload(room=self.room, bot=self.bot, text=self.text, apikey=self.bot_secret)
        self.assertEqual(payload["bot_verifier"], self.calculated_bot_verifier)
        self.assertEqual(payload["room"], self.room)
        self.assertEqual(payload["text"], self.text)
        self.assertEqual(payload["bot"], self.bot)

    def test_is_enabled(self):
        self.l.dry_run = True
        self.l.settings["lingr"]["enabled"] = False
        r = self.l.say(self.text)
        self.assertFalse(r)

    def test_say(self):
        self.l.dry_run = True
        pass


class TestPostSlack(unittest.TestCase):
    webhook_url = "https://hooks.slack.com/services"
    channel = "#general"
    text = '本文'

    def setUp(self):
        self.s = PostSlack()

    def test_is_enabled(self):
        self.s.dry_run = True
        self.s.settings["slack"]["enabled"] = False
        r = self.s.say(self.text)
        self.assertFalse(r)

if __name__ == '__main__':
    unittest.main()
