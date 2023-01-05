"""
    Questo file serve nel caso si decidesse di configurare l'applicativo 
    su un server di produzione: Nginx, Apache
"""

import sys
sys.path.insert(0, "/var/www/html/blog.lab.it/")
from wsgi import app as application