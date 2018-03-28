# use hammock from https://github.com/kadirpekel/hammock
# use antigate from https://github.com/gotlium/antigate
# 2ec03ba74ad16d2da9b30a2d94ab2a6a antigate API key

import argparse
from termcolor import colored
from grab.spider import Spider, Task
from hammock import Hammock as GendreAPI
import logging
from antigate import AntiGate


parser = argparse.ArgumentParser(description = "Spider for site: http://meetup.com")
parser.add_argument("-u", "--users", dest="u", help="User email list. Format: mail:pass")
parser.add_argument("-p", "--proxy", dest="p", help="Proxy list. Format: ip:port")
parser.add_argument("-w", "--proxy-pr", dest="w", help="Proxy protocol")
parser.add_argument("-t", "--treads", dest="t", help="Threads")
parser.add_argument("-f", "--first-name", dest="f", help="User first name list")
parser.add_argument("-l", "--last-name", dest="l", help="User last name list")
args = parser.parse_args()


def zip_info(emails, fnames, lnames):
    try:
        e = open(emails, "r").readlines()
        f = open(fnames, "r").readlines()
        l = open(lnames, "r").readlines()
    except Exception as e:
        print colored("Please read help: ", "red") + "python meetupbot.py --help 'or' -h"
    return zip(e, f, l)


# Check gender from username
def check_gendre(fname, lname):
    gendre = GendreAPI("http://api.namsor.com/onomastics/api/json/gendre")
    response = gendre(fname, lname).GET()
    return response.json().get('gender')


# Start registration
class RegisterSpider(Spider):
    initial_urls = ["https://secure.meetup.com/register/"]

    # First page
    def task_initial(self, grab, task):
        for user in zip_info(args.u, args.f, args.l):
            grab.doc.set_input("realname", "%s %s" % (user[1].rstrip("\n"), user[2].rstrip("\n")))
            grab.doc.set_input("email", "%s" % user[0].split(":")[0])
            grab.doc.set_input("password", "%s" % user[0].rstrip("\n").split(":")[1])
            grab.doc.submit(make_request=False, submit_name="doSubmit")
            yield Task("more_info", grab=grab, gender=check_gendre(user[1].rstrip("\n"), user[2].rstrip("\n")))

    # Second page
    def task_more_info(self, grab, task):
        print grab.doc.select("//body").html()
        grab.doc.save("//tmp/h.html")


if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    bot = RegisterSpider(thread_number=2, priority_mode="const")
    bot.run()