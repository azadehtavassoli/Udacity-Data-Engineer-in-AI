import os
import glob
import psycopg2
import pandas as pd
import numpy as np
from sql_queries import *



def process_song_file(cur, filepath):
 """
  Description: This function is responsible for extracting the data from JSON song file, in first step,
  and based on the extracted data prepares inputs for artists, and songs table.

  Arguments:
      cur: the cursor object.
      filepath: song data (path+filename)

  Returns:
      None
  """
    '''
    This function extracts Data for Songs Table from the JSON files
    Selects columns for song ID, title, artist ID, year, and duration
  - Convert the array to a list and insert it to `song_data`
    '''
    
    
    # open song file
    df =pd.read_json(filepath, lines=True) 

    # insert song record
    song_data = df[['song_id','title','artist_id','year','duration']].values[0] 
    cur.execute(song_table_insert, song_data)
    
    # insert artist record
    artist_data =  df[['artist_id', 'artist_name','artist_location','artist_latitude', 'artist_longitude']].values[0]
    cur.execute(artist_table_insert, artist_data)

def process_log_file(cur, filepath):
 """
  Description: This function is responsible for extracting the data from JSON log file, in first step,
  and based on the extracted data prepares inputs for users, time, and songs play table.

  Arguments:
      cur: the cursor object.
      filepath: log data (path+filename)

  Returns:
      None
  """  

    # open log file
    df = pd.read_json(filepath, lines=True) 

    # filter by NextSong action
    df['ts'] = pd.to_datetime(df['ts'], unit='ms')
    df = df[df['page']=="NextSong"]

    # convert timestamp column to datetime
    t = pd.to_datetime(df['ts'])
    
    # insert time data records
    time_data = np.array([t.dt.time, t.dt.hour.values, t.dt.day.values , t.dt.week.values,
             t.dt.month.values , t.dt.year.values, t.dt.dayofweek.values]).T
    column_labels = ['timestamp','hour', 'day', 'week', 'month' , 'year', 'weekday']
    time_df = pd.DataFrame(time_data,columns=column_labels)

    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # load user table
    user_df = df[["userId", "firstName","lastName","gender" , "level"]] 

    # insert user records
    for i, row in user_df.iterrows():
        cur.execute(user_table_insert, row)

    # insert songplay records
    for index, row in df.iterrows():
        
        # get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()
        
        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # insert songplay record
        songplay_data = (row.ts, row.userId, row.level, songid, artistid, row.sessionId, row.location, row.userAgent)
        cur.execute(songplay_table_insert, songplay_data)



def process_data(cur, conn, filepath, func):
"""
  Description: This function is responsible for listing the files in a directory,
  and then executing the ingest process for each file according to the function
  that performs the transformation to save it to the database.

  Arguments:
      cur: the cursor object.
      conn: connection to the database.
      filepath: log data or song data file path.
      func: function that transforms the data and inserts it into the database.

  Returns:
      None
  """    
    
    # get all files matching extension from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root,'*.json'))
        for f in files :
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    print('{} files found in {}'.format(num_files, filepath))

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        func(cur, datafile)
        conn.commit()
        print('{}/{} files processed.'.format(i, num_files))


def main():
"""
  Description: This function is the main function of the ETL pipline.
  It sets up the connection to the database and the cursor object.
  Finally, it porcesses the song files and log files.

  Arguments:
      None

  Returns:
      None
  """    
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student password=student")
    cur = conn.cursor()

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    conn.close()


if __name__ == "__main__":
    main()