#! /usr/bin/env python
import os
import re
import requests
import sys

try:
    os.environ["BINTRAY_USERNAME"]
except KeyError:
    print "Please set the environment variable BINTRAY_USERNAME"
    sys.exit(1)

try:
    os.environ["BINTRAY_API_KEY"]
except KeyError:
    print "Please set the environment variable BINTRAY_API_KEY"
    sys.exit(1)

USERNAME = os.environ["BINTRAY_USERNAME"]
API_KEY = os.environ["BINTRAY_API_KEY"]


top = os.getcwd()

if os.path.basename(top) != 'REPO' :
    sys.stderr.write("Need to run from the $ONL/REPO directory\n")
    sys.exit(1)

for subdir, dirs, files in os.walk('.'):
    for f in files:
        if f.endswith(".deb"):
            parts = subdir.split(os.sep)  # should be "./jessie/packages/powerpc"
            if len(parts) != 4: 
                sys.stderr.write("WARN: Skipping unparsed file %s in subdir %s\n" % ( f, subdir))
                continue
            release = parts[1] # grab the release name
            arch = parts[3] # grab the package architecture
            filedir = subdir + os.sep + f # assemble the relative path to the package
            firstchars_split = re.split(r'(\-|\_)', f) # split off the first few chars as the package name
            package = str(firstchars_split[0]) # pull the first part of the list as a string
            letter = f[0] # find the first character of the package name
           
            print "Uploading %s to bintray" % (
                f)
            
            headers = {
                "X-Bintray-Package": package,
                "X-Bintray-Debian-Distribution": release,
                "X-Bintray-Debian-Architecture": arch,
                "X-Bintray-Publish": "1",
                "X-Bintray-Override": "1"
            }
            url = "https://api.bintray.com/content/{user}/deb/pool/main/{letter}/{package}/{f}".format ( 
                user=USERNAME, letter=letter, package=package, f=f)
            
            with open(filedir, "rb") as package_fp:
                response= requests.put(
                    url, auth=(USERNAME, API_KEY), headers=headers, data=package_fp)

            if response.status_code != 201:
                   "Failed to submit package: {0}\n{1}".format(
                       response.status_code, response.text)

            print("Submitted successfully.")
