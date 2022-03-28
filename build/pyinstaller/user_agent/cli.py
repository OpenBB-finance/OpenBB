from argparse import ArgumentParser
import json

from user_agent import generate_navigator_js


def script_ua():
    parser = ArgumentParser()
    parser.add_argument('-e', '--extended', action='store_true',
                        default=False)
    parser.add_argument('-o', '--os')
    parser.add_argument('-n', '--navigator')
    parser.add_argument('-d', '--device-type')
    opts = parser.parse_args()
    nav = generate_navigator_js(os=opts.os,
                                navigator=opts.navigator,
                                device_type=opts.device_type)
    if opts.extended:
        print(json.dumps(nav, indent=2))
    else:
        print(nav['userAgent'])
