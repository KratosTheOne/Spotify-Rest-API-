import sys
import json
import requests
import token_file


class LastFmSpotify:
    def __init__(self):
        self.token = token_file.spotify_token()
        self.api_key = token_file.last_fm_api_key()
        self.user_id = token_file.spotify_user_id()
        self.spotify_headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        self.playlist_id = ''
        self.song_info = {}
        self.uris = []

    def fetch_songs(self):
        params = {'limit': 20, 'api_key': self.api_key}
        url = f'http://ws.audioscrobbler.com/2.0/?method=chart.gettoptracks&format=json'
        response = requests.get(url, params=params)
        if response.status_code != 200:
            self.exceptions(response.status_code, response.text())
        print("Top Songs are: \n")
        res = response.json()
        for item in res['tracks']['track']:
            song = item['name'].title()
            artist = item['artist']['name'].title()
            print(f"{song} by {artist}")
            self.song_info[song] = artist
        print("\nGetting Songs URI\n")
        self.get_uri_from_spotify()
        print("Creating a Playlist!\n")
        self.create_playlist()
        print("Adding Songs!\n")
        self.add_songs()
        print("Songs are as follows:\n")
        self.list_songs()

    def get_uri_from_spotify(self):
        for song_name, artist in self.song_info.items():
            url = f"https://api.spotify.com/v1/search?query=track%3A{song_name}+artist%3A{artist}&type=track&offset=0&limit=10"
            response = requests.get(url, headers=self.spotify_headers)
            res = response.json()
            output_uri = res['tracks']['items']
            uri = output_uri[0]['uri']
            self.uris.append(uri)

    def create_playlist(self):
        data = {
            "name": "Top Latest Songs",
            "description": "Songs from the top charts of LastFm via API",
            "public": True
        }
        data = json.dumps(data)

        url = f'https://api.spotify.com/v1/users/{self.user_id}/playlists'
        response = requests.post(url, data=data, headers=self.spotify_headers)
        if response.status_code == 201:
            res = response.json()
            print("Playlist Created")
            self.playlist_id = res['id']
        else:
            self.exceptions(response.status_code, response.text())

    def add_songs(self):
        uri_list = json.dumps(self.uris)
        url = f"https://api.spotify.com/v1/playlists/{self.playlist_id}/tracks"
        response = requests.post(url, data=uri_list, headers=self.spotify_headers)
        if response.status_code == 201:
            print("Songs Added Successfully")
        else:
            self.exceptions(response.status_code, response.text())

    def list_songs(self):
        url = f"https://api.spotify.com/v1/playlists/{self.playlist_id}/tracks"
        response = requests.get(url, headers=self.spotify_headers)
        if response.status_code != 200:
            self.exceptions(response.status_code, response.text())
        else:
            res = response.json()
            for item in res['items']:
                print(item['track']['name'])

    def exceptions(self, status_code, err):
        print("Exception Occurred with status_code ", status_code)
        print("Error: ", err)
        sys.exit(0)


if __name__ == '__main__':
    d = LastFmSpotify()
    d.fetch_songs()
