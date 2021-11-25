# My Spotify

## Introduction

In this project I analyze my personal spotify data, including my streaming history between 09/2020-09/2021 and my library items (a.k.a, songs I liked). These datasets were retrieved from my account section on Spotify's website. To complement them I also use public data I gathered from Spotify's API (for more info see [here](https://developer.spotify.com/documentation/web-api/)).

The notebook consists of the following sections:

* [Data Collection and Preparation](#Data-Collection-and-Preparation)
    * [My Personal Data](#My-Personal-Data)
    * [Spotify API](#Spotify-API)
* [Data Analysis](#Data-Analysis)
    * [Streaming Time](#Streaming-Time)


```python
import pandas as pd             # For dataframes etc.
import numpy as np              # For multi-conditionals (np.where)
import seaborn as sns           # For plotting
import matplotlib.pyplot as plt # For plotting
import requests                 # For API data
import json                     # For loading json files
import datetime                 # For working with date values
from dateutil    import tz      # For converting time values between time-zones
from itertools   import chain   # For unnesting list of lists
from collections import Counter # For counting list items
%run code/functions             # Import user-defined functions
```

## Data Collection and Preparation

### My Personal Data

I use my personal data which I downloaded from Spotify's website on September 21, 2021. It includes my streaming history from the past year and all my library items (i.e., "liked songs"), according to that date.

#### Streaming History


```python
stream_file = 'MyData/StreamingHistory0.json'
my_stream = pd.read_json(stream_file)
my_stream.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>endTime</th>
      <th>artistName</th>
      <th>trackName</th>
      <th>msPlayed</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2020-09-21 11:11</td>
      <td>Miles Kane</td>
      <td>Blame It On The Summertime</td>
      <td>57630</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2020-09-21 16:04</td>
      <td>The Libertines</td>
      <td>The Good Old Days</td>
      <td>125160</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2020-09-22 12:35</td>
      <td>Franz Ferdinand</td>
      <td>Bullet</td>
      <td>1537</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2020-09-22 12:35</td>
      <td>The Libertines</td>
      <td>The Good Old Days</td>
      <td>54669</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2020-09-22 12:35</td>
      <td>Arctic Monkeys</td>
      <td>A Certain Romance</td>
      <td>941</td>
    </tr>
  </tbody>
</table>
</div>



The streaming history includes 4 features:

1. The date and time the stream was ended in UTC format
2. Artist name
3. Track name
4. Playing duration in milliseconds

For easier use, I'll rename the columns and convert the time to Israel time-zone and the duration's format to time-delta. Another feature I'll extract is whether the track was skipped. This will allow me to consider whether to remove a track from the library, as it is probably no longer needed. I set the bar at 10 seconds of playing.


```python
# Rename columns
my_stream.rename(columns = {'endTime':'date_played', 'artistName':'artist','trackName':'track'}, inplace = True)

# Convert endTime
my_stream['date_played'] = pd.to_datetime(my_stream.date_played)
my_stream['date_played'] = my_stream.date_played.dt.tz_localize('utc').dt.tz_convert('Asia/Jerusalem')

# Convert msPlayed
my_stream['time_played'] = round(my_stream.msPlayed / 1000)
my_stream['time_played'] = pd.to_timedelta(my_stream.time_played, unit='s')
my_stream['hours_played'] = round(my_stream.time_played / np.timedelta64(1, 'h'), 1)

# Skipped tracks
my_stream['skipped'] = my_stream.time_played.dt.total_seconds() < 10

my_stream.head().style.hide_index()
```




<style type="text/css">
</style>
<table id="T_c8c39_">
  <thead>
    <tr>
      <th class="col_heading level0 col0" >date_played</th>
      <th class="col_heading level0 col1" >artist</th>
      <th class="col_heading level0 col2" >track</th>
      <th class="col_heading level0 col3" >msPlayed</th>
      <th class="col_heading level0 col4" >time_played</th>
      <th class="col_heading level0 col5" >hours_played</th>
      <th class="col_heading level0 col6" >skipped</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td id="T_c8c39_row0_col0" class="data row0 col0" >2020-09-21 14:11:00+03:00</td>
      <td id="T_c8c39_row0_col1" class="data row0 col1" >Miles Kane</td>
      <td id="T_c8c39_row0_col2" class="data row0 col2" >Blame It On The Summertime</td>
      <td id="T_c8c39_row0_col3" class="data row0 col3" >57630</td>
      <td id="T_c8c39_row0_col4" class="data row0 col4" >0 days 00:00:58</td>
      <td id="T_c8c39_row0_col5" class="data row0 col5" >0.000000</td>
      <td id="T_c8c39_row0_col6" class="data row0 col6" >False</td>
    </tr>
    <tr>
      <td id="T_c8c39_row1_col0" class="data row1 col0" >2020-09-21 19:04:00+03:00</td>
      <td id="T_c8c39_row1_col1" class="data row1 col1" >The Libertines</td>
      <td id="T_c8c39_row1_col2" class="data row1 col2" >The Good Old Days</td>
      <td id="T_c8c39_row1_col3" class="data row1 col3" >125160</td>
      <td id="T_c8c39_row1_col4" class="data row1 col4" >0 days 00:02:05</td>
      <td id="T_c8c39_row1_col5" class="data row1 col5" >0.000000</td>
      <td id="T_c8c39_row1_col6" class="data row1 col6" >False</td>
    </tr>
    <tr>
      <td id="T_c8c39_row2_col0" class="data row2 col0" >2020-09-22 15:35:00+03:00</td>
      <td id="T_c8c39_row2_col1" class="data row2 col1" >Franz Ferdinand</td>
      <td id="T_c8c39_row2_col2" class="data row2 col2" >Bullet</td>
      <td id="T_c8c39_row2_col3" class="data row2 col3" >1537</td>
      <td id="T_c8c39_row2_col4" class="data row2 col4" >0 days 00:00:02</td>
      <td id="T_c8c39_row2_col5" class="data row2 col5" >0.000000</td>
      <td id="T_c8c39_row2_col6" class="data row2 col6" >True</td>
    </tr>
    <tr>
      <td id="T_c8c39_row3_col0" class="data row3 col0" >2020-09-22 15:35:00+03:00</td>
      <td id="T_c8c39_row3_col1" class="data row3 col1" >The Libertines</td>
      <td id="T_c8c39_row3_col2" class="data row3 col2" >The Good Old Days</td>
      <td id="T_c8c39_row3_col3" class="data row3 col3" >54669</td>
      <td id="T_c8c39_row3_col4" class="data row3 col4" >0 days 00:00:55</td>
      <td id="T_c8c39_row3_col5" class="data row3 col5" >0.000000</td>
      <td id="T_c8c39_row3_col6" class="data row3 col6" >False</td>
    </tr>
    <tr>
      <td id="T_c8c39_row4_col0" class="data row4 col0" >2020-09-22 15:35:00+03:00</td>
      <td id="T_c8c39_row4_col1" class="data row4 col1" >Arctic Monkeys</td>
      <td id="T_c8c39_row4_col2" class="data row4 col2" >A Certain Romance</td>
      <td id="T_c8c39_row4_col3" class="data row4 col3" >941</td>
      <td id="T_c8c39_row4_col4" class="data row4 col4" >0 days 00:00:01</td>
      <td id="T_c8c39_row4_col5" class="data row4 col5" >0.000000</td>
      <td id="T_c8c39_row4_col6" class="data row4 col6" >True</td>
    </tr>
  </tbody>
</table>




We can already see some of the tracks that were skipped, and other tracks that were skipped in less than a minute. It might be better to raise the bar for skipped songs, but I'll leave it for now.

#### Library

Next, we'll deal with the library dataset. It includes my saved/liked items on Spotify. The raw file is composed of several sub-dictionaries (see below), but I'll only use those of `artists`, `albums` and `tracks`.


```python
library_file = 'MyData/YourLibrary.json'

with open(library_file, encoding='utf-8') as library_file:
    library_json = json.load(library_file)

print('The provided datasets includes:', library_json.keys())
```

    The provided datasets includes: dict_keys(['tracks', 'albums', 'shows', 'episodes', 'bannedTracks', 'artists', 'bannedArtists', 'other'])
    

The first thing I want to do is to exclude podcasts from the `my_stream` to focus on songs only. For that I'll load the `shows` section from `library_json`.


```python
my_shows = pd.DataFrame(library_json['shows'])
my_stream = my_stream[~my_stream.artist.isin(list(my_shows.name))]
```

Now we can move on to data we actually want:


```python
my_artists = pd.DataFrame(library_json['artists'])
my_albums  = pd.DataFrame(library_json['albums'])
my_tracks  = pd.DataFrame(library_json['tracks'])

# Match artist column name between dfs
my_artists.rename(columns = {'name':'artist'}, inplace=True)

# Glance at column names
df_list = [my_artists, my_albums, my_tracks]
[df.columns for df in df_list]
```




    [Index(['artist', 'uri'], dtype='object'),
     Index(['artist', 'album', 'uri'], dtype='object'),
     Index(['artist', 'album', 'track', 'uri'], dtype='object')]



A quick check reveals some inconsistencies. For example, some of the artists in `my_tracks` does not appear in `my_artists` and/or `my_albums`:


```python
[df.artist.nunique() for df in df_list]
```




    [40, 15, 79]



We'll join the 3 dataframes for later analysis, but also help for identifying the inconsistencies:


```python
# Merge artists and albums
my_tracks_albums = my_tracks.merge(my_albums,
                                     how = 'outer',
                                     on = ['artist', 'album'], 
                                     suffixes = ('_tracks', '_albums'), 
                                     indicator = 'tracks_albums')

# Merge artists_albums with tracks
my_library = my_tracks_albums.merge(my_artists,
                                     how = 'outer',
                                     on = 'artist', 
                                     suffixes = ('_tracks_albums', '_artists'), 
                                     indicator = 'tracks_albums_artists')

my_library.rename(columns = {'uri':'uri_artists'}, inplace = True)

# Indicate match status for each row
my_library['match'] = np.select(
    [
        (my_library['tracks_albums'] == 'both')       & (my_library['tracks_albums_artists'] == 'both'),
        (my_library['tracks_albums'] == 'both')       & (my_library['tracks_albums_artists'] == 'left_only'),
        (my_library['tracks_albums'] == 'left_only')  & (my_library['tracks_albums_artists'] == 'left_only'),
        (my_library['tracks_albums'] == 'left_only')  & (my_library['tracks_albums_artists'] == 'both'),
        (my_library['tracks_albums'] == 'right_only') & (my_library['tracks_albums_artists'] == 'both')

    ], 
    [
        'all',
        'tracks_albums',
        'tracks_only',
        'tracks_artists',
        'artists_albums'
    ], 
    default='artists_only'
)

my_library.drop(['tracks_albums', 'tracks_albums_artists'], axis = 1, inplace = True)
```


```python
c = my_library['match'].value_counts(dropna = False)
p = my_library['match'].value_counts(normalize = True, dropna = False).multiply(100).round(1)

pd.concat([c, p], axis = 1, keys=['N', '%'])
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>N</th>
      <th>%</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>all</th>
      <td>464</td>
      <td>56.8</td>
    </tr>
    <tr>
      <th>tracks_artists</th>
      <td>256</td>
      <td>31.3</td>
    </tr>
    <tr>
      <th>tracks_only</th>
      <td>75</td>
      <td>9.2</td>
    </tr>
    <tr>
      <th>tracks_albums</th>
      <td>17</td>
      <td>2.1</td>
    </tr>
    <tr>
      <th>artists_only</th>
      <td>3</td>
      <td>0.4</td>
    </tr>
    <tr>
      <th>artists_albums</th>
      <td>2</td>
      <td>0.2</td>
    </tr>
  </tbody>
</table>
</div>



We can see how the 3 datasets match each other  &ndash; more than a half are fully matched, and about 31% were only found in the `tracks` dataset, which makes sense. It seems odd that I follow 3 artists while not having any of their songs (`artists_only`). The same applies for `artists_albums`, which has 2. I'll drop the last two categories from my library (the actual one, too) since they are useless and probably there by mistake.


```python
my_library = my_library[~my_library.match.isin( ['artists_only', 'artists_albums'])]
```

We should also look for duplicates in `my_library`, since I might have the same songs from different albums (e.g., a single and a track in an album). If there, we'll drop them.


```python
print('There are', my_library.duplicated(['artist', 'track'], keep=False).sum(), 'duplicates.')
```

    There are 66 duplicates.
    


```python
my_library.drop_duplicates(['artist', 'track'], keep='last', inplace=True)
```

I could use some of the information in `my_library` in `my_stream`. I'll take the album name, and also create a new indicator for being in `my_library`.


```python
my_stream = my_stream.merge(my_library[['artist', 'track','album']], how = 'left', 
                                    on = ['artist', 'track'], indicator = 'in_library')
my_stream['in_library'] = np.where(my_stream['in_library']=='left_only', False, True)
```

### Accessing Spotify API

In this section I will access the Spotify API to complement my personal data with more information, such as detecting whether a listing is a song or a podcast, getting songs' duration, year of production, and more).

First, I'll prepare my data for communicating with the API. That means organizing the different id columns in a proper format.


```python
# Extract item ID from each level's uri
uri_cols = [col for col in my_library.columns if 'uri' in col]

for col in uri_cols:
    my_library[col] = my_library[col].str.split(':').str[-1]
    my_library.rename(columns = {col:col.split("_")[1][:-1] + '_id'}, inplace = True)
    
my_library.head().style.hide_index()
```




<style type="text/css">
</style>
<table id="T_bad75_">
  <thead>
    <tr>
      <th class="col_heading level0 col0" >artist</th>
      <th class="col_heading level0 col1" >album</th>
      <th class="col_heading level0 col2" >track</th>
      <th class="col_heading level0 col3" >track_id</th>
      <th class="col_heading level0 col4" >album_id</th>
      <th class="col_heading level0 col5" >artist_id</th>
      <th class="col_heading level0 col6" >match</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td id="T_bad75_row0_col0" class="data row0 col0" >The Strokes</td>
      <td id="T_bad75_row0_col1" class="data row0 col1" >Room On Fire</td>
      <td id="T_bad75_row0_col2" class="data row0 col2" >Reptilia</td>
      <td id="T_bad75_row0_col3" class="data row0 col3" >2hmibAtdObO8F4tnhLENuQ</td>
      <td id="T_bad75_row0_col4" class="data row0 col4" >5OA9iN6WTzunqAdiuEpr7Q</td>
      <td id="T_bad75_row0_col5" class="data row0 col5" >0epOFNiUfyON9EYx7Tpr6V</td>
      <td id="T_bad75_row0_col6" class="data row0 col6" >all</td>
    </tr>
    <tr>
      <td id="T_bad75_row1_col0" class="data row1 col0" >The Strokes</td>
      <td id="T_bad75_row1_col1" class="data row1 col1" >Room On Fire</td>
      <td id="T_bad75_row1_col2" class="data row1 col2" >Under Control</td>
      <td id="T_bad75_row1_col3" class="data row1 col3" >5Llxit9Fc8E5C1jT9epRTU</td>
      <td id="T_bad75_row1_col4" class="data row1 col4" >5OA9iN6WTzunqAdiuEpr7Q</td>
      <td id="T_bad75_row1_col5" class="data row1 col5" >0epOFNiUfyON9EYx7Tpr6V</td>
      <td id="T_bad75_row1_col6" class="data row1 col6" >all</td>
    </tr>
    <tr>
      <td id="T_bad75_row2_col0" class="data row2 col0" >The Strokes</td>
      <td id="T_bad75_row2_col1" class="data row2 col1" >Room On Fire</td>
      <td id="T_bad75_row2_col2" class="data row2 col2" >I Can't Win</td>
      <td id="T_bad75_row2_col3" class="data row2 col3" >4rC465YB5dS1MySDtFsAE6</td>
      <td id="T_bad75_row2_col4" class="data row2 col4" >5OA9iN6WTzunqAdiuEpr7Q</td>
      <td id="T_bad75_row2_col5" class="data row2 col5" >0epOFNiUfyON9EYx7Tpr6V</td>
      <td id="T_bad75_row2_col6" class="data row2 col6" >all</td>
    </tr>
    <tr>
      <td id="T_bad75_row3_col0" class="data row3 col0" >The Strokes</td>
      <td id="T_bad75_row3_col1" class="data row3 col1" >Room On Fire</td>
      <td id="T_bad75_row3_col2" class="data row3 col2" >12:51</td>
      <td id="T_bad75_row3_col3" class="data row3 col3" >0nkLI0pdyTRpq7BsTFBufZ</td>
      <td id="T_bad75_row3_col4" class="data row3 col4" >5OA9iN6WTzunqAdiuEpr7Q</td>
      <td id="T_bad75_row3_col5" class="data row3 col5" >0epOFNiUfyON9EYx7Tpr6V</td>
      <td id="T_bad75_row3_col6" class="data row3 col6" >all</td>
    </tr>
    <tr>
      <td id="T_bad75_row4_col0" class="data row4 col0" >The Strokes</td>
      <td id="T_bad75_row4_col1" class="data row4 col1" >Room On Fire</td>
      <td id="T_bad75_row4_col2" class="data row4 col2" >What Ever Happened?</td>
      <td id="T_bad75_row4_col3" class="data row4 col3" >08yezFIhte4aFiDpmQmQlP</td>
      <td id="T_bad75_row4_col4" class="data row4 col4" >5OA9iN6WTzunqAdiuEpr7Q</td>
      <td id="T_bad75_row4_col5" class="data row4 col5" >0epOFNiUfyON9EYx7Tpr6V</td>
      <td id="T_bad75_row4_col6" class="data row4 col6" >all</td>
    </tr>
  </tbody>
</table>




#### Defining Connection

Connecting to the Spotify API requires personal access credentials that can be retrieved from [Spotify for Developers Dashboard](https://developer.spotify.com/dashboard/applications). For security and privacy reasons, I store mine in a separate script called `secrets`, which creates two object: `CLIENT_ID` and `CLIENT_SECRET`, containing the personal keys to access Spotify API.


```python
 %run code/secrets
```

Now for defining the connection to the API:


```python
AUTH_URL = 'https://accounts.spotify.com/api/token'

# POST
auth_response = requests.post(AUTH_URL, {
    'grant_type': 'client_credentials',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET
})

# convert the response to JSON
auth_response_data = auth_response.json()

# save the access token
access_token = auth_response_data['access_token']

headers = {'Authorization': 'Bearer {token}'.format(token=access_token)}

# The base url for all requests
BASE_URL = 'https://api.spotify.com/v1/'
```

#### Tracks

Here I'll retrieve the desired data for every track in my library, using the _Tracks API_ endpoint. I'll loop over `tracks_ids`, which uniquely identify each track in the spotify database. For efficiency, I split the ids into chunks of 50, the maximal amount that the API allows to get in a single request.


```python
# Get unique track ids
tracks_ids  = my_library.track_id.dropna().unique()

# Split into chunks of size 50 (max) beacuse of the API limitation
chunks = [tracks_ids[x:x+50] for x in range(0, len(tracks_ids), 50)]

# Prepare empty list for the filtered dictionary
d_filtered = []

# Collect data
for i in range(len(chunks)):
    
    chunks[i] = "%2C".join(chunks[i]) # Concat ids in each chunk and sepearate by comma ('%2C') to fit url query
    
    response = requests.get(BASE_URL + 'tracks?ids=' + chunks[i], 
                            headers=headers,
                            params={'limit': 50})
    d = response.json()
    
    # Filter list of dictionaries out of irrelevant information
    for track in d['tracks']:
        d_track = {'artist'           : track['artists'][0]['name'],
                   'album'            : track['album']['name'],
                   'album_release'    : track['album']['release_date'],
                   'album_tracks'     : track['album']['total_tracks'],                    
                   'track'            : track['name'],
                   'track_number'     : track['track_number'],
                   'duration_ms'      : track['duration_ms'],
                   'track_popularity' : track['popularity'],
                   'artist_id'        : track['artists'][0]['id'],
                   'album_id'         : track['album']['id'],
                   'track_id'         : track['id']}
        d_filtered.append(d_track)
    
spotify_tracks = pd.DataFrame(d_filtered)
```

A glance at the new dataset:


```python
spotify_tracks.head().style.hide_index()
```




<style type="text/css">
</style>
<table id="T_9e467_">
  <thead>
    <tr>
      <th class="col_heading level0 col0" >artist</th>
      <th class="col_heading level0 col1" >album</th>
      <th class="col_heading level0 col2" >album_release</th>
      <th class="col_heading level0 col3" >album_tracks</th>
      <th class="col_heading level0 col4" >track</th>
      <th class="col_heading level0 col5" >track_number</th>
      <th class="col_heading level0 col6" >duration_ms</th>
      <th class="col_heading level0 col7" >track_popularity</th>
      <th class="col_heading level0 col8" >artist_id</th>
      <th class="col_heading level0 col9" >album_id</th>
      <th class="col_heading level0 col10" >track_id</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td id="T_9e467_row0_col0" class="data row0 col0" >The Strokes</td>
      <td id="T_9e467_row0_col1" class="data row0 col1" >Room On Fire</td>
      <td id="T_9e467_row0_col2" class="data row0 col2" >2003-10-28</td>
      <td id="T_9e467_row0_col3" class="data row0 col3" >11</td>
      <td id="T_9e467_row0_col4" class="data row0 col4" >Reptilia</td>
      <td id="T_9e467_row0_col5" class="data row0 col5" >2</td>
      <td id="T_9e467_row0_col6" class="data row0 col6" >219826</td>
      <td id="T_9e467_row0_col7" class="data row0 col7" >0</td>
      <td id="T_9e467_row0_col8" class="data row0 col8" >0epOFNiUfyON9EYx7Tpr6V</td>
      <td id="T_9e467_row0_col9" class="data row0 col9" >5OA9iN6WTzunqAdiuEpr7Q</td>
      <td id="T_9e467_row0_col10" class="data row0 col10" >2hmibAtdObO8F4tnhLENuQ</td>
    </tr>
    <tr>
      <td id="T_9e467_row1_col0" class="data row1 col0" >The Strokes</td>
      <td id="T_9e467_row1_col1" class="data row1 col1" >Room On Fire</td>
      <td id="T_9e467_row1_col2" class="data row1 col2" >2003-10-28</td>
      <td id="T_9e467_row1_col3" class="data row1 col3" >11</td>
      <td id="T_9e467_row1_col4" class="data row1 col4" >Under Control</td>
      <td id="T_9e467_row1_col5" class="data row1 col5" >8</td>
      <td id="T_9e467_row1_col6" class="data row1 col6" >187306</td>
      <td id="T_9e467_row1_col7" class="data row1 col7" >0</td>
      <td id="T_9e467_row1_col8" class="data row1 col8" >0epOFNiUfyON9EYx7Tpr6V</td>
      <td id="T_9e467_row1_col9" class="data row1 col9" >5OA9iN6WTzunqAdiuEpr7Q</td>
      <td id="T_9e467_row1_col10" class="data row1 col10" >5Llxit9Fc8E5C1jT9epRTU</td>
    </tr>
    <tr>
      <td id="T_9e467_row2_col0" class="data row2 col0" >The Strokes</td>
      <td id="T_9e467_row2_col1" class="data row2 col1" >Room On Fire</td>
      <td id="T_9e467_row2_col2" class="data row2 col2" >2003-10-28</td>
      <td id="T_9e467_row2_col3" class="data row2 col3" >11</td>
      <td id="T_9e467_row2_col4" class="data row2 col4" >I Can't Win</td>
      <td id="T_9e467_row2_col5" class="data row2 col5" >11</td>
      <td id="T_9e467_row2_col6" class="data row2 col6" >162040</td>
      <td id="T_9e467_row2_col7" class="data row2 col7" >0</td>
      <td id="T_9e467_row2_col8" class="data row2 col8" >0epOFNiUfyON9EYx7Tpr6V</td>
      <td id="T_9e467_row2_col9" class="data row2 col9" >5OA9iN6WTzunqAdiuEpr7Q</td>
      <td id="T_9e467_row2_col10" class="data row2 col10" >4rC465YB5dS1MySDtFsAE6</td>
    </tr>
    <tr>
      <td id="T_9e467_row3_col0" class="data row3 col0" >The Strokes</td>
      <td id="T_9e467_row3_col1" class="data row3 col1" >Room On Fire</td>
      <td id="T_9e467_row3_col2" class="data row3 col2" >2003-10-28</td>
      <td id="T_9e467_row3_col3" class="data row3 col3" >11</td>
      <td id="T_9e467_row3_col4" class="data row3 col4" >12:51</td>
      <td id="T_9e467_row3_col5" class="data row3 col5" >4</td>
      <td id="T_9e467_row3_col6" class="data row3 col6" >153133</td>
      <td id="T_9e467_row3_col7" class="data row3 col7" >0</td>
      <td id="T_9e467_row3_col8" class="data row3 col8" >0epOFNiUfyON9EYx7Tpr6V</td>
      <td id="T_9e467_row3_col9" class="data row3 col9" >5OA9iN6WTzunqAdiuEpr7Q</td>
      <td id="T_9e467_row3_col10" class="data row3 col10" >0nkLI0pdyTRpq7BsTFBufZ</td>
    </tr>
    <tr>
      <td id="T_9e467_row4_col0" class="data row4 col0" >The Strokes</td>
      <td id="T_9e467_row4_col1" class="data row4 col1" >Room On Fire</td>
      <td id="T_9e467_row4_col2" class="data row4 col2" >2003-10-28</td>
      <td id="T_9e467_row4_col3" class="data row4 col3" >11</td>
      <td id="T_9e467_row4_col4" class="data row4 col4" >What Ever Happened?</td>
      <td id="T_9e467_row4_col5" class="data row4 col5" >1</td>
      <td id="T_9e467_row4_col6" class="data row4 col6" >169506</td>
      <td id="T_9e467_row4_col7" class="data row4 col7" >0</td>
      <td id="T_9e467_row4_col8" class="data row4 col8" >0epOFNiUfyON9EYx7Tpr6V</td>
      <td id="T_9e467_row4_col9" class="data row4 col9" >5OA9iN6WTzunqAdiuEpr7Q</td>
      <td id="T_9e467_row4_col10" class="data row4 col10" >08yezFIhte4aFiDpmQmQlP</td>
    </tr>
  </tbody>
</table>




#### Artists

Similarly, we can get the details of artists. Remember that `my_library` doesn't contain the unique id for every track's artist, but only for those I follow. It will be better to get them from the `spotify_track` dataframe, which we have just created:


```python
# Get unique artist ids
artists_ids  = spotify_tracks.artist_id.dropna().unique()

# Split into chunks of size 50 (max) beacuse of the API limitation
chunks = [artists_ids[x : x + 50] for x in range(0, len(artists_ids), 50)]

# Prepare empty list for the filtered dictionary
d_filtered = []

# Collect data
for i in range(len(chunks)):
    
    chunks[i] = "%2C".join(chunks[i]) # Concat ids in each chunk and sepearate by comma ('%2C') to fit url query
    
    response = requests.get(BASE_URL + 'artists?ids=' + chunks[i], 
                            headers=headers,
                            params={'limit': 50})
    d = response.json()
    
    # Filter list of dictionaries out of irrelevant information
    for artist in d['artists']:
        d_artist = {'artist_id' :artist['id'],
                    'artist'    :artist['name'],
                    'followers' :artist['followers']['total'],
                    'artist_popularity':artist['popularity'],
                    'genres'    :artist['genres']}
        d_filtered.append(d_artist)
    
spotify_artists = pd.DataFrame(d_filtered)
```

A glance at the new dataset:


```python
spotify_artists.head().style.hide_index()
```




<style type="text/css">
</style>
<table id="T_60469_">
  <thead>
    <tr>
      <th class="col_heading level0 col0" >artist_id</th>
      <th class="col_heading level0 col1" >artist</th>
      <th class="col_heading level0 col2" >followers</th>
      <th class="col_heading level0 col3" >artist_popularity</th>
      <th class="col_heading level0 col4" >genres</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td id="T_60469_row0_col0" class="data row0 col0" >0epOFNiUfyON9EYx7Tpr6V</td>
      <td id="T_60469_row0_col1" class="data row0 col1" >The Strokes</td>
      <td id="T_60469_row0_col2" class="data row0 col2" >4042874</td>
      <td id="T_60469_row0_col3" class="data row0 col3" >78</td>
      <td id="T_60469_row0_col4" class="data row0 col4" >['alternative rock', 'garage rock', 'modern rock', 'permanent wave', 'rock']</td>
    </tr>
    <tr>
      <td id="T_60469_row1_col0" class="data row1 col0" >7mnBLXK823vNxN3UWB7Gfz</td>
      <td id="T_60469_row1_col1" class="data row1 col1" >The Black Keys</td>
      <td id="T_60469_row1_col2" class="data row1 col2" >3578388</td>
      <td id="T_60469_row1_col3" class="data row1 col3" >73</td>
      <td id="T_60469_row1_col4" class="data row1 col4" >['alternative rock', 'blues rock', 'garage rock', 'modern blues rock', 'modern rock', 'punk blues', 'rock', 'roots rock']</td>
    </tr>
    <tr>
      <td id="T_60469_row2_col0" class="data row2 col0" >2uH0RyPcX7fnCcT90HFDQX</td>
      <td id="T_60469_row2_col1" class="data row2 col1" >Manic Street Preachers</td>
      <td id="T_60469_row2_col2" class="data row2 col2" >543972</td>
      <td id="T_60469_row2_col3" class="data row2 col3" >59</td>
      <td id="T_60469_row2_col4" class="data row2 col4" >['alternative rock', 'britpop', 'modern rock', 'permanent wave', 'pop rock', 'rock', 'welsh rock']</td>
    </tr>
    <tr>
      <td id="T_60469_row3_col0" class="data row3 col0" >3yY2gUcIsjMr8hjo51PoJ8</td>
      <td id="T_60469_row3_col1" class="data row3 col1" >The Smiths</td>
      <td id="T_60469_row3_col2" class="data row3 col2" >2849835</td>
      <td id="T_60469_row3_col3" class="data row3 col3" >74</td>
      <td id="T_60469_row3_col4" class="data row3 col4" >['madchester', 'new wave', 'permanent wave', 'rock', 'uk post-punk']</td>
    </tr>
    <tr>
      <td id="T_60469_row4_col0" class="data row4 col0" >6e9wIFWhBPHLE9bXK8gtBI</td>
      <td id="T_60469_row4_col1" class="data row4 col1" >Editors</td>
      <td id="T_60469_row4_col2" class="data row4 col2" >637069</td>
      <td id="T_60469_row4_col3" class="data row4 col3" >59</td>
      <td id="T_60469_row4_col4" class="data row4 col4" >['alternative dance', 'alternative rock', 'britpop', 'indie rock', 'modern rock', 'new rave', 'rock']</td>
    </tr>
  </tbody>
</table>




The `genres` column is actually composed of lists, which need to get separated in some way. I'll create a dummy for each genre, and keep only the main ones.


```python
# # Extract genres column as list of lists
# genres_raw = list(spotify_artists['genres'])

# # Unnest list, and remove duplicate genres
# genres = list(chain.from_iterable(genres_raw))

# counted = Counter(genres)
# print(counted)
# genres_filtered = [genre for genre in genres if counted[genre] > 1 or "israel" in genre]

```

Finally, we'll merge the artist information into the tracks dataset:


```python
spotify_data = spotify_tracks.merge(spotify_artists.drop(columns='artist'), how = 'left', on = 'artist_id')
```

## Data Analysis

Up to this point that we prepared several datasets:

* Personal data:
    * `my_stream`: with all the tracks I played in the past year (Sep 20'&ndash;Sep 21').
    * `my_library`: with all the items that are in my spotify library.
* Public data:
    * `spotify_tracks`: with public information regarding the tracks in `my_library`.
    * `spotify_artists`: same, but for aritsts.
 
Let's see what we can derive from them!

### Streaming Time

In start by exploring my most played tracks, albums and artists by the total duration played.


```python
# By artist
stream_by_artist = my_stream_library\
                   .groupby('artist', as_index=False)\
                   .hours_played.sum()

top10_artists = stream_by_artist.nlargest(10, 'hours_played')

plt.figure(figsize=(4, 6))
my_hbarplot(y = 'artist', x= 'hours_played', data = top10_artists,
            xlabel = 'Hours Played', title = 'Most Played Artists in 2021')
savefig('plots/top_played_artists.png')
plt.close()
```


```python
stream_by_album = my_stream_library\
                  .groupby('album', as_index=False)\
                  .agg({'artist':'first','hours_played':'sum'})
stream_by_album['album'] = stream_by_album['album'].str.replace('השחור החדש', 'HaSachor HaHadash')
stream_by_album['album'] = (stream_by_album['album'] + ' \n (' + stream_by_album['artist'] + ')').str.replace(' - Remastered', '')
top10_albums = stream_by_album.nlargest(10, 'hours_played')

plt.figure(figsize=(4, 6))
my_hbarplot(y = 'album', x= 'hours_played', data = top10_albums,
           xlabel = 'Hours Played', title = 'Most Played Albums in 2021')
savefig('plots/top_played_albums.png')
plt.close()
```


```python
stream_by_track = my_stream_library\
                  .groupby('track', as_index=False)\
                  .agg({'artist':'first','hours_played':'sum'})
stream_by_track['track'] = (stream_by_track['track'] + ' \n (' + stream_by_track['artist'] + ')').str.replace(' - Remastered', '')
top10_tracks = stream_by_track.nlargest(10, 'hours_played')

plt.figure(figsize=(4, 6))
my_hbarplot(y = 'track', x= 'hours_played', data = top10_tracks,
           xlabel = 'Hours Played', title = 'Most Played Tracks in 2021')
savefig('plots/top_played_tracks.png')
plt.close()
```

![](plots/top_played_artists.png)

![](plots/top_played_albums.png)

![](plots/top_played_tracks.png)

The next step will be to explore the streaming pattern of the top 10 artists across time, to see if there was a change in listening preferences.


```python
top10_artists_list = list(top10_artists['artist'])

monthly_stream = my_stream.groupby(['artist', pd.Grouper(key = 'date_played', freq = 'M')]).agg({'hours_played':'sum'}).reset_index()

top10_monthly = monthly_stream[monthly_stream.artist.isin(top10_artists_list)].reset_index(drop=True).sort_values('date_played')
top10_monthly['pct'] = top10_monthly.groupby(['date_played'])['hours_played'].apply(lambda x: round(100 * x / float(x.sum()), 1))
top10_monthly = top10_monthly.pivot(index='date_played',columns='artist')['pct']

x_ticks = list(top10_monthly.index.strftime('%b %y').unique())

sns.set_palette('deep')
plot=top10_monthly.plot.bar(stacked=True, figsize = (8,5),
              xlabel = 'Month', ylabel = 'Time Played, %', rot = 45)
plt.title('Most Played Artists Across Time',fontsize=16)
plt.legend(bbox_to_anchor=(1.0, 1.0))
plt.annotate('* Among the 10 most played artists throughout the whole year.', (0,-0.07), (0, -50), xycoords='axes fraction', textcoords='offset points', size = 11)
plot.set_xticklabels(labels=x_ticks, rotation=45, ha='right')
savefig('plots/artists_by_month.png')

plt.close()
```

![](plots/artists_by_month.png)

It seems like Editors started to dominate in February 21', continuing up until September, when Manic Street Preaches suddenly took the throne.

Most of the time I stream the playlist "Liked Songs", which contains the items in my library. Although I actively marked them as such, I don't want to listen to them __every__ time they come up. To explore that phenomenon, I use the `skipped` variable I created eralier. Let's start looking at the artists level:


```python
skipped_artists = my_stream_library.groupby(['artist'], as_index=False)[['skipped']].sum().nlargest(10, 'skipped')
plt.figure(figsize=(4, 6))
my_hbarplot(x = 'skipped', y = 'artist', data = skipped_artists, 
            title = 'Most Skipped Artists', xlabel = 'Times Skipped')
savefig('plots/most_skipped_artists_false.png')
plt.close()
```

![](plots/most_skipped_artists_false.png)

It appears that most of these artists intersects with my most played artists, which is a bit strange. It happens because each of them has a different probability to come up when shuffling through my library. Let's adjust these values to consider this issue:


```python
# Count times skipped and total appearances. Filter for appearances > 10
skipped_artists_adj = my_stream.groupby(['artist']).agg({'skipped':'sum', 'artist':'count'}).rename(columns={'artist':'times_played'}).query('times_played > 10').reset_index()

# Calculate percentage skipped and display
skipped_artists_adj['skipped_pct'] = round(skipped_artists_adj.skipped / skipped_artists_adj.times_played * 100, 1)
skipped_artists_adj = skipped_artists_adj.drop(columns='skipped').query('skipped_pct > 60').sort_values('skipped_pct', ascending=False)
```


```python
# Plot
plt.figure(figsize=(4, 8))
my_hbarplot(x = 'skipped_pct', y = 'artist', data = skipped_artists_adj, 
            title = 'Most Skipped Artists, % of Total Streams', xlabel = 'Percentage Skipped')
plt.annotate('* Artists who were streamed at least 10 times.', (-0.5,0), (0, -50), xycoords='axes fraction', textcoords='offset points', size = 10)
savefig('plots/most_skipped_artists.png')
plt.close()
```

![](plots/most_skipped_artists.png)

This is a completely different picture, but note that Franz Ferdinand (also FFS) appears in both figures. That means that while I have many of their songs marked as "liked", I tend to skip them too often. Maybe I should reconsider my affection to them...

The next thing to consider is openness to new music. This can be found by comparing streaming time of songs in my library to those that aren't there. Two major caveats arise:
    
  1. I can't distinguish songs that got into the library in the middle of the year.
  2. I occasionally listen to reading soundtracks for focusing. I might be able to distinguish them by getting the playlists, but currently I skip that.

Nevertheless, let's see what we have:


```python
in_library = my_stream.groupby('in_library', as_index=False).hours_played.sum()
in_library['in_library'] = np.where(in_library['in_library']==True, 'In Library', 'Not In Library')
fig = plt.figure(facecolor="w")
plt.pie(in_library['hours_played'], labels = in_library['in_library'], autopct='%1.0f%%')
plt.title('Openness To New Music', size = 16)
savefig('plots/library_streaming.png')
plt.close()
```

![](plots/library_streaming.png)

### Popularity/Followers

**Artist Popularity**

> The popularity of the artist. The value will be between 0 and 100, with 100 being the most popular. The artist’s popularity is calculated from the popularity of all the artist’s tracks.	

**Track Popularity**

> The popularity of the track. 
>
> The popularity of a track is a value between 0 and 100, with 100 being the most popular. The popularity is calculated by algorithm and is based, in the most part, on the total number of plays the track has had and how recent those plays are.
>
>Generally speaking, songs that are being played a lot now will have a higher popularity than songs that were played a lot in the past. Duplicate tracks (e.g. the same track from a single and an album) are rated independently. Artist and album popularity is derived mathematically from track popularity. Note that the popularity value may lag actual popularity by a few days: the value is not updated in real time.


```python
# spotify_artists['test'] = np.log(spotify_artists.followers)

# sns.regplot(x = 'artist_popularity',
#             y = 'test',
#            data = spotify_artists,
#            ci = None           )
# plt.show()
```


```python
# followers_duration = stream_by_artist\
#                      .merge(spotify_artists, how='inner', on='artist')\
#                      .query('hours_played > 10 | followers > 7000000').reset_index()

# followers_duration['followers_m'] = followers_duration['followers'] / 1000000

# sns.lmplot(x = 'hours_played',
#             y = 'followers_m',
#            data = followers_duration,
#            ci = None,
#            height=5, aspect=3/2)  

# plt.xlabel('Hours Played', fontsize=12)
# plt.ylabel('Followers (millions)', fontsize=12)
# plt.title('Worldwide Followers vs. My Playing Time in 2021', fontsize=16)
# footnote = 'Note: The artist presented had at least 7M followers or were played for at least 10 hours.'
# plt.annotate(footnote, (0,0), (0, -50), xycoords='axes fraction', textcoords='offset points', size = 11)


# for i in range(followers_duration.shape[0]):
#     if any(sub in followers_duration.artist[i] for sub in ['Arcade']):
#         plt.text(x=followers_duration.hours_played[i]+0.4,y=followers_duration.followers_m[i]-1.2,s=followers_duration.artist[i])
#     elif any(sub in followers_duration.artist[i] for sub in ['Puppets']):
#         plt.text(x=followers_duration.hours_played[i]-0.1,y=followers_duration.followers_m[i]-2,s=followers_duration.artist[i])
#     elif any(sub in followers_duration.artist[i] for sub in ['Manic']):
#         plt.text(x=followers_duration.hours_played[i]-10,y=followers_duration.followers_m[i]+0.9,s=followers_duration.artist[i])
#     else:
#         plt.text(x=followers_duration.hours_played[i]+0.3,y=followers_duration.followers_m[i]+0.9,s=followers_duration.artist[i])
```
