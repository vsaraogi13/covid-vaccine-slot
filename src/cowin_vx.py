import requests
import datetime
import base64
import time
import sys
import re
import os
import copy
import json

from apscheduler.schedulers.background import BackgroundScheduler

from hashlib import sha256
from flask import Flask, request, jsonify

CAPTCHA_MODEL = '''eyJNTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExMUUxMUUxMUUxMUUxMUUxMUUxMUVpNTExRTExMUUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTExRTExRTExRTExRTExRTExMUUxMTFFMTFFaIjoiMiIsIk1MTFFMTFFMTFFMTFFMTExRTExRTExRTExRTExRTExRTExRTExMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUVpNTExRTExRTExRTExRTExRTExMTFFMTFFMTFFMTFFMTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExMTFFMTFFMTFFMTFFMTFFMTFFMTExMUUxMUUxMUUxMUUxMUUxMUUxMTExMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFaIjoiMyIsIk1MTFFMTFFMTFFMTFFaTUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFaTUxMUUxMTFFMTFFMTFFMTFFMTFFMTFFMTExRTExMUUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTExRTExRTExRTExRWk1MTFFMTFFMTFFMTFFMTFFaIjoiNCIsIk1MTFFMTFFMTFFMTFFMTFFMTFFMTFFMTExMUUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFaTUxMUUxMUUxMUUxMUUxMTExMUUxMTFFMTExRTExRTExRTExMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMTExRTExRTExRTExRTExRWiI6IjUiLCJNTExRTExRTExRTExRTExRTExRTExRTExRTExRWk1MTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFaTUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMTExRTExRTExRTExMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUVpNTExRTExRTExRTExRTExRTExRTExRTExRWiI6IjYiLCJNTExRTExRTExMUUxMUUxMUUxMUUxMUUxMTFFMTFFMTExRTExRTExRTExMUUxMUUxMUUxMUUxMUVpNTExMUUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTExMTFFMTFFMTFFMTFFMTFFMTExRTExMUUxMUUxMUUxMTFFaIjoiNyIsIk1MTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFaTUxMUUxMUUxMUUxMUUxMUUxMUUxMUVpNTExMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUVpNTExMUUxMUUxMUUxMUUxMTExMUUxMUUxMUUxMUUxMTExRTExMUUxMUUxMUUxMUUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTFFaTUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUVpNTExRTExMUUxMUUxMUUxMUUxMUUxMUVoiOiI4IiwiTUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFaTUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFaTUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTExRTExRTExRTExRTExMUVpNTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRWiI6IjkiLCJNTExRTExRTExRTExRTExRTExRTExRTExRWk1MTFFMTExRTExRTExRTExRTExRTExRTExMUUxMUUxMUUxMUUxMTFFMTExRWiI6InYiLCJNTExRTExRTExRTExRTExRTExRTExRTExRTExMUUxMTFFMTFFMTFFMTExRTExRTExRTExRWk1MTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTExRWiI6IloiLCJNTExRTExRTExRTExRTExRTExRTExRTExRWk1MTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFaTUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFaTUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUVoiOiJkIiwiTUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFaTUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTExRTExRTExRTExRTExRTExMUVoiOiJ4IiwiTUxMUUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFaTUxMUUxMUUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTFFMTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExMUUxMUUxMUUxMUUxMUVoiOiJNIiwiTUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUVpNTExRTExRTExRTExRTExRTExRTExRTExMUUxMUUxMUUxMTFFMTExRTExRTExRTExRTExRWk1MTFFMTFFMTFFMTFFMTExMTFFMTExRTExRTExMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTFFMWk1MTFFMTFFMTFFMTFFMTExRTExMUUxMTFFMTFFaIjoicCIsIk1MTFFMTExRTExRTExRTExMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMTFFMTFFaTUxMUUxMUUxMTFFMTFFMTFFMTFFMTFFMTExRTExRTExMUUxMTExRTExRTExMUUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFaIjoiZiIsIk1MTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTExRTExRTExRTExRTExRTExMUUxMUUxMUUxMUVpNTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExMUUxMUUxMUUxMTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRWiI6IkUiLCJNTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRWk1MTFFMTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRWiI6Im4iLCJNTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRWk1MTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFaTUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMTFFMTFFMTFFaTUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUVoiOiJxIiwiTUxMUUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTExRTExRTExRTExRTExRTExMUVpNTExRTExRTExRTExRTExRTExMUUxMUUxMUUxMUUxMTFFMTExRTExRTExRTExMUUxMUUxMUUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTFoiOiJ3IiwiTUxMUUxMUUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTExRTExMUUxMUUxMUUxMUUxMUUxMUUxMTFFaTUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMTFFMTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExMUUxMUUxMUUxMUUxMUUxMUUxMUVoiOiJXIiwiTUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFaTUxMTExMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUVoiOiJKIiwiTUxMUUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFaTUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUVoiOiJUIiwiTUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUVpNTExRTExRTExRTExRTExRTExRWk1MTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFaTUxMUUxMUUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTExRTExRTExRWk1MTFFMTFFMTFFMTFFMTExRTExRTExRTExRWk1MTExRTExMTExRTExMUUxMUUxMUUxMUUxMUUxMUVoiOiJCIiwiTUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFaTUxMUUxMUUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFaIjoiSCIsIk1MTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTExRTExRTExRTExRWk1MTFFMTFFMTFFMTFFMTFFMTFFMTExMUUxMUUxMUUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTFpNTExMWiI6InIiLCJNTExRTExRTExRTExRTExRTExRTExRTExMUUxMUVpNTExRTExMUUxMUUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTExRTExRWiI6InkiLCJNTExRTExRTExRTExRTExRTExRTExRTExRTExMUUxMUUxMUUxMUUxMUUxMTFFMTFFMTFFaTUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMTFFMTFFMTFFMTExMTFFMTFFMTExRTExRTExRTExRTExRTExRTExRTExRWiI6InUiLCJNTExRTExRTExRTExRTExRTExRTExRTExRTExMUUxMUUxMUUxMUUxMUUxMUVpNTExRTExRTExaTUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMTFFMTFFMTExRTExRTExRTExRTExRTExMUUxMTExRTExRWk1MTExRTExRTExRTExRTExRTExRTExRWiI6ImoiLCJNTExRTExRTExMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUVpNTExRTExRTExRTExRTExRTExRTExMUUxMTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExMTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRWiI6IlMiLCJNTExMUUxMUUxMUUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTFFMTExRTExRTExRTExRTExRTExRTExRTExRTExRWk1MTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTExMTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExMUUxMUUxMTExRTExRTExRTExMUUxMUVoiOiJzIiwiTUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUVpNTExRTExRTExRTExMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUVoiOiJDIiwiTUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExMUUxMUUxMUVpNTExRTExRTExRTExRTExMUUxMUUxMUUxMUUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTExRTExRTExRTExRTExRTExRTExRTExMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMTFFMTFoiOiJHIiwiTUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUVpNTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRWk1MTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTExRWk1MTFFMTFFMTFFMTFFMTFFMTFFMTFFMTExRWiI6ImIiLCJNTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRWk1MTFFMTFFMTFFMTFFMTFFMTFFMTFFMTExRTExRTExRTExRTExRTExRTExRTExRTExRTExMUUxMUUxMUUxMUUxMUUxMTFFMTFFaIjoiaCIsIk1MTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMWk1MTFFMTExRTExRTExRTExRTExRTExRTExRTExRTExMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUVoiOiJOIiwiTUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTFFMTFFaTUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMTFFMTExRTExRTExRTExRTExRTExRTExRTExRTExRWiI6InoiLCJNTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUVpNTExRTExRTExRTExRTExRTExRTExRTExMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTFFMTExRTExRTExMUUxMUUxMUUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTExRTExRWk1MTExaIjoibSIsIk1MTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFaTUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMTExRTExRTExRTExRTExRTExRTExMUUxMUUxMUUxMUVoiOiJYIiwiTUxMUUxMUUxMUUxMUUxMTFFMTFFMTFFMTExRTExRTExRTExRTExRWk1MTFFMTExRTExRTExRTExRTExRTExRTExRTExRTExRTExMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTExRTExMUUxMUUxMUVoiOiJ0IiwiTUxMUUxMUUxMUUxMUUxMUUxMUUxMTFFMTFFMTFFMTExRTExMUUxMUUxMUUxMUUxMUVpNTExRTExMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUVpNTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExMTFFMTFFMTFFMTFFMTFFMTFFMTFFaTUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMTFFMTFFMTExMTFFMTFFMTFFaIjoiUSIsIk1MTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFaTUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTExRTExRTExRTExRTExRTExRTExRTExRWk1MTFFMTFFMTFFMTFFMTFFMTExRTExMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTExMUUxMUUxMUUxMUUxMUUxMTFFMTExRTExRTExMUUxMTFFaTUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUVoiOiJnIiwiTUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFaTUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFaIjoiViIsIk1MTFFMTFFMTFFMTFFMTFFMTFFMTFFaTUxMUUxMTFFMTFFMTFFMTFFMTFFMTExRTExRTExRTExRTExRTExRTExRTExRWk1MTExRTExRTExRTExRTExRTExRTExMUUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTFFMTExRTExRWk1MTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFaIjoiYSIsIk1MTFFMTFFMTFFMTFFMTFFaTUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFaTUxMTFFMTFFMTFFMTFFMTFFMTExRTExMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUVpNTExRTExMUVoiOiJBIiwiTUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTExRTExRTExRWk1MTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTExRTExRTExRTExRTExMUUxMUUxMUUxMUUxMUUxMUVoiOiJGIiwiTUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFaTUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUVoiOiJVIiwiTUxMUUxMUUxMUUxMUUxMUUxMUVpNTExRTExRTExRTExRTExRTExRTExRTExMUUxMUUxMTFFMTFFMTFFaTUxMTExRTExRTExRTExMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMTFFMTFFMTFFaTUxMUUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFaIjoiUiIsIk1MTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFaTUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUVpNTExRTExRTExRTExMUUxMUUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFaTUxMUUxMUUxMUUxMUUxMUUxMUUxMUVoiOiJEIiwiTUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTExRTExRTExRTExRTExRTExRTExMUUxMUUxMUVpNTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExRTExMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMTExRTExRTExRWiI6ImMiLCJNTExRTExRTExRTExRTExRTExRTExRTExRTExRTExMUUxMUUxMUUxMUVpNTExRTExRTExRTExRTExMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUVoiOiJrIiwiTUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTFFMTFFMTExRTExRTExRTExMTExRWk1MTFFMTFFMTFFMTExRTExRTExMUUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFaIjoiSyIsIk1MTFFMTFFMTFFMTFFMTFFMTFFaTUxMUUxMUUxMUUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTFFMTExRTExRTExRTExRTExRWk1MTFFMTFFMTFFMTFFMTFFMTFFMTFFMTExRTExRTExRTExRTExMUUxMUUxMUUxMUUxMUUxMUUxMTFFaTUxMUUxMUUxMUUxMUUxMUVpNTExRTExMTFFMTFFMTFFaIjoiZSIsIk1MTExRTExRTExRTExRTExRTExRTExRTExRTExRWk1MTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTExRTExRTExRTExRTExaIjoiWSIsIk1MTFFMTFFMTExRTExRTExRTExRWk1MTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFMTFFaTUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMTFFMTFFMTFFMTFFMTFFaTUxMUUxMUUxMUUxMUUxMUUxMUUxMUUxMTFFaIjoiUCJ9'''
CAPTCHA_PARSE_MODEL = json.loads(base64.b64decode(CAPTCHA_MODEL))

