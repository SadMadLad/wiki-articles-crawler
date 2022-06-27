import requests
from requests.exceptions import ConnectionError
from requests.exceptions import Timeout
from requests.exceptions import TooManyRedirects
from requests.exceptions import RequestException
from requests.exceptions import HTTPError as HTTPErrorRequests

from bs4 import BeautifulSoup

import re

import random
import os
import argparse

class WikiScrapper():
    def __init__(self, url, parser='html.parser'):
        self.url = url
        self.html = self.__simpleConnector()
        self.soup = BeautifulSoup(self.html, parser)
        
        self.embedded_links = self.__bodyLinks()
        self.reference_links = self.__referenceLinks()
        self.body_content = self.__bodyContent()
        self.article_tags = self.__articleTags()
                
    def __simpleConnector(self):
        '''Uses requests library, without any webdriver from selenium'''
        try:
            html = requests.get(self.url)
            html.raise_for_status()
        except HTTPErrorRequests as e:
            print('HTTP ERROR')
            print(e)
            return None
        except ConnectionError as e:
            print('CONNECTION ERROR')
            print(e)
            return None
        except Timeout as e:
            print('TIMEOUT')
            print(e)
            return None
        except TooManyRedirects as e:
            print('BAD URL: TOO MANY REDIRECTS')
            print(e)
            return None
        except RequestException as e:
            raise SystemExit(e)
        else:
            print('URL Connected')
            return html.text
    
    def __bodyLinks(self):
        '''All the links in the reading of the Wikipedia Page'''
        def linkTester(tag):
            '''Returns True if the link is valid (has no colon and takes to other pages), else False'''
            regex_wiki = '(\/wiki\/).*'
            regex_wiki_bool = bool(re.search(regex_wiki, tag))
            regex_category_bool = not(':' in tag)
            return (regex_wiki_bool and regex_category_bool)
        
        def convertLinks(all_links):
            '''Adds 'https://en.wikipedia.org/' in start of links.'''
            temp_list = []
            for link in all_links:
                temp_list.append('https://en.wikipedia.org/' + link['href'])
            
            return temp_list
        
        try:
            bodyContent = self.soup.find('div', {'id': 'bodyContent'}) 
            links = bodyContent.find_all('a', href=lambda tag: tag and linkTester(tag))
            links = convertLinks(links)
            print('Links Extracted Successfully')
            return links
        except AttributeError as e:
            print(e)
            return
            
    def __referenceLinks(self):
        '''Links to external articles in the references'''
        def convertLinks(all_links):
            temp_list = []
            for link in all_links:
                temp_list.append(link['href'])
            
            return temp_list
        try:
            links_r = self.soup.find_all('a', {'class': 'external text'})
            links_r = convertLinks(links_r)
            
            return links_r
        except AttributeError as e:
            print(e)
            return
    
    def __bodyContent(self):
        '''The main article content'''
        try:
            bodyContent = self.soup.find('div', {'id': 'bodyContent'})
            print('Body Content Extracted Successfully')
            return bodyContent
        except AttributeError as e:
            print(e)
            return
        
    def __articleTags(self):
        '''Extracting out tags within the article.'''
        
        try:
            '''tagsToExtract = ['h2', 'h3', 'p', 'ul', 'ol']'''
            mwContent = self.body_content.find('div', {'class': 'mw-parser-output'})
            supTags = mwContent.find_all('sup')
            
            '''Removing <sup> tags, (they look like [3], [5] etc.)'''
            for supTag in supTags:
                supTag.decompose()
                
            noAttributeTags = mwContent.find_all(lambda tag: not tag.attrs, recursive=False)
            print('Plain Article Tags extracted successfully from the article.')
            return noAttributeTags
        
        except AttributeError as e:
            print(e)
            return
    
    def getBodyLinks(self):
        return self.embedded_links
    def getReferenceLinks(self):
        return self.reference_links
    def getArticleTexts(self):
        headings = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']
        
        texts_list = []
        headings_list = []
        
        for tag in self.article_tags:
            if tag.name in headings:
                edit_button = tag.find('span', {'class': 'mw-editsection'})
                if edit_button:
                    edit_button.decompose()
                headings_list.append(tag.text)
            else:
                texts_list.append(tag.text)
        return headings_list, texts_list

