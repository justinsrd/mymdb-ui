import os
from flask import Flask, request
from flask_restful import Resource, Api
import psycopg2
import psycopg2.extras
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
api = Api(app)


class MyApp(Resource):
    def get(self):
        print(request.args)
        title = None
        imdb_id = None
        if request.args.get('title'):
            title = request.args['title'].replace('\'', '\'\'').lower()
        elif request.args.get('imdb_id'):
            imdb_id = request.args['imdb_id']

        try:
            db_name = os.environ['db_name']
            db_user = os.environ['db_user']
            db_host = os.environ['db_host']
            db_pass = os.environ['db_pass']
            credentials = "dbname=%s user=%s host=%s password=%s" % (db_name, db_user, db_host, db_pass)
            conn = psycopg2.connect(credentials)
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            query = None
            if title is not None:
                query = 'select * from show join episode on show.imdb_id = episode.show_id where LOWER(show.name) = \'%s\' and rating is not null order by episode.season asc, episode.episode asc;' % (title)
            elif imdb_id is not None:
                query = 'select * from show join episode on show.imdb_id = episode.show_id where show.imdb_id = \'%s\' and rating is not null order by episode.season asc, episode.episode asc;' % (imdb_id)
            print(query)

            cur.execute(query)
            res = cur.fetchall()
            print('\n\n\nres:::\n')
            print(res)
            print('\n\n\n')

            return res
        except Exception as e:
            print("ERROR FETCHING FROM DB: " + str(e))
            return {}

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