GENERATE_OTP_SECRET_KEY = "U2FsdGVkX1+PNg3aRsB47jXG/bLLzfxl3jiKsi5t4ck5SlCUWW97NwxnXS8btRUz4EMSMrnN0sq18ls6IVabQw=="

MOBILE_NUMBER = 8758849692
DISTRICT_IDS = [772,770]
# PINCODES = ['7000']
ONLY_PAID_USER = False

BASE_URL = 'https://cdn-api.co-vin.in/api'

COWIN_TXN_ID = 'COWIN_TXN_ID'
COWIN_USER_TOKEN = 'COWIN_USER_TOKEN'
CENTER_ID = 'CENTER_ID'
SESSION_ID = 'SESSION_ID'
SLOT = 'SLOT'
BIDS = 'BIDS'

BENEFICIARIES = {}
ATTEMPTING_TO_BOOK = False

REQUEST_HEADER = {
    'authority': 'cdn-api.co-vin.in',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    'accept': 'application/json, text/plain, */*',
    'sec-ch-ua-mobile': '?0',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    'content-type': 'application/json',
    'origin': 'https://selfregistration.cowin.gov.in',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://selfregistration.cowin.gov.in/',
    'accept-language': 'en-US,en;q=0.9'
}


REQUEST_HEADER2 = {
    'accept': 'application/json, text/plain, */*',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    'content-type': 'application/json',
}



