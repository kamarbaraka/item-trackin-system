import cv2
from pyzbar.pyzbar import decode
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.button import Button


class CameraScanner(App):

    """builds the UI layout of the app.
    :returns (Layout) the layout object defined"""
    def build(self):
        """construct the layout and set the orientation"""
        layout = BoxLayout()
        layout.orientation = 'vertical'

        """construct the camera widget and add it to the layout and make it an instance member of the
        class"""
        camera = Camera(resolution=(1200, 720), size_hint=(1, 0.8))
        self.camera = camera
        layout.add_widget(self.camera)

        """construct a button to trigger barcode scanning and bind it to a slot,
        then add the button to the layout"""
        scan_button = Button(text='scan', size_hint=(1, 0.2))
        scan_button.bind(on_press=self.scan_barcode)
        layout.add_widget(scan_button)

        return layout

    """scans the barcode using the camera.
    :param instance the instance of a scan"""
    def scan_barcode(self, instance):
        """capture the image from the camera"""
        self.camera.export_to_png("barcode_image.png")

        """decode barcodes from the image"""
        barcodes = decode(cv2.imread("barcode_image.pnd"))

        if barcodes:
            barcode_data = []
            for barcode in barcodes:
                barcode_data.append(barcode.data.decode("utf8"))

            self.show_barcode_data(barcode_data)

        else:
            self.show_barcode_data("no barcodes found")

    """presents the barcode
    :param barcode_data the decoded barcode data"""
    def show_barcode_data(self, barcode_data):
        for barcode in barcode_data:
            print(barcode)


if __name__ == "__main__":
    app = CameraScanner()
    app.run()
