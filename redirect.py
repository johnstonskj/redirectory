import re, socket, sys
import urllib2, httplib

RE_META = re.compile("\s*<meta\s+http-equiv\s*=\s*\"Refresh\"\s+content\s*=\s*\"(?P<target>[^\"]+)", re.IGNORECASE)
MAX_TIMEOUT=5 # seconds

class SmartRedirectHandler(urllib2.HTTPRedirectHandler): 
    """ copied from the web this intercepts the redirect logic and stashes away the target location """
    def __init__(self):
        # Only used to store the details on redirect
        self.target = self.method = None

    def http_error_301(self, req, fp, code, msg, headers):
        self.target = headers["Location"]
        self.method = "301"
        return None

    def http_error_302(self, req, fp, code, msg, headers):
        self.target = headers["Location"]
        self.method = "302"
        return None


def process_host(host):
    """ process either hostname or URL """
    if host[:4] != "http":
        host = "http://" + host
    target = None
    method = None
    # Create request using http by default; if you want https you need to ask for it
    request = urllib2.Request(host)
    handler = SmartRedirectHandler()
    opener = urllib2.build_opener(handler)
    try:
        f = opener.open(request, timeout=MAX_TIMEOUT)
        content = f.readlines()
        # Look for HTML redirect in meta tags, this wont be needed on an HTTP redirect
        for line in content:
            # generally the content looks like n;url=<value> where n is the delay in seconds
            match = RE_META.match(line)
            if match != None:
                target = match.group("target").lower()
                index = target.find("url=")
                if index >= 0:
                    target = target[index+4:]
                    method = "meta tag"
                    break
    except urllib2.HTTPError, err:
        if err.code == 301 or err.code == 302:
            # we only process these standard redirects
            target = handler.target
            method = handler.method
        else:
            target = str(err)
    except urllib2.URLError, err:
        # turns out some socket timeouts end up here
        target = "ERROR (URL): " + str(err.reason)
    except socket.timeout:
        # even though true timeouts end up here
        target = "SOCKET TIMEOUT"
    except:
        # anything else ends up here
        err = sys.exc_info()[0]
        target = "ERROR processing %s: %s" % (host, str(err))
    if not target is None:
        # a redirect, or error
        print "%s, %s, %s" % (host, target, method)
    else:
        # no redirection occured
        print "%s, %s, NO REDIRECT" % (host, host)

def process_file(filename):
    """ process a file where each line is a host name or URL """
    with open(filename) as f:
        for line in f:
            process_host(line.strip())

if len(sys.argv) == 2:
    process_host(sys.argv[1])
elif len(sys.argv) == 3 and sys.argv[1] == "-f":
    process_file(sys.argv[2])
else:
    print "Usage: python redirect.py (hostname | -f filename)"
