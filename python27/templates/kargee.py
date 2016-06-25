# -*- coding: utf-8 -*-
"""
Created on Wed Aug 13 16:17:45 2014

@author: karthik.ganapathy
"""

import cgi
form_data = cgi.FieldStorage()
file_data = form_data['myfile'].value