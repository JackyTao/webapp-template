# -*- coding:utf-8 -*-

from config_base import *


#########################################
#     -*-   online settings   -*-
#########################################

QUAN_SERVER_HOST = "http://quan.sohuno.com"
TAG_NAME = u'搜狐拍客'
HOST_NAME = 'changquantest.blog.sohu.com'

settings = dict(
    template_path=os.path.join(CURRENT_DIR, '../', 'templates'),
    static_path=os.path.join(CURRENT_DIR, '../', 'static'),
    debug=True,
    login_url='/auth/login')