# def play_music(needMusic):
#     if needMusic:
#         sound = AudioSegment.from_file("/Users/nitin/Desktop/BabyElephantWalk60.wav", format="wav")
#     else:
#         sound = generators.Sine(440).to_audio_segment(duration=1500)
#         play(sound)
#     time.sleep(0.1)
#     play(sound)


def generate_sms():
    url = f'{BASE_URL}/v2/auth/generateMobileOTP'
    payload = {"mobile": MOBILE_NUMBER, "secret": GENERATE_OTP_SECRET_KEY}
    res = requests.post(url=url, headers=REQUEST_HEADER, json=payload)
    status_code = res.status_code
    if status_code == 200:
        data = res.json()
        os.environ[COWIN_TXN_ID] = data['txnId']
        print("SMS Sent")
    elif status_code == 403:
        print(f'SMS failed! status: {status_code}')
        time.sleep(60)
        generate_sms()
    else:
        print(f'SMS failed! status: {status_code}')


def verify_otp(otp):
    txn_id = os.getenv(COWIN_TXN_ID)
    if txn_id == None or len(txn_id) < 1:
        return

    url = f'{BASE_URL}/v2/auth/validateMobileOtp'
    payload = {"otp": sha256(str(otp).encode('utf-8')).hexdigest(), "txnId": txn_id}
    res = requests.post(url, json=payload, headers=REQUEST_HEADER)
    if res.status_code == 200:
        token = res.json()['token']
        os.environ[COWIN_USER_TOKEN] = token
        print(f'auth token success!! token: {token}')
    else:
        print("verify_otp failed")


def fetch_beneficiaries():
    global BENEFICIARIES
    if len(BENEFICIARIES) > 0:
        print("skipped beneficiaries fetch!!")
        return

    url = f'{BASE_URL}/v2/appointment/beneficiaries'
    headers = REQUEST_HEADER.copy()
    headers['authorization'] = 'Bearer ' + os.getenv(COWIN_USER_TOKEN)
    res = requests.get(url, headers=headers)
    status_code = res.status_code
    if status_code == 200:
        d = res.json()
        print(f'Beneficiary: {d}')
        for beneficiary in res.json()['beneficiaries']:
            name = beneficiary['name']
            bid = beneficiary['beneficiary_reference_id']
            print(f'{name}\t\t{bid}')
        BENEFICIARIES = res.json()
    elif status_code == 401:
        generate_sms()
    else:
        print(f'fetch_beneficiaries failed!! Status - {status_code}')


