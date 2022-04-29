"""Termcast - Liam Masters (2022)"""
import glob
import os
import time

import feedparser
import requests
import vlc
from picotui.defs import C_BLUE, C_WHITE
from picotui.screen import Screen
from picotui.widgets import (
    ACTION_CANCEL,
    ACTION_OK,
    ACTION_PREV,
    Dialog,
    WButton,
    WLabel,
    WListBox,
)


class TermCast:
    """A terminal-based podcast player from RSS feeds"""

    def __init__(self):
        self.show_list = []
        self.feed_list = []
        self.show = None
        self.episode = None
        self.download_link = ""

        self.state = []
        self.screen = None
        self.result = None

        self.media_player = None
        self.listen_time = 0

    def _get_feeds(self):
        """Download RSS feeds defined in source list"""
        print("Downloading feeds...")

        self.feed_list = []
        with open("./sources.txt", "r", encoding="utf-8") as file:
            for source in file.readlines():
                retries = 0
                parsed = False
                while retries < 3 and not parsed:
                    res = requests.get("https://" + source.rstrip("\n"))
                    if res.status_code == 200:
                        self.feed_list.append(feedparser.parse(res.text))
                        parsed = True
                    else:
                        retries += 1
                        time.sleep(3)
            file.close()

        self.show_list = []
        for feed in self.feed_list:
            self.show_list.append(feed.feed.title)

    def _show_list_state(self):
        """Draw the list of shows for selection"""
        self.screen.attr_color(C_WHITE, C_BLUE)
        self.screen.cls()
        self.screen.attr_reset()

        if self.result == ACTION_CANCEL:
            self.state.pop(0)
            return

        self.show = self.feed_list[0]
        frame = Dialog(3, 3, 60, 20, title="Termcast")
        frame.add(1, 1, "Shows:")

        shows_widget = WListBox(50, 16, self.show_list)

        def show_changed(shows):
            self.show = self.feed_list[shows.choice]

        shows_widget.on("changed", show_changed)
        frame.add(1, 2, shows_widget)

        select_button = WButton(8, "Select")
        frame.add(2, 18, select_button)
        select_button.finish_dialog = ACTION_OK

        exit_button = WButton(8, "Exit")
        frame.add(12, 18, exit_button)
        exit_button.finish_dialog = ACTION_CANCEL

        self.result = frame.loop()
        self.state.append(self._episode_list_state)
        self.state.pop(0)

    def _episode_list_state(self):
        """Draw the list of episodes for the selected show"""
        if self.result == ACTION_CANCEL:
            self.state.pop(0)
            return

        frame = Dialog(3, 3, 60, 20, title="Termcast")
        episodes = self.show.entries
        self.episode = episodes[0]

        titles = []
        for episode in episodes:
            titles.append(episode.title)

        frame.add(1, 1, "Episodes:")

        episode_list = WListBox(50, 16, titles)

        def episode_changed(e_list):
            self.episode = episodes[e_list.choice]

        episode_list.on("changed", episode_changed)
        frame.add(1, 2, episode_list)

        select_button = WButton(8, "Select")
        frame.add(2, 18, select_button)
        select_button.finish_dialog = ACTION_OK

        back_button = WButton(8, "Back")
        frame.add(12, 18, back_button)
        back_button.finish_dialog = ACTION_PREV

        self.result = frame.loop()
        self.state.append(self._player_state)
        self.state.pop(0)

    def _handle_play_pause(self, button, frame):
        """Handle play/pause commands when the button is pressed"""
        if button.t == "Play":
            self.media_player.play()
            if self.media_player.get_time() < 1000:
                self.media_player.set_time(self.listen_time)
            button.t = "Pause"
        else:
            self.media_player.pause()
            button.t = "Play"
        button.redraw()
        time.sleep(0.3)
        self.screen.attr_color(C_WHITE, C_BLUE)
        self.screen.cls()
        self.screen.attr_reset()
        frame.redraw()

    def _handle_stop(self):
        """Handle stop commands when returning to the show list"""
        self.media_player.stop()

    def _handle_skip(self, skip_time):
        """Handle skips back/forward in time"""
        new_time = self.media_player.get_time() + skip_time * 1000

        if new_time <= 0:
            self.media_player.set_time(0)
        elif new_time < self.media_player.get_length():
            self.media_player.set_time(new_time)

    def _get_listen_time(self):
        """Get the time listened to an eipsode from a file"""
        self.listen_time = 0
        files = glob.glob("./.temp/*")
        if "./.temp/" + self.episode.title + ".dat" in files:
            with open(
                "./.temp/" + self.episode.title + ".dat", "r", encoding="utf-8"
            ) as file:
                self.listen_time = int(file.readline().rstrip("\n"))
                file.close()

    def _write_listen_time(self):
        """Write time listened to an episode to a file when it's stopped"""
        listen_time = self.media_player.get_time()
        if listen_time > self.media_player.get_length() - 3 * 60 * 1000:
            listen_time = 0  # Reset listen time if it's within the last 3 minutes
        try:
            os.mkdir(".temp")
        except FileExistsError:
            pass
        with open(
            ".temp/" + self.episode.title + ".dat", "w+", encoding="utf-8"
        ) as file:
            file.write(str(listen_time))

    def _player_state(self):
        """Handle playing the selected episode"""
        self.screen.attr_color(C_WHITE, C_BLUE)
        self.screen.cls()
        self.screen.attr_reset()

        if self.result == ACTION_CANCEL:
            self.state.pop(0)
            return
        elif self.result == ACTION_PREV:
            self.state.append(self._show_list_state)
            self.state.pop(0)
            return

        for link in self.episode.links:
            if link.type == "audio/mpeg":
                download_link = link.href
                break

        frame = Dialog(3, 3, 80, 7, title="Termcast")

        self.media_player = vlc.MediaPlayer(download_link)

        self._get_listen_time()

        play_pause = WButton(8, "Play")
        play_pause.on(
            "click",
            lambda _: self._handle_play_pause(play_pause, frame),
        )
        frame.add(2, 2, play_pause)

        skip_back = WButton(8, "-10")
        skip_back.on("click", lambda _: self._handle_skip(-10))
        frame.add(12, 2, skip_back)

        skip_forward = WButton(8, "+10")
        skip_forward.on("click", lambda _: self._handle_skip(10))
        frame.add(22, 2, skip_forward)

        shows_button = WButton(8, "Shows")
        shows_button.on("click", lambda _: self._handle_stop())
        frame.add(32, 2, shows_button)
        shows_button.finish_dialog = ACTION_CANCEL

        title = WLabel(self.episode.title, w=76)
        frame.add(2, 5, title)

        self.result = frame.loop()

        self._write_listen_time()

        self.state.append(self._show_list_state)
        self.state.pop(0)

        self.result = ACTION_OK

    def main(self):
        """Main function to run the player state"""
        self._get_feeds()

        self.screen = Screen()
        self.state.append(self._show_list_state)

        try:
            self.screen.init_tty()
            self.screen.enable_mouse()
            while len(self.state) > 0:
                self.state[0]()
        finally:
            self.screen.cls()
            self.screen.goto(0, 50)
            self.screen.cursor(True)
            self.screen.disable_mouse()
            self.screen.deinit_tty()
