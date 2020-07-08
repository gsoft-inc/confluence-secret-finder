# confluence-secret-finder

Script to search Confluence Cloud for secrets.

## Setup
Textract depencencies:
```
apt-get install python-dev libxml2-dev libxslt1-dev antiword unrtf poppler-utils pstotext swig
```

Other python dependencies:
```
pip3 install -r requirements.txt
```

## Usage
```
usage: main.py [-h] --domain DOMAIN --user USER --token TOKEN [--max-attachment-size MAX_ATTACHMENT_SIZE] [--blacklist BLACKLIST_FILE] [-v] [-vv] [--json]

Confluence Secret Finder

optional arguments:
  -h, --help            show this help message and exit
  --domain DOMAIN, -d DOMAIN
                        Confluence domain.
  --user USER, -u USER  Confluence user.
  --token TOKEN, -t TOKEN
                        API token for the user.
  --max-attachment-size MAX_ATTACHMENT_SIZE, -s MAX_ATTACHMENT_SIZE
                        Max attachment size to download in MB. Defaults to 10MB.
  --blacklist BLACKLIST_FILE, -b BLACKLIST_FILE
                        File containing regexes to blacklist secrets.
  -v                    Increases output verbosity.
  -vv                   Increases output verbosity even more.
  --json, -j            Outputs the results as json.

```
