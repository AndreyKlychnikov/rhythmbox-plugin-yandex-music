from gi.repository import RB

from music_source import MusicSource


class YMLikesEntry(RB.RhythmDBEntryType):
    def __init__(self, client):
        RB.RhythmDBEntryType.__init__(self, name="ym-likes-type", save_to_disk=False)
        self.client = client

    def do_get_playback_uri(self, entry):
        track_id = entry.get_string(RB.RhythmDBPropType.LOCATION)
        downinfo = self.client.tracks_download_info(
            track_id=track_id, get_direct_links=True
        )
        return downinfo[1].direct_link

    def do_destroy_entry(self, entry):
        track_id = entry.get_string(RB.RhythmDBPropType.LOCATION)
        return self.client.users_likes_tracks_remove(track_ids=track_id)


class YMLikesSource(MusicSource):
    def get_tracks(self):
        return self.client.users_likes_tracks().fetch_tracks()
