from gi.repository import RB, Gdk, GLib


class YMDashboardEntry(RB.RhythmDBEntryType):
    def __init__(self, client, station):
        RB.RhythmDBEntryType.__init__(
            self, name="ym-dashboard-entry", save_to_disk=False
        )
        self.client = client
        self.station = station[6:]
        self.last_track = None

    def do_get_playback_uri(self, entry):
        self.last_track = entry.get_string(RB.RhythmDBPropType.LOCATION)[6:]
        downinfo = self.client.tracks_download_info(
            track_id=self.last_track, get_direct_links=True
        )
        return downinfo[1].direct_link


class YMDashboardSource(RB.BrowserSource):
    def __init__(self):
        RB.BrowserSource.__init__(self)

    def setup(self, db, client, station):
        self.initialised = False
        self.db = db
        self.entry_type = self.props.entry_type
        self.client = client
        self.station = station
        self.last_track = None

    def do_selected(self):
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self.rotor_station_tracks)

    def rotor_station_tracks(self):
        tracks = self.client.rotor_station_tracks(
            station=self.station[6:], queue=self.last_track
        ).sequence
        self.iterator = 0
        self.listcount = len(tracks)
        Gdk.threads_add_idle(GLib.PRIORITY_DEFAULT_IDLE, self.add_entry, tracks)
        return False

    def add_entry(self, tracks):
        track = tracks[self.iterator].track
        if track.available:
            entry_str = f"{self.station[:6]}{track.id}:{track.albums[0].id}"
            entry = self.db.entry_lookup_by_location(entry_str)
            if entry is None:
                entry = RB.RhythmDBEntry.new(self.db, self.entry_type, entry_str,)
                if entry is not None:
                    self.db.entry_set(entry, RB.RhythmDBPropType.TITLE, track.title)
                    self.db.entry_set(
                        entry, RB.RhythmDBPropType.DURATION, track.duration_ms / 1000
                    )
                    artists = ", ".join((artist.name for artist in track.artists))
                    self.db.entry_set(entry, RB.RhythmDBPropType.ARTIST, artists)
                    self.db.entry_set(
                        entry, RB.RhythmDBPropType.ALBUM, track.albums[0].title
                    )
                    self.db.commit()
        self.iterator += 1
        if self.iterator >= self.listcount:
            self.last_track = f"{track.id}:{track.albums[0].id}"
            return False
        else:
            return True
