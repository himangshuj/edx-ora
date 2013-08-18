"""
sokratik config for ora,, uses postgres and low cost aws settings. no theming is involved here
interfaces with config repo integrated into bitbucket
"""

__author__ = 'vulcan'

from settings import *
import json
from logsettings import get_logger_config
from os.path import expanduser

HOME_FOLDER = path(expanduser("~"))
CONFIG_ROOT = HOME_FOLDER / "sokratik-infra/json-configs"
# specified as an environment variable.  Typically this is set
# in the service's upstart script and corresponds exactly to the service name.
# Service variants apply config differences via env and auth JSON files,
# the names of which correspond to the variant.
SERVICE_VARIANT = os.environ.get('SERVICE_VARIANT', "ora")

# when not variant is specified we attempt to load an unvaried
# config set.
CONFIG_PREFIX = ""

if SERVICE_VARIANT:
    CONFIG_PREFIX = SERVICE_VARIANT + "."

with open(CONFIG_ROOT / CONFIG_PREFIX + "env.json") as env_file:
    ENV_TOKENS = json.load(env_file)
REQUESTS_TIMEOUT = int(ENV_TOKENS.get('REQUESTS_TIMEOUT', REQUESTS_TIMEOUT))
TIME_BETWEEN_XQUEUE_PULLS = int(TIME_BETWEEN_XQUEUE_PULLS)
TIME_BETWEEN_EXPIRED_CHECKS = int(ENV_TOKENS.get('TIME_BETWEEN_EXPIRED_CHECKS', TIME_BETWEEN_EXPIRED_CHECKS))
MAX_NUMBER_OF_TIMES_TO_RETRY_GRADING = int(ENV_TOKENS.get('MAX_NUMBER_OF_TIMES_TO_RETRY_GRADING'))

#ML
MIN_TO_USE_ML = int(ENV_TOKENS.get('MIN_TO_USE_ML', MIN_TO_USE_ML))
ML_MODEL_PATH = os.path.join(HOME_FOLDER, ENV_TOKENS.get('ML_MODEL_PATH'))
TIME_BETWEEN_ML_CREATOR_CHECKS = int(ENV_TOKENS.get('TIME_BETWEEN_ML_CREATOR_CHECKS', TIME_BETWEEN_ML_CREATOR_CHECKS))
TIME_BETWEEN_ML_GRADER_CHECKS = int(TIME_BETWEEN_ML_GRADER_CHECKS)
USE_S3_TO_STORE_MODELS = ENV_TOKENS.get('USE_S3_TO_STORE_MODELS', USE_S3_TO_STORE_MODELS)
if isinstance(USE_S3_TO_STORE_MODELS, basestring):
    USE_S3_TO_STORE_MODELS = USE_S3_TO_STORE_MODELS.lower() == "true"
S3_BUCKETNAME = ENV_TOKENS.get('S3_ORA_BUCKETNAME', "OpenEnded")

#Peer
MIN_TO_USE_PEER = int(ENV_TOKENS.get('MIN_TO_USE_PEER', MIN_TO_USE_PEER))
PEER_GRADER_COUNT = int(ENV_TOKENS.get('PEER_GRADER_COUNT', PEER_GRADER_COUNT))
PEER_GRADER_MINIMUM_TO_CALIBRATE = int(
    ENV_TOKENS.get("PEER_GRADER_MINIMUM_TO_CALIBRATE", PEER_GRADER_MINIMUM_TO_CALIBRATE))
PEER_GRADER_MAXIMUM_TO_CALIBRATE = int(
    ENV_TOKENS.get("PEER_GRADER_MAXIMUM_TO_CALIBRATE", PEER_GRADER_MAXIMUM_TO_CALIBRATE))
PEER_GRADER_MIN_NORMALIZED_CALIBRATION_ERROR = float(
    ENV_TOKENS.get("PEER_GRADER_MIN_NORMALIZED_CALIBRATION_ERROR", PEER_GRADER_MIN_NORMALIZED_CALIBRATION_ERROR))

#Submission Expiration
EXPIRE_SUBMISSIONS_AFTER = int(ENV_TOKENS.get('EXPIRE_SUBMISSIONS_AFTER', EXPIRE_SUBMISSIONS_AFTER))
RESET_SUBMISSIONS_AFTER = int(ENV_TOKENS.get('RESET_SUBMISSIONS_AFTER', RESET_SUBMISSIONS_AFTER))

#Time zone (shows up in logs)
TIME_ZONE = ENV_TOKENS.get('TIME_ZONE', TIME_ZONE)

local_loglevel = ENV_TOKENS.get('LOCAL_LOGLEVEL', 'INFO')
LOG_DIR = ENV_TOKENS.get("LOG_DIR", ENV_ROOT / "log")

LOGGING = get_logger_config(debug=DEBUG)
with open(CONFIG_ROOT / CONFIG_PREFIX + "auth.json") as auth_file:
    AUTH_TOKENS = json.load(auth_file)
SECRET_KEY = AUTH_TOKENS.get("SECRET_KEY")
XQUEUE_INTERFACE = AUTH_TOKENS['XQUEUE_INTERFACE']
GRADING_CONTROLLER_INTERFACE = AUTH_TOKENS['GRADING_CONTROLLER_INTERFACE']
DATABASES = AUTH_TOKENS['DATABASES']


AWS_ACCESS_KEY_ID = AUTH_TOKENS.get("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = AUTH_TOKENS.get("AWS_SECRET_ACCESS_KEY", "")
#Celery settings
BROKER_URL = AUTH_TOKENS.get("BROKER_URL", "")
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_RESULT_BACKEND = AUTH_TOKENS.get("BROKER_URL", "")
