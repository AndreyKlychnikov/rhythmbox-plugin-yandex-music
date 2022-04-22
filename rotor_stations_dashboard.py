from gi.repository import RB

from music_source import MusicSource


class YMDashboardEntry(RB.RhythmDBEntryType):
    def __init__(self, client, station):
        RB.RhythmDBEntryType.__init__(
            self, name="ym-dashboard-entry", save_to_disk=False
        )
        self.client = client
        self.station = station
        self.last_track = None

    def do_get_playback_uri(self, entry):
        self.last_track = entry.get_string(RB.RhythmDBPropType.LOCATION)
        downinfo = self.client.tracks_download_info(
            track_id=self.last_track, get_direct_links=True
        )
        return downinfo[1].direct_link


class YMDashboardSource(MusicSource):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_track = None

    def get_tracks(self):
        return self.client.rotor_station_tracks(
            station=self.source_name, queue=self.last_track
        ).sequence

    def add_track(self, track):
        track = track.track
        super().add_track(track)
        self.last_track = f"{track.id}:{track.albums[0].id}"
        return track
