import cherrypy
import csv
import io
from jinja2 import Environment, FileSystemLoader
import os
import requests
import redis
import zipfile
import datetime
env = Environment(loader=FileSystemLoader('templates'))
redis_host = "localhost"
redis_port = 6379
redis_password = ""


class NSEBhaveCopy():

    def load_zip_file(self):
        try:
            r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
            today = datetime.datetime.today().strftime('%d%m%y')
            url = "https://www.bseindia.com/download/BhavCopy/Equity/EQ%s_CSV.ZIP" % today
            response = requests.get(url)  # request should be called only once in a day using scheduler, but as of now putted it on page load as sample task
            if response.ok:
                zfile = zipfile.ZipFile(io.BytesIO(response.content))
                for finfo in zfile.infolist():
                    ifile = zfile.open(finfo)
                    readCSV = csv.reader(io.TextIOWrapper(ifile), delimiter=',')
                    headers = next(readCSV, None)
                    for row in readCSV:
                        r.hmset("sc_code:"+row[0], {headers[0]: row[0], headers[1]: row[1].strip(), headers[4]: row[4], headers[5]: row[5], headers[6]: row[6], headers[7]: row[7]})
                        r.set("sc_name:"+row[1].strip(), row[0])
                        r.rpush("order_stock_list", row[0])
        except Exception as e:
            print(e)

    def get_redis_data(self):
        try:
            r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
            top_stock_lists = r.lrange("order_stock_list", 0, 9)
            data = []
            for stock in top_stock_lists:
                data.append(r.hgetall("sc_code:"+stock))
        except Exception as e:
            print(e)
        return data


class CherryRedis(object):
    @cherrypy.expose()
    def index(self):
        nse = NSEBhaveCopy()
        nse.load_zip_file()
        data = nse.get_redis_data()
        template = env.get_template('index.html')
        return template.render(stock_data=data)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def getData(self):
        search_string = cherrypy.request.json
        if not search_string:
            nse = NSEBhaveCopy()
            data = nse.get_redis_data()
            return data
        r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
        stock_list = r.keys("sc_name:*"+search_string+"*")
        stock_data = []
        for stock in stock_list:
            stoc_id = r.get(stock)
            stock_data.append(r.hgetall("sc_code:"+stoc_id))
        return stock_data


cherrypy.config.update({'server.socket_host': '0.0.0.0', 'server.socket_port': int(os.environ.get('PORT', '8069'))})
conf = {
    '/': {
        'tools.sessions.on': True,
        'tools.staticdir.root': os.getcwd()
    },
    '/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': 'static'
    }
}
cherrypy.quickstart(CherryRedis(),'/',conf)

