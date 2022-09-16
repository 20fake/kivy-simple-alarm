from logging import root
from tkinter import Widget
from kivymd.app import MDApp
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.pickers import MDTimePicker
from kivymd.uix.pickers import MDDatePicker
from kivy.clock import Clock
from kivymd.uix.list import TwoLineAvatarIconListItem, ILeftBodyTouch
from kivymd.uix.list import IconRightWidget
from kivymd.uix.selectioncontrol import MDCheckbox
from kivy.core.window import Window
import pygame
import sqlite3
import datetime

Window.size = (350, 600)


class ListItemWithCheckBox(TwoLineAvatarIconListItem):
    """Check Box and Trash Icon function"""


class LeftCheckBox(ILeftBodyTouch, MDCheckbox):
    """Custom Left CheckBox"""


class HomeScreen(MDScreen):
    name = "homescreen"

    def delete_item(self):
        # icon = IconRightWidget()
        print("FUNGSI UNTUK HAPUS WIDGET LIST")
        # self.ids.list.child.remove_widget(self)


class RingingScreen(MDScreen):
    name = "ringingscreen"


class AddReminderScreen(MDScreen):
    name = "addreminderscreen"

    pygame.init()
    sound = pygame.mixer.Sound("alarm.mp3")
    volume = 0

    time_dialog = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        conn = sqlite3.connect('reminder.db')  # Hubungkan database
        c = conn.cursor()
        c.execute("""CREATE TABLE if not exists reminder(title TEXT, alarm TEXT, date TEXT)""")
        conn.commit()
        conn.close()

        self.time_dialog = MDTimePicker()  # inisialisasi
        self.date_dialog = MDDatePicker()  # inisialisasi
        Clock.schedule_interval(self.alarm, 1)  # schedule the alarm function for every one second

    def time_picker(self):
        self.time_dialog.bind(on_save = self.schedule)
        self.time_dialog.open()

    def schedule(self, *args):
        self.ids.alarm_timed.text = str(self.time_dialog.time)

    def save_date(self, instance, value, date_range):
        self.ids.date_time.text = str(value)

    def date_picker(self):
        self.date_dialog.bind(on_save = self.save_date)
        self.date_dialog.open()

    def save_reminder(self, *args):
        self.ids.title_add.text = str(self.ids.title_add.text)
        self.ids.alarm_timed.text = str(self.time_dialog.time)
        self.ids.date_time.text = str(self.ids.date_time.text)

        conn = sqlite3.connect("reminder.db")
        c = conn.cursor()
        c.execute("INSERT INTO reminder (title, alarm, date) VALUES (:first, :second, :third)",
                {
                    'first':self.ids.title_add.text,
                    'second':self.ids.alarm_timed.text,
                    'third':self.ids.date_time.text,
                })

        conn.commit()
        conn.close()

        self.manager.get_screen('homescreen').ids['container'].add_widget(
                    TwoLineAvatarIconListItem(text = self.ids.title_add.text,
                    secondary_text = self.ids.alarm_timed.text + " " + self.ids.date_time.text
                    )
                )
        
        self.ids.title_add.text = "" # Reempty the add title text field
        self.ids.alarm_timed.text = "" # Reempty the add time text field
        self.ids.date_time.text = "" # Reempty the add time text field

        self.manager.transition.direction = "right"  # set the direction of the transition before moving to next
        self.manager.current = "homescreen"  # move to the home screen

    def alarm(self, *args):
        current_time = datetime.datetime.now().strftime("%H:%M:%S %Y-%m-%d")

        conn = sqlite3.connect("reminder.db")
        c = conn.cursor()
        c.execute("SELECT alarm || ' ' || date AS today FROM reminder")
        records = c.fetchall()
        conn.commit()
        conn.close()

        alarms = [record[0] for record in records]

        if str(current_time) in alarms:
            self.start()

    def start(self, *args):
        """Changing screen while the alarm start ringing"""
        self.manager.transition.direction = "left"
        self.manager.current = "ringingscreen"
        
        """Playing sound"""
        self.sound.play(-1)
        self.set_volume()

    def set_volume(self, *arfgs):
        self.volume += 0.05
        if self.volume < 1.0:
            Clock.schedule_once(self.set_volume, 10)
            self.sound.set_volume(self.volume)
            print(self.volume)
        else:
            self.sound.set_volume(1)


class CustomScreenManager(MDScreenManager):
    """This is Screen Manager"""


class MervisApp(MDApp):
    def build(self):
        screen = Builder.load_file('ui.kv')
        return screen

    def on_start(self):
        conn = sqlite3.connect('reminder.db')
        c = conn.cursor()
        records = c.execute("SELECT * FROM reminder").fetchall()
        conn.commit()
        conn.close()

        homesc = HomeScreen()

        if records != []:
            for i in records:
                reminder_items = TwoLineAvatarIconListItem(
                    IconRightWidget(
                        icon = 'trash-can-outline',
                        on_release = lambda x: homesc.delete_item()
                    ),
                    text = i[0], secondary_text = i[1]
                    )
                self.root.get_screen('homescreen').ids.container.add_widget(reminder_items)


if __name__ == "__main__":
    MervisApp().run()