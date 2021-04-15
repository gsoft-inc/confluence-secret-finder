# confluence-secret-finder

Script to search Confluence Cloud for secrets.

## Setup
Textract depencencies (Ubuntu/Debian/Kali):
```
apt-get install python-dev libxml2-dev libxslt1-dev antiword unrtf poppler-utils swig
```

Textract depencencies (OSX):
```
See https://textract.readthedocs.io/en/stable/installation.html#osx
```

Tool
```
python setup.py install
```

## Usage
```
usage: confluence-secret-finder [-h] --domain DOMAIN --user USER --token TOKEN [--start-date START_DATE] [--max-attachment-size MAX_ATTACHMENT_SIZE] [--blacklist BLACKLIST_FILE] [--cache-location CACHE_LOCATION] [-v] [-vv]
               [--json]

Confluence Secret Finder

optional arguments:
  -h, --help            show this help message and exit
  --domain DOMAIN, -d DOMAIN
                        Confluence domain.
  --user USER, -u USER  Confluence user.
  --token TOKEN, -t TOKEN
                        API token for the user.
  --start-date START_DATE, -s START_DATE
                        Date (YYYY-MM-DD) from which to start the crawling. Otherwise, the script will default to the oldest content creation date or resume where it last stopped.
  --max-attachment-size MAX_ATTACHMENT_SIZE, -m MAX_ATTACHMENT_SIZE
                        Max attachment size to download in MB. Defaults to 10MB.
  --blacklist BLACKLIST_FILE, -b BLACKLIST_FILE
                        File containing regexes to blacklist secrets.
  --cache-location CACHE_LOCATION, -c CACHE_LOCATION
                        Specified where the cache sqlite file will be saved.
  -v                    Increases output verbosity.
  -vv                   Increases output verbosity even more.
  --json, -j            Outputs the results as json.
```

## License

Copyright © 2020, GSoft inc. This code is licensed under the Apache License, Version 2.0. You may obtain a copy of this license [here](https://github.com/gsoft-inc/gsoft-license/blob/master/LICENSE).
