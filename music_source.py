from abc import abstractmethod

from gi.repository import RB, Gdk, GLib


class MusicSource(RB.BrowserSource):
    def __init__(self, *args, **kwargs):
        RB.BrowserSource.__init__(self, *args, **kwargs)
        self.loaded_tracks_count = 0
        self.total_tracks = 0
        self.source_name = ""
        self.initialised = False
        self.db = None
        self.client = None

    @property
    def entry_type(self):
        return self.props.entry_type

    def setup(self, db, client, source_name):
        self.db = db
        self.client = client
        self.source_name = source_name

    def do_selected(self):
        if not self.initialised:
            self.initialised = True
            Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self.fetch_tracks)

    def fetch_tracks(self):
        tracks = self.get_tracks()
        self.total_tracks = len(tracks)
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self.add_entry_task, tracks)
        return False

    @abstractmethod
    def get_tracks(self):
        pass

    def add_track(self, track):
        if not track.available:
            return

        entry_location = f"{track.id}:{track.albums[0].id}"
        entry = self.db.entry_lookup_by_location(entry_location)
        if entry is None:
            entry = RB.RhythmDBEntry.new(self.db, self.entry_type, entry_location)

            artists = ", ".join((artist.name for artist in track.artists))
            self.db.entry_set(entry, RB.RhythmDBPropType.TITLE, track.title)
            self.db.entry_set(
                entry, RB.RhythmDBPropType.DURATION, track.duration_ms / 1000
            )
            self.db.entry_set(entry, RB.RhythmDBPropType.ARTIST, artists)
            self.db.entry_set(entry, RB.RhythmDBPropType.ALBUM, track.albums[0].title)
            self.db.commit()
        return track

    def add_entry_task(self, tracks):
        track = tracks[self.loaded_tracks_count]
        self.add_track(track)
        self.loaded_tracks_count += 1
        return self.loaded_tracks_count < self.total_tracks
