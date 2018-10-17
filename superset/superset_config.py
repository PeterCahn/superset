#---------------------------------------------------------
# Superset specific config
#---------------------------------------------------------
AAAAAROW_LIMIT = 5000

SUPERSET_WEBSERVER_PORT = 8088

# The file upload folder, when using models with files
UPLOAD_FOLDER = '/home/superset/uploaded/csv/'

# The image upload folder, when using models with images
IMG_UPLOAD_FOLDER = '/home/superset/uploaded/images/'

SUPERSET_WORKERS = 2  # deprecated
SUPERSET_CELERY_WORKERS = 32 # deprecated

#---------------------------------------------------------

#---------------------------------------------------------
# Flask App Builder configuration
#---------------------------------------------------------
# Your App secret key
SECRET_KEY = '\2\1thisismyscretkey\1\2\e\y\y\h'

# The SQLAlchemy connection string to your database backend
# This connection defines the path to the database that stores your
# superset metadata (slices, connections, tables, dashboards, ...).
# Note that the connection information to connect to the datasources
# you want to explore are managed directly in the web UI
SQLALCHEMY_DATABASE_URI = 'sqlite:////var/lib/superset/superset.db'
#SQLALCHEMY_DATABASE_URI = 'postgresql://postgres@tst-kubenode1.pochdp.csi.it:32754/postgres'

# Flask-WTF flag for CSRF
WTF_CSRF_ENABLED = True
# Add endpoints that need to be exempt from CSRF protection
WTF_CSRF_EXEMPT_LIST = []
# A CSRF token that expires in 1 year
WTF_CSRF_TIME_LIMIT = 60 * 60 * 24 * 365

# Set this API key to enable Mapbox visualizations
MAPBOX_API_KEY = ''

PUBLIC_ROLE_LIKE_GAMMA = True

CACHE_DEFAULT_TIMEOUT = 60 * 60 * 24
CACHE_CONFIG = {
        'CACHE_TYPE': 'filesystem',
        'CACHE_DIR': '/home/superset/temp',
        'CACHE_DEFAULT_TIMEOUT': CACHE_DEFAULT_TIMEOUT,
        }
#TABLE_NAMES_CACHE_CONFIG = {'CACHE_TYPE': 'filesystem'}