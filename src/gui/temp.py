import os
import winsound
import sqlite3
from collections import namedtuple
from PIL import ImageOps, Image
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.utils import platform
from kivy.uix.anchorlayout import AnchorLayout
from kivy_garden.xcamera import XCamera
from pyzbar import pyzbar
from pyzbar.pyzbar import ZBarSymbol
from plyer import notification

DATABASE_PATH = "inventory.db"

kv_string = """
<ZBarCam>:
    BoxLayout:
        orientation: 'vertical'
        XCamera:
            id: camera
            play: True
            resolution: root.resolution
        Label:
            id: label
            size_hint_y: None
            height: '48dp'
            text: ''
"""

class ZBarCam(AnchorLayout, App):
    resolution = ListProperty([640, 480])
    symbols = ListProperty([])
    symbol = namedtuple("symbol", ["type", "data"])
    code_types = ListProperty(set(pyzbar.ZBarSymbol))

    def build(self):
        Builder.load_string(kv_string)
        self.init_database()
        Clock.schedule_once(lambda dt: self._setup())
        return super(ZBarCam, self).build()

    def on_xcamera(self, instance, value):
        self._setup()

    def _setup(self):
        if self.xcamera is not None:
            self._remove_shoot_button()
            self.xcamera.bind(on_camera_ready=self._on_camera_ready)

            if self.xcamera._camera is not None:
                self._on_camera_ready(self.xcamera)

    def _on_camera_ready(self, xcamera):
        xcamera._camera.bind(on_texture=self._on_texture)

    def _on_texture(self, instance):
        self.symbols = self._detect_qrcode_frame(texture=instance.texture, code_types=self.code_types)
        self.process_detected_symbols()

    @classmethod
    def _detect_qrcode_frame(cls, texture, code_types):
        image_data = texture.pixels
        size = texture.size
        pil_image = Image.frombytes(mode="RGBA", size=size, data=image_data)
        pil_image = cls._fix_android_image(cls, pil_image)
        symbols = []
        codes = pyzbar.decode(pil_image, symbols=code_types)
        for code in codes:
            symbol = ZBarCam.symbol(type=code.type, data=code.data)
            symbols.append(symbol)
        return symbols

    def _remove_shoot_button(self):
        xcamera = self.xcamera
        shoot_button = xcamera.children[0]
        xcamera.remove_widget(shoot_button)

    @staticmethod
    def _is_android():
        return platform == "android"

    def _fix_android_image(self, pil_image):
        if not self._is_android():
            return pil_image
        pil_image = pil_image.rotate(90)
        pil_image = ImageOps.mirror(pil_image)
        return pil_image

    def process_detected_symbols(self):
        if len(self.symbols) != 0:
            winsound.Beep(2500, 500)
            barcode_data = [symbol.data for symbol in self.symbols]
            self.update_database(barcode_data)
        else:
            self.display_barcode_data([])

    def display_barcode_data(self, barcode_data):
        if barcode_data:
            print("Detected Barcode Data:", barcode_data)
            barcode = barcode_data[0]
            item_data = self.get_item_from_database(barcode)
            if item_data:
                scan_count, total_weight = item_data
                self.root.ids.label.text = f"Scan Count: {scan_count} | Total Weight: {total_weight} kgs"
            else:
                self.root.ids.label.text = "Barcode not found in inventory."

    def init_database(self):
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS item (
                barcode TEXT PRIMARY KEY,
                item_type TEXT,
                weight_kgs REAL,
                scan_count INTEGER,
                total_weight REAL
            )
        """)
        self.conn.commit()

    def update_database(self, barcode_data):
        if not barcode_data:
            return

        barcode = barcode_data[0]
        item_data = self.get_item_from_database(barcode)

        if item_data:
            scan_count, total_weight = item_data
            scan_count += 1
            total_weight = scan_count * self.get_item_weight(barcode)
            self.cursor.execute("""
                UPDATE item
                SET scan_count = ?, total_weight = ?
                WHERE barcode = ?
            """, (scan_count, total_weight, barcode))
        else:
            self.cursor.execute("""
                INSERT INTO item (barcode, item_type, weight_kgs, scan_count, total_weight)
                VALUES (?, ?, ?, 1, ?)
            """, (barcode, "Unknown", 1.0, 1))

        self.conn.commit()
        self.display_database_result(barcode)

    def get_item_from_database(self, barcode):
        self.cursor.execute("SELECT scan_count, total_weight FROM item WHERE barcode = ?", (barcode,))
        return self.cursor.fetchone()

    def get_item_weight(self, barcode):
        # You can implement a method here to fetch item weight from a barcode lookup service.
        # For this example, we assume all items have a weight of 1 kg.
        return 1.0

    def display_database_result(self, barcode):
        item_data = self.get_item_from_database(barcode)
        if item_data:
            scan_count, total_weight = item_data
            self.root.ids.label.text = f"Scan Count: {scan_count} | Total Weight: {total_weight} kgs"
            notification.notify(
                title="Barcode Scanned",
                message=f"Scan Count: {scan_count} | Total Weight: {total_weight} kgs",
            )
        else:
            self.root.ids.label.text = "Barcode not found in inventory."

    def on_stop(self):
        self.conn.close()

if __name__ == "__main__":
    ZBarCam().run()
