# Introduction

Simple script to report on the redirect status of one or more URLs. The results are expressed in a CSV format allowing reporting for batches of URLs. The script reports on both HTTP redirect status codes (3xx) as well as HTML meta tag redirects.

This depends on [Python](https://www.python.org/downloads/).

## Simple example

In this case, simply provide either a full URL or a hostname (and HTTP will be assumed) on the command line.

    $ python redirect.py www.amazon.com
    
Note that you can also add "-p https" to set the default protocol to something other that "http://" when constructing URLs from simple host names.
  
## Input list example

In this case simply prepare an input file that contains either a full URL or a hostname on each line.

    $ python redirect.py -i listofurls.txt -o results.csv
  
## Results format

The following is the format for each row of the response:

    input-URL, (redirected-url | error), (redirect-type | "None")
    
* input-url - the URL requested
* redirected-url - any URL that the page redirects to
* error - any error status/message whn retrieving the URL
* redirect-type - either "NO REDIRECT", "HTTP", "META" to denote how the page redirects
* None - denotes that an error occured.

