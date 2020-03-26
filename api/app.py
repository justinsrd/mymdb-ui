import os
from flask import Flask, request
from flask_restful import Resource, Api
import psycopg2
import psycopg2.extras
from flask_cors import CORS

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


class MyApp(Resource):
    def get(self):
        # print(request.args)
        res2 = {}
        title = None
        imdb_id = None
        if request.args.get('title'):
            title = request.args['title'].replace('\'', '\'\'').lower()
        elif request.args.get('imdb_id'):
            imdb_id = request.args['imdb_id']

        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            query = None
            if title is not None:
                query = 'select * from show join episode on show.imdb_id = episode.show_id where LOWER(show.name) = \'%s\' and rating is not null order by episode.season asc, episode.episode asc;' % (title)
            elif imdb_id is not None:
                query = 'select * from show join episode on show.imdb_id = episode.show_id where show.imdb_id = \'%s\' and rating is not null order by episode.season asc, episode.episode asc;' % (imdb_id)
            print(query)

            cur.execute(query)
            # res = cur.fetchall()
            res2['show_data'] = cur.fetchall()
            # print('\n\n\nres:::\n')
            # print(res)
            # print('\n\n\n')
        except Exception as e:
            print("ERROR FETCHING FROM DB: " + str(e))
            return {}



        try:
            # if show does not have poster
            # scrape imdb for poster url
            # add poster url to show's db row
            print('yes')

            # add show + poster + id to redis list
        except Exception as e:
            print("ERROR OPERATING WITH REDIS: " + str(e))
            return {}









        # return show data, redis list
        # return res
        return res2


    def post(self):
        return {'meow': 'foo'}

    def patch(self):
        return {'bar': 'patch'}

    def put(self):
        return {'handle': 'put'}

    def delete(self):
        return {'LOL': 'delete'}


api.add_resource(MyApp, '/')

if __name__ == '__main__':
    app.run(debug=True)