# "<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"150\" height=\"50\" viewBox=\"0,0,150,50\"><path fill=\"#333\" d=\"M75.40 29.56L75.36 29.52L75.30 29.46Q74.14 28.72 73.49 28.76L73.50 28.76L73.41 28.68Q72.18 28.89 71.14 29.90L71.01 29.78L71.06 29.83Q69.98 30.81 70.10 32.18L70.13 32.21L70.23 32.31Q70.55 36.66 69.67 41.19L69.65 41.17L69.55 41.07Q67.33 41.51 66.23 42.05L66.30 42.12L66.35 42.17Q67.82 37.97 67.59 33.51L67.57 33.50L67.52 33.45Q67.22 28.87 65.50 24.80L65.68 24.98L65.62 24.92Q66.73 25.57 69.02 26.22L69.00 26.21L69.49 28.83L69.62 28.96Q70.32 26.07 74.58 26.07L74.49 25.99L74.55 26.05Q74.84 25.88 75.14 25.88L75.21 25.94L75.15 25.89Q76.53 25.97 77.78 26.65L77.70 26.56L77.71 26.58Q76.55 28.08 75.41 29.57ZM76.90 31.44L77.03 31.42L77.01 31.40Q77.84 30.17 79.51 27.73L79.66 27.88L79.62 27.84Q79.14 27.47 77.61 27.21L77.55 27.14L77.60 27.19Q77.86 26.81 78.32 26.20L78.38 26.26L78.32 26.20Q76.58 25.45 74.64 25.64L74.48 25.48L74.50 25.50Q72.61 25.74 71.89 26.01L71.96 26.08L71.95 26.07Q70.59 26.53 69.79 27.64L69.72 27.58L69.43 26.64L69.39 25.95L69.41 25.97Q66.97 25.51 64.99 24.17L64.95 24.14L64.97 24.16Q67.11 28.54 67.34 33.41L67.31 33.39L67.28 33.36Q67.57 38.33 65.82 42.86L65.75 42.79L65.86 42.90Q66.88 42.36 67.76 42.06L67.63 41.92L67.75 42.05Q67.41 43.07 66.91 44.14L67.05 44.28L67.01 44.24Q69.84 43.38 71.97 43.26L71.91 43.20L72.08 38.65L72.15 38.72Q72.15 36.36 72.15 34.12L72.30 34.27L72.20 34.17Q72.28 33.07 73.20 32.10L73.23 32.13L73.08 31.98Q74.12 31.14 75.27 31.06L75.28 31.07L75.12 30.92Q75.90 30.93 76.62 31.62L76.55 31.54L76.88 31.42ZM71.88 29.61L72.07 29.73L71.95 29.73L71.98 29.72Z\"/><path d=\"M11 25 C86 48,60 16,138 27\" stroke=\"#111\" fill=\"none\"/><path d=\"M20 26 C87 41,62 44,140 36\" stroke=\"#555\" fill=\"none\"/><path fill=\"#333\" d=\"M45.78 27.71L45.69 27.62L45.79 27.72Q43.39 27.57 42.12 29.07L42.17 29.13L42.14 29.10Q41.02 30.75 40.91 33.04L40.77 32.90L40.75 32.88Q40.71 35.62 41.55 36.57L41.57 36.59L41.60 36.63Q42.65 37.83 44.97 37.67L44.93 37.63L44.87 37.58Q49.55 37.31 49.93 34.30L49.97 34.34L49.86 34.23Q50.04 33.49 50.04 32.69L49.98 32.63L49.99 32.65Q50.07 30.74 48.93 29.22L48.97 29.26L48.86 29.15Q47.68 27.63 45.74 27.67ZM50.45 37.63L50.61 37.80L50.45 37.63Q49.17 39.97 44.79 40.20L44.77 40.17L44.80 40.20Q40.57 40.32 38.93 39.21L38.95 39.23L38.96 39.24Q37.91 38.23 37.76 36.52L37.75 36.50L37.75 36.50Q37.71 35.39 37.90 33.53L37.94 33.58L37.89 33.53Q38.41 29.25 39.63 27.42L39.74 27.53L39.68 27.47Q41.29 24.97 45.13 25.01L45.10 24.97L45.04 24.91Q47.71 25.11 50.00 27.44L49.95 27.39L49.96 27.40Q50.11 21.60 51.71 15.09L51.58 14.97L51.56 14.95Q53.62 14.68 55.48 13.85L55.50 13.86L55.39 13.76Q52.77 20.35 52.51 27.35L52.55 27.40L52.46 27.31Q52.25 34.56 54.38 41.14L54.36 41.12L54.33 41.10Q52.67 40.47 50.96 40.08L51.06 40.19L51.09 40.21Q50.74 38.88 50.59 37.77ZM53.67 43.29L53.52 43.14L53.56 43.18Q55.68 43.77 58.23 45.30L58.25 45.32L58.20 45.27Q54.58 38.30 54.43 30.00L54.35 29.92L54.33 29.90Q54.13 21.63 57.22 14.25L57.34 14.37L57.27 14.30Q56.56 14.74 55.12 15.38L55.15 15.42L55.27 15.54Q55.54 14.32 56.15 13.10L56.13 13.08L56.21 13.16Q53.69 14.11 51.25 14.68L51.38 14.81L51.22 14.65Q49.89 20.55 49.62 26.64L49.57 26.59L49.57 26.59Q47.74 24.83 45.22 24.72L45.11 24.60L45.19 24.68Q41.71 24.51 39.81 26.61L39.75 26.55L39.87 26.68Q38.14 29.02 37.72 33.70L37.64 33.62L37.61 33.59Q37.48 36.46 37.48 36.88L37.36 36.76L37.32 36.72Q37.54 38.62 38.69 39.69L38.65 39.65L38.70 39.71Q38.87 39.87 39.06 39.94L38.95 39.84L39.51 40.59L39.59 40.67Q40.41 41.87 43.38 42.14L43.48 42.24L43.40 42.15Q45.63 42.33 47.00 42.40L47.12 42.53L46.98 42.39Q51.12 42.53 52.83 41.19L52.87 41.23L52.86 41.22Q53.18 42.11 53.63 43.25ZM47.26 29.88L47.34 29.95L47.40 30.01Q48.28 29.87 49.12 30.36L49.23 30.48L49.25 30.49Q49.58 31.63 49.66 32.65L49.70 32.70L49.75 32.75Q50.09 37.00 45.06 37.35L45.00 37.28L45.01 37.29Q44.14 37.33 43.03 37.07L42.96 37.00L42.95 36.98Q42.77 36.42 42.69 35.89L42.72 35.92L42.82 36.02Q42.68 35.27 42.72 34.66L42.78 34.72L42.75 34.70Q42.99 31.21 45.62 30.22L45.70 30.29L45.66 30.26Q46.62 29.89 47.31 29.92Z\"/><path fill=\"#333\" d=\"M92.99 19.34L92.93 19.28L92.91 19.27Q93.88 23.62 94.03 27.20L94.04 27.21L93.94 27.10Q95.03 27.17 96.10 27.17L96.18 27.25L98.30 27.16L98.35 27.21Q99.47 27.27 100.34 25.86L100.21 25.73L100.32 25.83Q101.08 24.70 101.20 23.52L101.02 23.34L101.03 23.35Q101.45 20.38 97.23 19.89L97.23 19.89L97.34 20.00Q95.71 20.01 93.09 19.44ZM94.06 29.96L93.98 29.89L93.99 29.89Q94.00 36.19 92.86 40.60L92.78 40.52L92.82 40.57Q91.30 40.91 88.98 41.98L88.99 42.00L89.10 42.10Q91.40 35.38 91.14 28.11L91.14 28.11L91.18 28.16Q90.76 20.66 87.98 14.22L88.10 14.34L88.15 14.39Q92.20 17.07 98.44 17.07L98.45 17.07L98.43 17.05Q104.60 17.17 104.76 20.64L104.75 20.64L104.66 20.55Q104.78 23.03 103.79 25.69L103.73 25.63L103.77 25.66Q103.43 26.85 102.48 28.07L102.39 27.98L102.33 27.92Q101.12 29.64 98.57 29.91L98.58 29.92L98.60 29.94Q96.30 29.92 94.05 29.96ZM100.17 32.20L100.08 32.11L100.25 32.28Q104.33 32.43 105.58 27.63L105.61 27.66L105.54 27.59Q106.58 24.03 106.43 22.01L106.46 22.04L106.40 21.98Q106.29 20.46 105.53 19.47L105.60 19.54L105.54 19.48Q105.14 19.09 104.65 18.86L104.69 18.90L104.57 18.77Q104.71 18.77 104.11 18.01L104.05 17.96L104.08 17.98Q102.50 16.63 98.54 16.63L98.59 16.68L98.45 16.54Q91.59 16.58 87.37 13.42L87.33 13.38L87.36 13.40Q90.60 20.57 90.87 28.03L90.75 27.92L90.76 27.92Q91.09 35.64 88.43 42.72L88.48 42.77L88.43 42.72Q89.58 42.16 90.57 41.78L90.47 41.68L90.19 42.92L90.25 42.99Q90.04 43.54 89.78 44.11L89.71 44.05L89.68 44.01Q92.17 43.04 95.06 42.51L95.07 42.51L94.97 42.41Q95.91 37.00 95.99 32.28L95.98 32.27L95.90 32.19Q96.98 32.08 97.97 32.08L98.12 32.24L98.05 32.17Q99.31 32.10 100.11 32.13ZM99.23 22.27L99.15 22.19L99.21 22.26Q99.69 22.24 100.68 22.47L100.73 22.52L100.74 22.52Q100.89 22.79 100.93 23.10L100.85 23.01L100.82 22.98Q100.81 23.20 100.73 23.47L100.75 23.49L100.89 23.62Q100.68 24.75 99.96 25.63L99.99 25.66L100.01 25.67Q99.31 26.62 98.28 26.81L98.33 26.85L98.36 26.88Q97.67 26.91 96.03 26.91L95.94 26.82L95.94 26.82Q95.90 24.54 95.67 22.18L95.68 22.18L97.54 22.37L97.48 22.31Q98.43 22.43 99.31 22.35Z\"/><path fill=\"#222\" d=\"M124.78 30.95L124.75 30.93L124.81 30.99Q124.84 29.50 124.02 28.58L123.90 28.46L123.99 28.55Q123.22 27.68 121.77 27.72L121.81 27.76L121.62 27.57Q119.38 27.73 118.54 29.86L118.61 29.93L118.47 29.79Q118.24 30.62 118.20 31.31L118.34 31.45L118.32 31.43Q117.98 36.15 117.07 40.49L117.06 40.49L117.12 40.55Q115.46 41.09 113.59 42.08L113.47 41.96L113.64 42.13Q115.79 35.02 115.52 27.71L115.60 27.79L115.60 27.79Q115.37 20.49 112.82 13.67L112.72 13.57L112.71 13.56Q114.59 14.99 116.61 15.67L116.50 15.56L116.45 15.51Q117.98 21.38 118.17 27.24L118.17 27.24L118.09 27.16Q119.61 25.22 122.32 25.30L122.23 25.21L122.20 25.18Q127.35 25.34 127.46 30.71L127.48 30.72L127.53 30.78Q127.70 36.51 129.07 41.15L129.02 41.10L129.05 41.13Q127.19 40.30 125.44 40.11L125.35 40.01L125.33 39.99Q124.91 36.84 124.80 30.97ZM125.04 40.35L125.11 40.42L125.00 40.31Q126.00 40.40 127.10 40.66L127.12 40.68L127.14 40.70Q127.20 40.88 127.73 42.86L127.81 42.94L127.71 42.83Q130.83 43.93 132.84 45.38L132.73 45.26L132.83 45.37Q130.12 39.58 129.59 33.26L129.60 33.26L129.60 33.27Q129.26 29.54 127.85 27.98L127.74 27.86L127.79 27.91Q127.77 27.82 127.13 27.36L127.16 27.40L127.06 27.30Q126.82 26.79 126.17 26.03L126.25 26.11L126.24 26.02L126.22 26.00Q125.41 25.19 122.29 24.93L122.23 24.86L122.22 24.85Q121.63 24.99 120.22 25.33L120.15 25.26L120.14 25.25Q119.85 20.31 119.50 17.80L119.60 17.90L119.61 17.90Q118.81 17.76 117.33 17.45L117.34 17.46L117.31 17.44Q117.13 16.69 116.87 15.20L116.86 15.19L116.89 15.22Q113.91 14.23 112.04 12.66L112.09 12.71L112.17 12.79Q115.08 19.89 115.35 27.69L115.24 27.58L115.22 27.57Q115.56 35.41 113.01 42.76L112.98 42.72L113.10 42.84Q114.04 42.26 115.19 41.77L115.19 41.77L114.32 43.92L114.47 44.06Q117.54 42.67 119.52 42.48L119.57 42.53L119.44 42.41Q120.05 37.04 120.24 33.08L120.18 33.02L120.15 32.99Q120.42 31.32 122.36 30.22L122.22 30.07L122.28 30.13Q122.74 29.83 123.28 29.87L123.28 29.87L123.40 30.00Q123.55 29.99 123.89 30.03L123.77 29.91L124.27 30.06L124.28 30.08Q124.24 30.42 124.36 30.88L124.37 30.89L124.44 30.96Q124.53 36.91 125.03 40.34Z\"/><path fill=\"#111\" d=\"M30.32 40.32L30.37 40.37L30.37 40.37Q27.45 36.54 24.82 27.90L24.80 27.88L24.72 27.79Q24.18 25.77 23.38 23.63L23.34 23.60L20.39 32.30L20.43 32.33Q18.53 37.18 16.13 40.41L16.26 40.54L16.31 40.59Q15.31 40.50 13.67 40.65L13.80 40.78L13.73 40.71Q13.84 39.53 13.84 38.27L13.90 38.33L13.95 38.38Q13.81 32.23 11.07 26.10L11.12 26.15L11.20 26.23Q7.90 19.16 2.04 14.18L2.09 14.23L2.05 14.18Q4.36 15.04 6.72 15.58L6.59 15.45L6.60 15.47Q15.33 23.96 16.62 34.92L16.52 34.82L16.61 34.91Q18.28 31.63 19.72 26.26L19.72 26.26L19.63 26.17Q21.75 18.81 22.24 17.40L22.10 17.25L24.38 17.29L24.50 17.41Q25.07 19.31 25.71 21.63L25.79 21.71L26.99 26.10L27.03 26.15Q28.64 31.64 30.05 34.88L30.04 34.87L29.94 34.77Q31.61 23.15 39.53 15.80L39.51 15.78L39.59 15.87Q41.12 15.52 44.08 14.88L44.11 14.90L44.08 14.87Q38.62 19.05 35.58 25.18L35.66 25.26L35.61 25.21Q32.60 31.53 32.60 38.31L32.60 38.30L32.63 38.33Q32.59 39.40 32.67 40.54L32.65 40.52L31.44 40.34L31.47 40.37Q30.91 40.35 30.34 40.35ZM36.55 43.21L36.53 43.19L36.71 43.36Q35.33 39.66 35.45 35.78L35.41 35.74L35.38 35.72Q35.84 24.29 45.20 16.03L45.16 15.99L45.17 16.00Q44.25 16.26 42.31 16.79L42.32 16.81L42.23 16.72Q43.27 15.97 45.18 14.18L45.05 14.05L45.09 14.09Q42.56 14.99 39.63 15.48L39.62 15.47L39.54 15.40Q32.11 22.58 30.20 32.06L30.20 32.05L30.23 32.09Q29.59 30.38 26.74 18.92L26.76 18.95L26.63 18.82Q26.40 19.08 25.45 19.08L25.35 18.98L25.15 18.02L24.96 17.83Q24.90 17.35 24.67 16.86L24.70 16.88L21.86 16.94L21.79 16.87Q21.03 19.38 19.75 24.50L19.72 24.47L19.73 24.48Q18.52 29.67 17.53 32.14L17.38 31.99L17.42 32.03Q15.92 24.21 10.37 17.89L10.30 17.83L10.25 17.78Q9.85 17.79 8.89 17.60L8.85 17.56L8.88 17.59Q8.09 16.69 6.53 15.05L6.53 15.05L6.64 15.16Q3.11 14.22 0.94 13.42L1.03 13.51L1.07 13.55Q6.75 18.24 10.03 24.45L10.01 24.43L9.94 24.36Q13.46 31.04 13.46 38.05L13.47 38.05L13.45 38.04Q13.46 39.60 13.27 41.20L13.17 41.10L13.29 41.23Q13.39 41.10 13.85 41.00L14.01 41.16L13.89 41.05Q14.43 41.03 14.66 41.03L14.61 40.99L14.64 42.04L14.53 41.93Q14.70 42.55 14.77 43.09L14.71 43.02L14.68 42.99Q15.86 42.96 18.15 42.81L18.03 42.69L18.08 42.74Q21.74 37.38 24.48 27.97L24.44 27.93L24.43 27.93Q27.29 36.79 30.26 40.75L30.28 40.78L30.30 40.80Q30.68 40.72 31.52 40.84L31.61 40.93L31.63 40.95Q32.48 41.99 33.54 43.05L33.39 42.90L33.45 42.96Q34.31 43.09 36.71 43.36Z\"/><path d=\"M4 39 C91 1,92 43,136 36\" stroke=\"#333\" fill=\"none\"/></svg>"
def get_captcha_code(svg):
    global CAPTCHA_PARSE_MODEL
    x = svg.split("><")
    x1 = []
    for i in x:
        if 'stroke' not in i:
            x1.append(i)
    svg = "><".join(x1)

    vals = []
    x2 = svg.split("><")
    for i in x2:
        j = i.split('''d="''')
        if len(j) > 1:
            j = j[1].split('.')[0].replace('M', '')
            vals.append(int(j))
    sortedVal = copy.deepcopy(vals)
    sortedVal.sort()

    sol = []
    for idx, i in enumerate(x2):
        j = i.split('''d="''')
        if len(j) > 1:
            pattern = re.sub(r'[\d\.\s]', '', j[1])[:-2]
            sol.append(CAPTCHA_PARSE_MODEL[pattern])

    solution = ['', '', '', '', '']
    for idx, i in enumerate(sol):
        solution[sortedVal.index(vals[idx])] = i

    res = ''.join(solution)
    print(f'*****\n\n svg: {svg}\ncaptcha: {res}\n\n*****')
    return res


