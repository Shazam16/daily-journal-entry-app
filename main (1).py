"""
Personal Diary - Kivy Android App
Write, save, edit, search, and timestamp daily journal entries.
"""

import os
import sqlite3
from datetime import datetime

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty
from kivy.metrics import dp
from kivy.utils import platform
from kivy.uix.popup import Popup


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------

def get_db_path():
    """Return a writable path for the sqlite database, on Android or desktop."""
    if platform == "android":
        from android.storage import app_storage_path  # noqa
        base = app_storage_path()
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "diary.db")


DB_PATH = get_db_path()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            body TEXT NOT NULL,
            mood TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def add_entry(title, body, mood):
    now = datetime.now().isoformat(timespec="seconds")
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO entries (title, body, mood, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
        (title, body, mood, now, now),
    )
    conn.commit()
    conn.close()


def update_entry(entry_id, title, body, mood):
    now = datetime.now().isoformat(timespec="seconds")
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE entries SET title=?, body=?, mood=?, updated_at=? WHERE id=?",
        (title, body, mood, now, entry_id),
    )
    conn.commit()
    conn.close()


def delete_entry(entry_id):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM entries WHERE id=?", (entry_id,))
    conn.commit()
    conn.close()


def get_entries(search=None):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    if search:
        cur.execute(
            "SELECT id, title, body, mood, created_at, updated_at FROM entries "
            "WHERE title LIKE ? OR body LIKE ? ORDER BY created_at DESC",
            (f"%{search}%", f"%{search}%"),
        )
    else:
        cur.execute(
            "SELECT id, title, body, mood, created_at, updated_at FROM entries "
            "ORDER BY created_at DESC"
        )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_entry(entry_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, title, body, mood, created_at, updated_at FROM entries WHERE id=?",
        (entry_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row


# ---------------------------------------------------------------------------
# UI definition (KV language)
# ---------------------------------------------------------------------------

KV = """
#:import dp kivy.metrics.dp

<EntryRow@BoxLayout>:
    orientation: "vertical"
    size_hint_y: None
    height: dp(86)
    padding: dp(12), dp(8)
    spacing: dp(2)
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [dp(12)]
    entry_id: 0
    title_text: ""
    preview_text: ""
    date_text: ""
    mood_text: ""

    BoxLayout:
        size_hint_y: None
        height: dp(24)
        Label:
            text: root.title_text if root.title_text else "Untitled"
            color: 0.2, 0.18, 0.15, 1
            font_size: "16sp"
            bold: True
            halign: "left"
            valign: "middle"
            text_size: self.size
            shorten: True
        Label:
            text: root.mood_text
            font_size: "18sp"
            size_hint_x: None
            width: dp(28)

    Label:
        text: root.preview_text
        color: 0.45, 0.42, 0.38, 1
        font_size: "13sp"
        halign: "left"
        valign: "top"
        text_size: self.size
        shorten: True
        max_lines: 2

    Label:
        text: root.date_text
        color: 0.6, 0.56, 0.5, 1
        font_size: "11sp"
        halign: "left"
        valign: "bottom"
        text_size: self.size
        size_hint_y: None
        height: dp(16)


<ListScreen>:
    name: "list"
    canvas.before:
        Color:
            rgba: 0.97, 0.96, 0.93, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: "vertical"
        padding: dp(16)
        spacing: dp(10)

        BoxLayout:
            size_hint_y: None
            height: dp(40)
            Label:
                text: "Journal"
                font_size: "26sp"
                bold: True
                color: 0.2, 0.18, 0.15, 1
                halign: "left"
                valign: "middle"
                text_size: self.size
            Label:
                text: root.entry_count_text
                color: 0.55, 0.51, 0.45, 1
                font_size: "13sp"
                halign: "right"
                valign: "middle"
                text_size: self.size
                size_hint_x: None
                width: dp(80)

        BoxLayout:
            size_hint_y: None
            height: dp(44)
            spacing: dp(8)
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [dp(10)]
            TextInput:
                id: search_box
                hint_text: "Search entries..."
                multiline: False
                background_normal: ""
                background_active: ""
                background_color: 1, 1, 1, 1
                foreground_color: 0.2, 0.18, 0.15, 1
                padding: dp(12), dp(12)
                on_text: root.on_search(self.text)

        ScrollView:
            BoxLayout:
                id: entries_box
                orientation: "vertical"
                size_hint_y: None
                height: self.minimum_height
                spacing: dp(8)
                padding: 0, dp(4), 0, dp(80)

        Widget:
            size_hint_y: None
            height: 0

    BoxLayout:
        size_hint: None, None
        size: dp(60), dp(60)
        pos: root.width - dp(76), dp(16)
        canvas.before:
            Color:
                rgba: 0.55, 0.42, 0.30, 1
            Ellipse:
                pos: self.pos
                size: self.size
        Button:
            text: "+"
            font_size: "30sp"
            bold: True
            background_normal: ""
            background_color: 0, 0, 0, 0
            color: 1, 1, 1, 1
            on_release: root.new_entry()


<EditScreen>:
    name: "edit"
    canvas.before:
        Color:
            rgba: 0.97, 0.96, 0.93, 1
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: "vertical"
        padding: dp(16)
        spacing: dp(10)

        BoxLayout:
            size_hint_y: None
            height: dp(44)
            spacing: dp(8)
            Button:
                text: "< Back"
                size_hint_x: None
                width: dp(80)
                background_normal: ""
                background_color: 0.88, 0.85, 0.79, 1
                color: 0.2, 0.18, 0.15, 1
                on_release: root.go_back()
            Label:
                text: root.date_label
                color: 0.55, 0.51, 0.45, 1
                font_size: "12sp"
            Button:
                text: "Delete"
                size_hint_x: None
                width: dp(80)
                background_normal: ""
                background_color: 0.82, 0.55, 0.5, 1
                color: 1, 1, 1, 1
                opacity: 1 if root.entry_id else 0
                disabled: not root.entry_id
                on_release: root.confirm_delete()

        TextInput:
            id: title_input
            hint_text: "Title (optional)"
            multiline: False
            size_hint_y: None
            height: dp(48)
            font_size: "18sp"
            bold: True
            background_normal: ""
            background_color: 1, 1, 1, 1
            foreground_color: 0.2, 0.18, 0.15, 1
            padding: dp(12), dp(12)

        BoxLayout:
            size_hint_y: None
            height: dp(44)
            spacing: dp(6)
            Label:
                text: "Mood:"
                color: 0.45, 0.42, 0.38, 1
                size_hint_x: None
                width: dp(50)
            ToggleButton:
                id: mood_happy
                text: "😊"
                group: "mood"
                font_size: "20sp"
                background_normal: ""
                background_color: (0.85,0.78,0.6,1) if self.state=="down" else (1,1,1,1)
            ToggleButton:
                id: mood_neutral
                text: "😐"
                group: "mood"
                font_size: "20sp"
                background_normal: ""
                background_color: (0.85,0.78,0.6,1) if self.state=="down" else (1,1,1,1)
            ToggleButton:
                id: mood_sad
                text: "😔"
                group: "mood"
                font_size: "20sp"
                background_normal: ""
                background_color: (0.85,0.78,0.6,1) if self.state=="down" else (1,1,1,1)
            ToggleButton:
                id: mood_excited
                text: "🤩"
                group: "mood"
                font_size: "20sp"
                background_normal: ""
                background_color: (0.85,0.78,0.6,1) if self.state=="down" else (1,1,1,1)
            ToggleButton:
                id: mood_angry
                text: "😡"
                group: "mood"
                font_size: "20sp"
                background_normal: ""
                background_color: (0.85,0.78,0.6,1) if self.state=="down" else (1,1,1,1)

        ScrollView:
            TextInput:
                id: body_input
                hint_text: "What's on your mind today?"
                font_size: "15sp"
                background_normal: ""
                background_color: 1, 1, 1, 1
                foreground_color: 0.2, 0.18, 0.15, 1
                padding: dp(12), dp(12)
                size_hint_y: None
                height: max(self.minimum_height, dp(300))

        Button:
            text: "Save entry"
            size_hint_y: None
            height: dp(50)
            background_normal: ""
            background_color: 0.55, 0.42, 0.30, 1
            color: 1, 1, 1, 1
            bold: True
            on_release: root.save()
"""


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------

MOOD_MAP = {
    "happy": "😊",
    "neutral": "😐",
    "sad": "😔",
    "excited": "🤩",
    "angry": "😡",
}


class ListScreen(Screen):
    entry_count_text = StringProperty("")

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self, search=None):
        box = self.ids.entries_box
        box.clear_widgets()
        rows = get_entries(search)
        self.entry_count_text = f"{len(rows)} entr{'y' if len(rows) == 1 else 'ies'}"

        if not rows:
            from kivy.uix.label import Label
            box.add_widget(
                Label(
                    text="No entries yet. Tap + to write your first one."
                    if not search
                    else "No entries match your search.",
                    color=(0.55, 0.51, 0.45, 1),
                    size_hint_y=None,
                    height=dp(60),
                )
            )
            return

        for row in rows:
            entry_id, title, body, mood, created_at, updated_at = row
            dt = datetime.fromisoformat(created_at)
            date_text = dt.strftime("%a, %b %d %Y · %I:%M %p")
            preview = " ".join(body.split())
            widget = Builder.template("EntryRow")
            widget.entry_id = entry_id
            widget.title_text = title or ""
            widget.preview_text = preview
            widget.date_text = date_text
            widget.mood_text = MOOD_MAP.get(mood, "")
            widget.bind(on_touch_down=self._make_touch_handler(entry_id))
            box.add_widget(widget)

    def _make_touch_handler(self, entry_id):
        def handler(instance, touch):
            if instance.collide_point(*touch.pos):
                self.open_entry(entry_id)
                return True
            return False
        return handler

    def on_search(self, text):
        self.refresh(search=text.strip() if text.strip() else None)

    def new_entry(self):
        edit_screen = self.manager.get_screen("edit")
        edit_screen.load_entry(None)
        self.manager.transition.direction = "left"
        self.manager.current = "edit"

    def open_entry(self, entry_id):
        edit_screen = self.manager.get_screen("edit")
        edit_screen.load_entry(entry_id)
        self.manager.transition.direction = "left"
        self.manager.current = "edit"


class EditScreen(Screen):
    date_label = StringProperty("")
    entry_id = None

    def load_entry(self, entry_id):
        self.entry_id = entry_id
        self.ids.title_input.text = ""
        self.ids.body_input.text = ""
        for tb in (
            self.ids.mood_happy,
            self.ids.mood_neutral,
            self.ids.mood_sad,
            self.ids.mood_excited,
            self.ids.mood_angry,
        ):
            tb.state = "normal"

        if entry_id is None:
            self.date_label = "New entry"
            return

        row = get_entry(entry_id)
        if row is None:
            self.date_label = "New entry"
            return

        _id, title, body, mood, created_at, updated_at = row
        self.ids.title_input.text = title or ""
        self.ids.body_input.text = body or ""

        mood_widget = {
            "happy": self.ids.mood_happy,
            "neutral": self.ids.mood_neutral,
            "sad": self.ids.mood_sad,
            "excited": self.ids.mood_excited,
            "angry": self.ids.mood_angry,
        }.get(mood)
        if mood_widget:
            mood_widget.state = "down"

        created = datetime.fromisoformat(created_at)
        updated = datetime.fromisoformat(updated_at)
        if created_at == updated_at:
            self.date_label = created.strftime("%a, %b %d %Y · %I:%M %p")
        else:
            self.date_label = (
                f"Created {created.strftime('%b %d, %I:%M %p')} · "
                f"edited {updated.strftime('%b %d, %I:%M %p')}"
            )

    def get_selected_mood(self):
        for key, attr in (
            ("happy", "mood_happy"),
            ("neutral", "mood_neutral"),
            ("sad", "mood_sad"),
            ("excited", "mood_excited"),
            ("angry", "mood_angry"),
        ):
            if self.ids[attr].state == "down":
                return key
        return None

    def save(self):
        title = self.ids.title_input.text.strip()
        body = self.ids.body_input.text.strip()
        mood = self.get_selected_mood()

        if not body:
            self._show_message("Write something before saving.")
            return

        if self.entry_id is None:
            add_entry(title, body, mood)
        else:
            update_entry(self.entry_id, title, body, mood)

        self.go_back()

    def confirm_delete(self):
        if self.entry_id is None:
            return

        content = BoxLayout(orientation="vertical", spacing=dp(10), padding=dp(16))
        from kivy.uix.label import Label
        content.add_widget(Label(text="Delete this entry? This can't be undone."))

        buttons = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(44))
        cancel_btn = Button(text="Cancel")
        delete_btn = Button(text="Delete", background_color=(0.82, 0.55, 0.5, 1))
        buttons.add_widget(cancel_btn)
        buttons.add_widget(delete_btn)
        content.add_widget(buttons)

        popup = Popup(title="Confirm delete", content=content, size_hint=(0.8, 0.3))

        def do_cancel(*a):
            popup.dismiss()

        def do_delete(*a):
            delete_entry(self.entry_id)
            popup.dismiss()
            self.go_back()

        cancel_btn.bind(on_release=do_cancel)
        delete_btn.bind(on_release=do_delete)
        popup.open()

    def _show_message(self, text):
        content = BoxLayout(orientation="vertical", padding=dp(16))
        from kivy.uix.label import Label
        content.add_widget(Label(text=text))
        popup = Popup(title="", content=content, size_hint=(0.8, 0.25))
        popup.open()
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: popup.dismiss(), 1.2)

    def go_back(self):
        self.manager.transition.direction = "right"
        self.manager.current = "list"


from kivy.uix.button import Button  # noqa: E402  (used in confirm_delete)


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

class DiaryApp(App):
    def build(self):
        init_db()
        Builder.load_string(KV)
        sm = ScreenManager()
        sm.add_widget(ListScreen(name="list"))
        sm.add_widget(EditScreen(name="edit"))
        return sm


if __name__ == "__main__":
    DiaryApp().run()
