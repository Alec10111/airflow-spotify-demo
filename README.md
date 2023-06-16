# Airflow Spotify Demo

Use Airflow scheduled job and spotify API to update a playlist with songs from top charts

## DAG Draft

1. Use Billboard API to get top 10 songs
2. Use Billboard API to get top 10 artists
3. Browse the track id for each song with spotify API
4. Get most played track from each artists with spotify API
5. In Parallel
    - From the top 1 song, include the whole album. From the other songs. Remove blacklisted artists and genres
    - Generate statistics in excel from db (number of appereances of each track on the top)
6. Create playlist `Airflow hits` in spotify if not exists
7. Update the playlist with the depurated list of songs