def get_capcha():
    url = f'{BASE_URL}/v2/auth/getRecaptcha'
    headers = REQUEST_HEADER.copy()
    headers['authorization'] = 'Bearer ' + os.getenv(COWIN_USER_TOKEN)
    res = requests.post(url, headers=headers, json={})
    status_code = res.status_code
    if status_code == 200:
        print('fetched captcha!!')
        return get_captcha_code(res.json()['captcha'])
    elif status_code == 401:
        generate_sms()
    print(f'failed to fetch captcha!! status: {status_code}')
    return ""


def initate_booking(center_id, session_id, slot, beneficiaries, pincode):
    global ATTEMPTING_TO_BOOK
    if ATTEMPTING_TO_BOOK is False:
        code = get_capcha()
        if code != "":
            ATTEMPTING_TO_BOOK = True
            book_appointment(center_id, session_id, slot, beneficiaries, code, pincode)


def book_appointment(center_id, session_id, slot, beneficiaries, captcha, pincode):
    global BENEFICIARIES
    global ATTEMPTING_TO_BOOK
    url = f'{BASE_URL}/v2/appointment/schedule'
    headers = REQUEST_HEADER.copy()
    headers['authorization'] = 'Bearer ' + os.getenv(COWIN_USER_TOKEN)
    payload = {
        'beneficiaries': beneficiaries,
        'dose': 2,
        'center_id': center_id,
        'session_id': session_id,
        'slot': slot,
        'captcha': captcha
    }
    res = requests.post(url, headers=headers, json=payload)
    status_code = res.status_code
    if status_code == 200:
        print('------------ BOOKED ------------')
        print(f'Beneficiary: {beneficiaries}')
        print('------------ BOOKED ------------')
        BENEFICIARIES = {}
        fetch_beneficiaries()
        ATTEMPTING_TO_BOOK = False
    elif status_code == 401:
        generate_sms()
        ATTEMPTING_TO_BOOK = False
    else:
        print(f'Missed booking!! status: {status_code}')
        print(f'center_id: {center_id}\n session_id: {session_id}\n slot: {slot}\n beneficiaries: {beneficiaries}\n')
        ATTEMPTING_TO_BOOK = False
        fetch_on_pincode(pincode)


