import re, socket, sys
import urllib2, httplib
from HTMLParser import HTMLParser

MAX_TIMEOUT=5 # seconds

class SmartRedirectHandler(urllib2.HTTPRedirectHandler): 
    """ copied from the web this intercepts the redirect logic and stashes away the target location """
    def __init__(self):
        # Only used to store the details on redirect
        self.target = self.method = None

    def http_error_301(self, req, fp, code, msg, headers):
        self.target = headers["Location"]
        self.method = "HTTP 301"
        return None

    def http_error_302(self, req, fp, code, msg, headers):
        self.target = headers["Location"]
        self.method = "HTTP 302"
        return None

class MyHTMLParser(HTMLParser):
    def __init__(self):
        self.target = None
        self.title = ''
        self.current = None
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        name = tag.lower()
        if name == 'meta':
            equiv = target = None
            for (name, value) in attrs:
                if name == 'http-equiv':
                    equiv = value
                elif name == 'content':
                    target = value
            if equiv == 'Refresh':
                target = target.lower()
                index = target.find("url=")
                if index >= 0:
                    self.target = target[index+4:]
        elif name == 'title':
            self.current = 'title'
    def handle_endtag(self, tag):
        self.current = None
    def handle_data(self, data):
        if self.current == 'title':
            self.title = self.title + data

def parse_options():
    from optparse import OptionParser
    
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="input", 
                      help="Input file, one URL per line")
    parser.add_option("-o", "--output", dest="output", 
                      help="Output file, as CSV")
    parser.add_option("-p", "--protocol", dest="protocol", default="http",
                      help="default protocol if not specified (http)")
    parser.add_option("-t", "--gateway-title", dest="title", default="internet authorization",
                      help="What page title indicates the authentication gateway page?")
    (options, args) = parser.parse_args()
    if not options.input and len(args) == 0:
        parser.print_help()
    return (options, args)

def process_host(host, options):
    """ process either hostname or URL """
    if host[:4] != "http":
        host = "%s://%s" % (options.protocol, host)
    target = None
    method = None
    # Create request using http by default; if you want https you need to ask for it
    request = urllib2.Request(host)
    handler = SmartRedirectHandler()
    opener = urllib2.build_opener(handler)
    try:
        f = opener.open(request, timeout=MAX_TIMEOUT)
        content = f.read()
        parser = MyHTMLParser()
        parser.feed(content)
        if not parser.target is None:
            target = parser.target
            method = 'META'
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
        raise
    if not target is None:
        # a redirect, or error
        print >> options.outputf, "%s, %s, %s" % (host, target, method)
    else:
        # no redirection occured
        print >> options.outputf, "%s, %s, NO REDIRECT" % (host, host)

def process_file(filename, options):
    """ process a file where each line is a host name or URL """
    with open(filename) as f:
        for line in f:
            process_host(line.strip(), options)

(options, args) = parse_options()

if options.output:
    options.outputf = open(options.output, 'wt')
else:
    options.outputf = sys.stdout

if options.input:
    process_file(options.input, options)
for host in args:
    process_host(host, options)

if options.output:
    options.outputf.close()
