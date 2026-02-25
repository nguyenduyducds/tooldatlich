
class Project:
    def __init__(self):
        self.video_items = []

    def add_video(self, path):
        # Prevent duplicates if needed, or allow multiple uploads of same file?
        # Controller logic seems to allow adding.
        if path not in self.video_items:
            self.video_items.append(path)

    def remove_video(self, path):
        if path in self.video_items:
            self.video_items.remove(path)