class LoopScraper():
    def __init__(self, starter_url):
        self.starter_url = starter_url
        self.visited_links = []
        self.to_visit_links = {self.starter_url}
        self.total_content_dictionary = {}
        
    def dictionaryItem(self, bodyText, headingsText, externalLinks, bodyLinks):
        diction = {
            'bodyText': bodyText,
            'headingsText': headingsText,
            'externalLinks': externalLinks,
            'bodyLinks': bodyLinks
        }
        
        return diction
    
    def start(self, epochs=5):
        counter = 0
        while counter < epochs or len(self.to_visit_links) == 0:
            url_to_visit = random.choices([*self.to_visit_links])
            url_to_visit = url_to_visit[0]
            print('Visiting Link: ', url_to_visit, counter)
            self.visited_links.append(url_to_visit)
            self.to_visit_links.remove(url_to_visit)
            
            wikiObj = WikiScrapper(url_to_visit)
            headingsText, bodyText = wikiObj.getArticleTexts()
            externalLinks = wikiObj.getReferenceLinks()
            bodyLinks = wikiObj.getBodyLinks()
            
            self.to_visit_links.update(bodyLinks)
            
            headingsText = '\n'.join(headingsText)
            bodyText = ''.join(bodyText)
            externalLinks = '\n'.join(externalLinks)
            bodyLinks = '\n'.join(bodyLinks)

            wikiObjDiction = self.dictionaryItem(bodyText, headingsText, externalLinks, bodyLinks)
            self.total_content_dictionary[url_to_visit] = wikiObjDiction
            
            counter = counter + 1
            
    def getContentDictionary(self):
        return self.total_content_dictionary
    def getVisitedLinks(self):
        return self.visited_links
    def getRemainingLinks(self):
        return self.to_visit_links
    
    def exportAsFiles(self):
        def writeArticle(diction, directory, articleLink):
            if not os.path.isdir(directory):
                os.makedirs(directory)
                
            encoding = 'utf-8'
            
            f_articleLink = open(directory + 'articleLink.txt', "w", encoding=encoding)
            f_bodyText = open(directory + 'bodyText.txt', "w", encoding=encoding)
            f_headingsText = open(directory + 'headingsText.txt', "w", encoding=encoding)
            f_externalLinks = open(directory + 'externalLinks.txt', "w", encoding=encoding)
            f_bodyLinks = open(directory + 'bodyLinks.txt', "w", encoding=encoding)
            
            f_articleLink.write(articleLink)
            f_bodyText.write(diction['bodyText'])
            f_headingsText.write(diction['headingsText'])
            f_externalLinks.write(diction['externalLinks'])
            f_bodyLinks.write(diction['bodyLinks'])
            
            f_articleLink.close()
            f_bodyText.close()
            f_headingsText.close()
            f_externalLinks.close()
            f_bodyLinks.close()
            
        baseDirectory = './Article/'
        for index ,(key, value) in enumerate(self.total_content_dictionary.items()):
            writeArticle(value, baseDirectory + str(index) + '/', key)



def main():
    parser = argparse.ArgumentParser("wikiScrapper")
    parser.add_argument("article_link", help="A URL of the Wikipedia Article as from which the extraction will start.", type=str)
    parser.add_argument("epochs", help="For how long should the crawling go on.", type=int)

    args = parser.parse_args()
    
    print('Arguments: \nStarter Article Link: ', args.article_link, '\nNumber of articles that will be extracted: ', args.epochs)
    print('\nExtraction has started!\n')

    scraper = LoopScraper(args.article_link)
    scraper.start(epochs=args.epochs)
    scraper.exportAsFiles()

    print('The extraction has been done. Check the Articles folder for all the articles.')
    
main()