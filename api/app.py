import os
import redis
import requests
import json
import psycopg2
import psycopg2.extras
from flask import Flask, request
from flask_restful import Resource, Api, abort
from flask_cors import CORS
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)
api = Api(app)


# init db
db_name = os.environ['db_name']
db_user = os.environ['db_user']
db_host = os.environ['db_host']
db_pass = os.environ['db_pass']
credentials = "dbname=%s user=%s host=%s password=%s" % (db_name, db_user, db_host, db_pass)
conn = psycopg2.connect(credentials)

# init redis
r = redis.StrictRedis(
    host=os.environ['redis_host'],
    port=int(os.environ['redis_port']),
    password=os.environ['redis_pw'],
    decode_responses=True
)
LIST_NAME = 'mymdb_recents'
IMDB_URL = 'https://www.imdb.com/title/'


class MyApp(Resource):
    def get(self):
        res = {}
        title = None
        imdb_id = None
        show_id = None
        show_name = None
        img_url = None
        cur = None
        if request.args.get('title'):
            title = request.args['title'].replace('\'', '\'\'').lower()
        elif request.args.get('imdb_id'):
            imdb_id = request.args['imdb_id']

        # for anyone tryna sql inject
        if (title is not None and ';' in title) or (imdb_id is not None and ';' in imdb_id):
            abort(400, error='Plz don\'t hack me bro')

        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            query = None
            if title is not None:
                query = 'select show.name, show.imdb_id, episode.episode_title, episode.season, episode.episode, episode.rating, episode.votes from show join episode on show.imdb_id = episode.show_id where LOWER(show.name) = \'%s\' and rating is not null order by episode.season asc, episode.episode asc;' % (title)
            elif imdb_id is not None:
                query = 'select show.name, show.imdb_id, episode.episode_title, episode.season, episode.episode, episode.rating, episode.votes from show join episode on show.imdb_id = episode.show_id where show.imdb_id = \'%s\' and rating is not null order by episode.season asc, episode.episode asc;' % (imdb_id)
            cur.execute(query)
            res['show_data'] = cur.fetchall()

            if len(res['show_data']) > 0:
                show_name = res['show_data'][0]['name']
                show_id = res['show_data'][0]['imdb_id']

                query2 = 'select poster_url from poster join show on show.imdb_id = poster.show_id where LOWER(show.imdb_id) = \'%s\';' % show_id
                cur.execute(query2)
                poster_data = cur.fetchall()
                if poster_data is not None and len(poster_data) > 0:
                    img_url = poster_data[0]['poster_url']
        except Exception as e:
            print('ERROR FETCHING FROM DB: ' + str(e))
            return {'error': 'DB Fetch Error'}

        if show_name is not None and img_url is None:
            try:
                # if show does not have poster
                # scrape imdb for poster url
                # add poster url to show's db row
                page = requests.get(IMDB_URL + show_id)
                soup = BeautifulSoup(page.content, 'html.parser')
                results = soup.find(class_='poster').find('img')
                img_url = results['src']

                query3 = 'INSERT INTO poster(show_id, poster_url) VALUES (\'%s\', \'%s\');' % (show_id, img_url)
                cur.execute(query3)
                conn.commit()
            except Exception as e:
                print('ERROR OPERATING WITH SCRAPER: ' + str(e))
                return {'error': 'Poster Scraper Error'}

        # remove previous instances of show & poster from list
        # add show & poster to beginning of list
        # get entire list (0 - 15)
        # add to response
        if img_url is not None and show_name is not None and show_id is not None:
            try:
                s = json.dumps({
                    'show_id': show_id,
                    'show_name': show_name,
                    'poster_url': img_url
                })
                r.lrem(LIST_NAME, 0, s)
                r.lpush(LIST_NAME, s)
                d = r.lrange(LIST_NAME, 0, 15)
                if len(d) > 15:
                    r.rpop(LIST_NAME)
                    d.pop()
                res['recents'] = d
            except Exception as e:
                print('ERROR OPERATING WITH REDIS: ' + str(e))
                return {'error': 'Redis Error'}
        else:
            print('Unable to find show_name or img_url')

        return res

    def post(self):
        try:
            d = r.lrange(LIST_NAME, 0, 15)
            return d
        except Exception as e:
            print('ERROR OPERATING WITH REDIS: ' + str(e))
            return {'error': 'Redis Error'}

api.add_resource(MyApp, '/q')

if __name__ == '__main__':
    app.run(debug=True)
