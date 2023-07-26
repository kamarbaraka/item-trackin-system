import os
import winsound
import sqlite3

from collections import namedtuple
from PIL import ImageOps
from PIL import Image
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ListProperty
from kivy.properties import ObjectProperty
from kivy.utils import platform
from kivy.uix.anchorlayout import AnchorLayout
from kivy_garden.xcamera import XCamera
from pyzbar import pyzbar
from pyzbar.pyzbar import ZBarSymbol

# Path to the SQLite database file
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
        Button:
            size_hint_y: None
            height: '48dp'
            text: 'Generate Report'
            on_press: root.generate_report()
"""

class ZBarCam(AnchorLayout, App):
    """the resolution of the camera"""
    resolution = ListProperty([640, 480])

    symbols = ListProperty([])
    symbol = namedtuple("symbol", ["type", "data"])

    """the qr or barcode types. Default is all types"""
    code_types = ListProperty(set(pyzbar.ZBarSymbol))

    xcamera = ObjectProperty(None)

    def build(self):
        Builder.load_string(kv_string)  # Load the kv string
        self.init_database()
        Clock.schedule_once(lambda dt: self._setup())
        return super(ZBarCam, self).build()

    def on_xcamera(self, instance, value):
        # This method is called when xcamera is assigned a value after loading the kv file
        self._setup()

    def _setup(self):
        if self.xcamera is not None:
            """remove the shoot button"""
            self._remove_shoot_button()

            """bind camera to event"""
            self.xcamera.bind(on_camera_ready=self._on_camera_ready)

            """camera may be ready before bind"""
            if self.xcamera._camera is not None:
                self._on_camera_ready(self.xcamera)

    def _on_camera_ready(self, xcamera):
        """binds when xcamera._camera instance is ready"""
        xcamera._camera.bind(on_texture=self._on_texture)

    def _on_texture(self, instance):
        """store symbols in symbols property"""
        self.symbols = self._detect_qrcode_frame(texture=instance.texture, code_types=self.code_types)
        self.process_detected_symbols()

    @classmethod
    def _detect_qrcode_frame(cls, texture, code_types):
        image_data = texture.pixels
        size = texture.size

        pil_image = Image.frombytes(
            mode="RGBA",
            size=size,
            data=image_data
        )

        pil_image = cls._fix_android_image(cls, pil_image)
        symbols = []
        codes = pyzbar.decode(pil_image, symbols=code_types)

        for code in codes:
            symbol = ZBarCam.symbol(type=code.type, data=code.data)
            symbols.append(symbol)

        return symbols

    def _remove_shoot_button(self):
        """removes the shoot button"""
        xcamera = self.xcamera
        shoot_button = xcamera.children[0]
        xcamera.remove_widget(shoot_button)

    @staticmethod
    def _is_android():
        return platform == "android"

    @staticmethod
    def _is_ios():
        return platform == "ios"

    def _fix_android_image(self, pil_image):
        """fix mirrored android image"""
        if not self._is_android():
            return pil_image

        """rotate 90"""
        pil_image = pil_image.rotate(90)
        pil_image = ImageOps.mirror(pil_image)
        return pil_image

    def process_detected_symbols(self):
        if len(self.symbols) != 0:
            winsound.Beep(2500, 500)
            print(self.symbols)
            barcode_data = [symbol.data for symbol in self.symbols]
            self.update_database(barcode_data)
        else:
            self.display_barcode_data([])

    def display_barcode_data(self, barcode_data):
        if barcode_data:
            print("Detected Barcode Data:", barcode_data)
            # Do something with the barcode data, e.g., save it, use it in other scripts, etc.

    def init_database(self):
        # Connect to the SQLite database
        self.conn = sqlite3.connect(DATABASE_PATH)
        self.cursor = self.conn.cursor()

        # Create the 'item' table if it doesn't exist
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
        self.cursor.execute("SELECT * FROM item WHERE barcode = ?", (barcode,))
        item = self.cursor.fetchone()

        if item:
            # If barcode exists in the database, update the scan count and total weight
            scan_count = item[3] + 1
            total_weight = scan_count * item[2]

            self.cursor.execute("""
                UPDATE item
                SET scan_count = ?, total_weight = ?
                WHERE barcode = ?
            """, (scan_count, total_weight, barcode))
        else:
            # If barcode doesn't exist in the database, insert a new record
            self.cursor.execute("""
                INSERT INTO item (barcode, item_type, weight_kgs, scan_count, total_weight)
                VALUES (?, ?, ?, 1, ?)
            """, (barcode, "Unknown", 1.0, 1))

        self.conn.commit()
        self.display_database_result(barcode)

    def display_database_result(self, barcode):
        self.cursor.execute("SELECT scan_count, total_weight FROM item WHERE barcode = ?", (barcode,))
        result = self.cursor.fetchone()

        if result:
            scan_count, total_weight = result
            self.root.ids.label.text = f"Scan Count: {scan_count} | Total Weight: {total_weight} kgs"

    def generate_report(self):
        # You can implement the code here to generate a report based on the database contents
        # For simplicity, this example doesn't include the report generation feature.
        print("Generating report...")

    def on_stop(self):
        # Close the database connection when the app is stopped
        self.conn.close()

if __name__ == "__main__":
    ZBarCam().run()