def select_beneficiary_and_book(center_id, session_id, slot, pincode):
    fetch_beneficiaries()
    global BENEFICIARIES
    beneficiaries = []
    for beneficiary in BENEFICIARIES['beneficiaries']:
        status = beneficiary['vaccination_status']
        #vaccine = beneficiary['vaccine']
        bid = beneficiary['beneficiary_reference_id']
        if len(beneficiaries) == 0 and len(beneficiary["dose2_date"]) == 0 and status == 'Partially Vaccinated':
            beneficiaries.append(bid)
    if len(beneficiaries) == 0:
        print('*' * 20)
        print('\n\nAnd the booking has completed for all\n\n')
        print('*' * 20)
        # play_music(False)
        sys.exit("Booking completed!!")
    print(f'attempting to book for {beneficiaries}')
    initate_booking(center_id, session_id, slot, beneficiaries, pincode)


def check_slot_and_booking(data):
    global ONLY_PAID_USER
    max_capacity = 0
    best_session = {}
    best_center_id = 0
    centers = data["centers"]
    for center in centers:
        #print(center)
        name = center['name']
        center_id = center["center_id"]
        sessions = center["sessions"]
        pincode = center['pincode']
        fee_type = center['fee_type']
        if fee_type != 'Free':
            continue
        for session in sessions:
            dose_count = session["available_capacity_dose2"]
            if session["min_age_limit"] < 45 and dose_count > max_capacity and session['vaccine'] == 'COVAXIN':
                #print(center_id)
                max_capacity = session["available_capacity_dose2"]
                best_center_id = center_id
                best_session = session
    if max_capacity > 0:
        session_id = best_session["session_id"]
        slot = best_session["slots"][-1]
        print('*' * 20)
        print(
            f'\nSlot found @pincode@{pincode} name:{name} session_id:{session_id} slot:{slot} capacity: {max_capacity}')
        print('*' * 20)
        select_beneficiary_and_book(best_center_id, session_id, slot, pincode)


