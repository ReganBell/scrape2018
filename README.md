## Before you do any scraping
1. Install [scrapy](http://scrapy.org/)

## Update my.harvard Scrape:

1. Open a terminal, `cd` into `FullOnScrapyst`
2. Run `python -B scrapeMyHarvard.py`

## Update Q Scrape: 

1. Visit `https://webapps.fas.harvard.edu/course_evaluation_reports/fas/list` and authenticate as needed.
2. Open Chrome Dev Tools `command-alt-j`.
3. Go to Network, click on any request, and go to Headers > Request Headers.
4. Copy the value labelled `Cookie`, we'll call that `cookieString`. It should look something like:
`"ajs_anonymous_id=%22f5f00078-52ed-47d5-b357-be978f99143c%22; ajs_user_id=null; ajs_group_id=null; _hp2_id.1532377119=4082495396395081.3402744559.3738768864; faspincookietest=1; _gacd=GA1.2.2592617635.1459108765; SS_MID=e1e2036c-02e0-4a82-beb4-b034dee0804cinp7wj85; visid_incap_881684=R0tVqNSqRUuXLA/3cmCOSztCnlcAAAAAQUIPAAAAAACzMQ4fF7p2a7r2pCZsbFQ8; __unam=500f178-15702260b4c-7817c66f-21; _ga=GA1.2.1475525715.1445201989; JSESSIONID=D489C7C9308D89F56D32993256914D4E"`
5. Open a terminal, `cd` into `FullOnScrapyst`.
6. Edit the terms and years you'd like to scrape at the top of `FullOnScrapyst/spiders/QSpiders.py`
7. Run `python -B scrapeTheQ.py "cookieString"`

## Get Past Data

1. Download and unzip [this](https://www.dropbox.com/s/l8fslg6sefv4m7n/Data.zip?dl=0).
2. You should have a folder `Data`. Drop that into `FullOnScrapyst`.

## Parse and Merge into Database

1. Open a terminal, `cd` into `FullOnScrapyst`.
2. If you want to update everything and call that version 7 (for example), run `python -B createDatabase.py -a -v 7`
3. To update specific data:

| Flag        | Updates...           |
| ------------- |-------------| 
| `-a`      | Everything | 
| `-q`      | Q Data | 
| `-c`      | Course Data | 
| `-f`      | Faculty | 
| `-p`      | Percentiles | 
| `-pc`      | Past courses | 
| `-na`      | Nothing on Algolia | 
| `-nf`      | Nothing on Firebase | 