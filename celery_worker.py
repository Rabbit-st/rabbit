#!/usr/bin/env python3
#-*- coding:utf-8 -*-

import os
from app import celery, create_app

app = create_app()
app.app_context().push()