def find_slot_with_pincode(date, pincode, explicit):
    url = f'{BASE_URL}/v2/appointment/sessions/calendarByPin?pincode={pincode}&date={date}'
    headers = REQUEST_HEADER.copy()
    if explicit:
        headers['authorization'] = 'Bearer ' + os.getenv(COWIN_USER_TOKEN)
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        if explicit:
            da = res.json()
            print(f'pincode: {pincode}, date: {date}, data: {da}')
        check_slot_and_booking(res.json())
    else:
        print(f'find slot failed for {date} - {pincode}')


def find_slot_with_district(date, district_id):
    url = f'{BASE_URL}/v2/appointment/sessions/public/calendarByDistrict?district_id={district_id}&date={date}'
    print(url)
    res = requests.get(url, headers=REQUEST_HEADER)
    print(res)
    #print(res.json())
    status_code = res.status_code
    if status_code == 200:
        check_slot_and_booking(res.json())
    elif status_code == 403:
        print(f'403 Error - Rate limit reached, sleep for 1 min')
        time.sleep(60)
    else:
        print(f'find slot failed for {date} - district_id: {district_id} - status_code: {status_code}')


def start_search_with_pincode(pincodes):
    today = datetime.datetime.today()
    print(f'retry@{today}')
    date = today.strftime("%d-%m-%Y")
    for pincode in pincodes:
        find_slot_with_pincode(date, pincode, False)


