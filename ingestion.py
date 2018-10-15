import os
import csv
import time
import sys
import psycopg2
from StringIO import StringIO

csv.field_size_limit(sys.maxsize)
start = int(time.time() * 1000)


def save_data_to_db(shows, episodes):
    try:
        db_name = os.environ['db_name']
        db_user = os.environ['db_user']
        db_host = os.environ['db_host']
        db_pass = os.environ['db_pass']
        credentials = "dbname=%s user=%s host=%s password=%s" % (db_name, db_user, db_host, db_pass)
        conn = psycopg2.connect(credentials)
        cur = conn.cursor()

        shows_query = ''
        for key, val in shows.iteritems():
            shows_query += val['title'] + '\t' + val['show_id'] + '\n'

        show_data = StringIO(shows_query)
        cur.copy_from(show_data, 'show', columns=('name', 'imdb_id'))
        conn.commit()

        episodes_query = ''
        for key, val in episodes.iteritems():
            episodes_query += val['show_id'] + '\t' + val['episode_id'] + '\t' + val['title'] + '\t' + str(val['season']) + '\t' + str(val['episode']) + '\t' + str(val['rating']) + '\t' + str(val['votes']) + '\n'

        episode_data = StringIO(episodes_query)
        cur.copy_from(episode_data, 'episode', null='\N', columns=('show_id', 'episode_id', 'episode_title', 'season', 'episode', 'rating', 'votes'))
        conn.commit()

    except Exception as e:
        print 'Error saving to DB: ' + str(e)


def main():
    with open("title.akas.tsv") as titles:
        all_titles = csv.reader(titles, delimiter=chr(181), quotechar='"') # use rare delimeter char so episode titles are not split
        with open("title.episode.tsv") as episodes:
            all_episodes = csv.reader(episodes, delimiter="\t", quotechar='"')
            with open("title.ratings.tsv") as ratings:
                all_ratings = csv.reader(ratings, delimiter="\t", quotechar='"')
                with open("title.basics.tsv") as names:
                    all_names = csv.reader(names, delimiter="\t", quotechar='"')

                    unique_shows = {}
                    unique_episodes = {}
                    unique_names = {}
                    for row in all_names:
                        if row[1] == 'tvEpisode':
                            episode_id = row[0]
                            unique_names[episode_id] = {
                                'id': episode_id,
                                'title': row[2]
                            }
                    title_parse_errors = 0
                    for index, row in enumerate(all_titles):
                        try:
                            row = row[0].replace('"', '').split('\t')
                            row[2].decode('utf-8') # error out if episode title is not utf-8 (causes db copy errors)
                            if row[0] not in unique_shows:
                                if '"' not in row[2]:
                                    unique_shows[row[0]] = {
                                        'title': row[2],
                                        'show_id': row[0],
                                        'has_episodes': False,
                                        'row_info': row
                                    }
                            elif row[3] == 'US' and row[5] == 'imdbDisplay':
                                unique_shows[row[0]] = {
                                    'title': row[2],
                                    'show_id': row[0],
                                    'has_episodes': False,
                                    'row_info': row
                                }

                            elif row[5] == 'original' and (unique_shows[row[0]]['row_info'][3] != 'US' and unique_shows[row[0]]['row_info'][5] != 'imdbDisplay'):
                                unique_shows[row[0]] = {
                                    'title': row[2],
                                    'show_id': row[0],
                                    'has_episodes': False,
                                    'row_info': row
                                }
                            elif not (unique_shows[row[0]]['row_info'][3] == 'US' and unique_shows[row[0]]['row_info'][5] == 'imdbDisplay') and unique_shows[row[0]]['row_info'][5] != 'original':
                                if row[1] == '1' and row[3] == 'US' and ('"' not in row[2]):
                                    unique_shows[row[0]] = {
                                    'title': row[2],
                                    'show_id': row[0],
                                    'has_episodes': False,
                                    'row_info': row
                                }
                                elif row[7] == '1' and unique_shows[row[0]]['row_info'][1] != '1' and unique_shows[row[0]]['row_info'][3] != 'US' and ('"' not in row[2]):
                                    unique_shows[row[0]] = {
                                    'title': row[2],
                                    'show_id': row[0],
                                    'has_episodes': False,
                                    'row_info': row
                                }
                                elif row[3] == 'US' and unique_shows[row[0]]['row_info'][3] == 'US' and int(row[1]) < int(unique_shows[row[0]]['row_info'][1]):
                                    unique_shows[row[0]] = {
                                    'title': row[2],
                                    'show_id': row[0],
                                    'has_episodes': False,
                                    'row_info': row
                                }
                        except Exception as e:
                            title_parse_errors += 1
                    print 'Number of errors: ' + str(title_parse_errors)
                    for row in all_episodes:
                        show_id = row[1]
                        episode_id = row[0]
                        if row[2] != '\N' and row[3] != '\N' and row[1] in unique_shows:
                            if unique_shows[show_id]['has_episodes'] is False:
                                unique_shows[show_id]['has_episodes'] = True
                            episode_title = unique_names[episode_id]['title'].replace('"', '').replace('\t', ' ')
                            unique_episodes[episode_id] = {
                                'show_id': show_id,
                                'episode_id': episode_id,
                                'title': episode_title,
                                'season': int(row[2]),
                                'episode': int(row[3]),
                                'rating': '\N',
                                'votes': '\N'
                            }

                    for row in all_ratings:
                        episode_id = row[0]
                        if episode_id in unique_episodes:
                            unique_episodes[episode_id]['rating'] = float(row[1])
                            unique_episodes[episode_id]['votes'] = int(row[2])

                    print '1 - unique_shows: ' + str(len(unique_shows.keys()))
                    print '2 - unique_episodes: ' + str(len(unique_episodes.keys()))


                    list_of_shows_to_delete = []
                    for show_id in unique_shows:
                        if unique_shows[show_id]['has_episodes'] is False:
                            list_of_shows_to_delete.append(show_id)
                    for show_id in list_of_shows_to_delete:
                        del unique_shows[show_id]
                    print '3 - UPDATED unique_shows WITH EPISODES: ' + str(len(unique_shows.keys()))


                    save_data_to_db(unique_shows, unique_episodes)
                    end = int(time.time() * 1000)
                    print str(end - start) + 'ms!'


main()
