# -*- coding: utf-8 -*-

import logging, requests, json

_logger = logging.getLogger(__name__)


class IPCountry(object):

    def conutry(self, request=False, ip=False):
        if request:
            if request.httprequest.environ.get('HTTP_X_REAL_IP'):
                ip = request.httprequest.environ.get('HTTP_X_REAL_IP')
            else:
                ip = request.httprequest.environ.get('REMOTE_ADDR')
        try:
            url = 'https://api.ipdata.co/' + ip + '/zh-CN?api-key=711bdbbbdb292be37d625a22bf9706a435764be5dc8e527322c682c8'
            data = requests.get(url)
            res = json.loads(data.content)
        except Exception as e:
            _logger.error(e.message)
            return None
        return res.get('country_name')
