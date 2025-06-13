import os
import shutil
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from plyer import storagepath


class TempCleaner(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=dp(15), spacing=dp(10), **kwargs)

        # === UI Colors ===
        self.bg_color = get_color_from_hex("#FFFFFF")
        self.primary_color = get_color_from_hex("#1E88E5")  # Blue
        self.text_color = get_color_from_hex("#000000")

        # === Header Image ===
        self.add_widget(Image(source='interface_temp_cleaner.png', size_hint_y=None, height=dp(250)))

        # === Title ===
        self.title = Label(text="📱 Temp Cleaner", font_size='24sp',
                           size_hint_y=None, height=dp(40), color=self.text_color)
        self.add_widget(self.title)

        # === Storage Info ===
        self.storage_info = Label(text="Storage Usage: Scanning...",
                                  size_hint_y=None, height=dp(40), color=self.text_color)
        self.add_widget(self.storage_info)

        # === Progress Bar ===
        self.progress_bar = ProgressBar(max=100, value=0,
                                        size_hint_y=None, height=dp(20))
        self.add_widget(self.progress_bar)

        # === Scan Button ===
        self.scan_btn = Button(text="🔍 Scan for Junk & Corrupted Files",
                               background_color=self.primary_color,
                               color=[1, 1, 1, 1], size_hint_y=None, height=dp(50))
        self.scan_btn.bind(on_press=self.scan_files)
        self.add_widget(self.scan_btn)

        # === File List View ===
        self.file_list_view = ScrollView(size_hint=(1, 1))
        self.file_list_label = Label(text="", size_hint_y=None,
                                     valign="top", color=self.text_color, markup=True)
        self.file_list_label.bind(texture_size=self.update_height)
        self.file_list_view.add_widget(self.file_list_label)
        self.add_widget(self.file_list_view)

        # === Delete Button ===
        self.delete_btn = Button(text="🗑️ Delete Junk Files",
                                 background_color=self.primary_color,
                                 color=[1, 1, 1, 1], size_hint_y=None, height=dp(50))
        self.delete_btn.bind(on_press=self.delete_files)
        self.add_widget(self.delete_btn)

        self.junk_files = []

    def update_height(self, *args):
        self.file_list_label.height = self.file_list_label.texture_size[1]

    def scan_files(self, instance):
        self.junk_files.clear()
        self.file_list_label.text = "[b]Scanning...[/b]\n"

        # Common junk file extensions
        extensions = [".log", ".tmp", ".bak", ".cache"]
        storage = storagepath.get_internal_storage()

        for root, dirs, files in os.walk(storage):
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)

                    if any(file.lower().endswith(ext) for ext in extensions) or file_size == 0:
                        self.junk_files.append(file_path)
                except:
                    self.junk_files.append(file_path)

        if self.junk_files:
            self.file_list_label.text = "\n".join(self.junk_files)
        else:
            self.file_list_label.text = "[b]✅ No junk or corrupted files found.[/b]"

        self.update_storage_info()

    def delete_files(self, instance):
        deleted = 0
        for file in self.junk_files:
            try:
                os.remove(file)
                deleted += 1
            except Exception as e:
                print(f"Cannot delete {file}: {e}")

        self.popup_message(f"✅ Deleted {deleted} files")
        self.file_list_label.text = ""
        self.junk_files.clear()
        self.update_storage_info()

    def popup_message(self, msg):
        popup = Popup(title='Cleanup Complete',
                      content=Label(text=msg),
                      size_hint=(None, None), size=(dp(300), dp(180)))
        popup.open()

    def update_storage_info(self):
        storage = storagepath.get_internal_storage()
        total, used, free = shutil.disk_usage(storage)
        percent_used = int(used / total * 100)

        self.storage_info.text = f"Storage: {self._format(used)} used / {self._format(total)} total"
        self.progress_bar.value = percent_used

    def _format(self, size_bytes):
        return f"{size_bytes / (1024 * 1024):.2f} MB"


class TempCleanerApp(App):
    def build(self):
        return TempCleaner()


if __name__ == '__main__':
    TempCleanerApp().run()
