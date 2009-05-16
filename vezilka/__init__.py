# Create a global singleton application instance, this means 
# this applicaiton can't be used more than once in a single 
# interpreter. Maybe rethink this?
from main import make_app
application = make_app()
