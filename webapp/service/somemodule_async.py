import json
import tornado.gen
import util.log
import quan_interface as quan
from conf.config import QUAN_SERVER_HOST

logger = util.log.LogService().getLogger()


# Comment
@tornado.gen.coroutine
def post_comment_for_topic(params, cookies=''):
    """ new comment
        reply if replied_id is given
        See:
    """
    topic_id = params['topic_id']
    url = "{host}/api/topics/{topic_id}/comments".format(
        host=QUAN_SERVER_HOST,
        topic_id=topic_id)
    r = yield quan.inner_call(
        url, params=params, method='POST', cookies=cookies, as_form=True)
    r = json.loads(r) if r else {}

    if 'data' in r:
        cmt_id = r['data']
    else:
        cmt_id = ''  # TODO: error handling
    raise tornado.gen.Return(cmt_id)


@tornado.gen.coroutine
def get_sid_by_access_token(params):
    url = 'http://rest.plus.sohuno.com/spassportrest/token/parse'
    r = yield quan.inner_call(url, params=params, method='POST', as_form=True)
    r = json.loads(r) if r else {'code': 1}

    if r['code'] == 0:
        sid = str(r['data']['sid'])
    else:
        sid = ''    # TODO: error handling
    raise tornado.gen.Return(sid)

if __name__ == '__main__':
    pass