def fetch_on_pincode(pincode):
    print(f'try on pincode: {pincode}')
    today = datetime.datetime.today()
    date = today.strftime("%d-%m-%Y")
    find_slot_with_pincode(date, pincode, False)


def start_search_with_district_id(district_ids):
    today = datetime.datetime.today()
    tomorrow = today + datetime.timedelta(days=1)
    print(f'retry@{today}')
    date = today.strftime("%d-%m-%Y")
    for district_id in district_ids:
        find_slot_with_district(date, district_id)


generate_sms()
scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(generate_sms, 'interval', minutes=14)
scheduler.start()

# scheduler_2 = BackgroundScheduler(daemon=True)
# scheduler_2.add_job(start_search_with_pincode,'interval', [PINCODES],seconds=10)
# scheduler_2.start()


scheduler_5 = BackgroundScheduler(daemon=True)
scheduler_5.add_job(start_search_with_district_id, 'interval', [DISTRICT_IDS], seconds=12)
scheduler_5.start()

app = Flask(__name__)


@app.route('/otp', methods=['POST'])
def otp_receiver():
    otp = request.args.get('otp')
    verify_otp(otp)
    fetch_beneficiaries()
    response = jsonify(message="Job Started!")
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


@app.route('/pincode', methods=['POST'])
def pincode_search():
    pincode = request.args.get('pincode')
    fetch_on_pincode(pincode)
    response = jsonify(message="Attempting on pincode")
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


app.run()
