import os
from Flask import Flask



def create app():
  app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(__file__), "static", "frontend", "dist"),
        static_url_path=''
  )
   
