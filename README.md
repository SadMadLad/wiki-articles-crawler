# wiki-articles-crawler
A python script that will crawl through Wikipedia articles and extract out embedded links, external links, content and headings from the articles.

## Requirements
- Python
And following libraries are required
- requests
- BeautifulSoup
- os
- random
- re
- argparse <br>
Most of the above mentioned libraries are in-built in python.

## Usage
The `wikiScrapper.py` script takes two arguments: Starting Article URL and Epochs (how many articles to extract starting from the starter URL).
For more help, type `python wikiScrapper.py -h` for more help regarding arguments.

## Output
Once the extraction/crawling has been done, the data of articles will be stored in `Articles` folder, with a following structure:
`
Articles/
   0/
    articleLink.txt
    bodyLinks.txt
    bodyText.txt
    externalLinks.txt
    headingsText.txt
   1/
    articleLink.txt
    bodyLinks.txt
    .....
    ...
`
