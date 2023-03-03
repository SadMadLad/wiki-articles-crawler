# frozen_string_literal: true

require 'nokogiri'
require 'open-uri'
require 'json'
require 'byebug'

# Helper methods for Scraping
module ScrapingTools
  def links(doc)
    doc.xpath('//a').map { |a| a.attr 'href' }
  end

  def internal_links(links)
    links.select { |link| link&.start_with? '/wiki/' }.map { |link| "https://www.wikipedia.org#{link}" }
  end

  def merge_lists(links_one, links_two)
    (links_one + links_two).uniq
  end

  def references(doc)
    puts 'Fetching references'
    doc.css('.reflist a').map { |a| a.attr 'href' }.select { |link| link.start_with? 'http' }
  end

  def make_new_article(doc, url)
    title = doc.css('title').text
    references = references(doc)

    WikiArticle.new(title, url, references)
  end
end

# The Mega Scraper
class WikiScraper
  include ScrapingTools

  attr_reader :starting_url, :articles_scrapped, :titles, :to_visit, :visited

  MAX_ARTICLES = 10

  def initialize(starting_url)
    @articles_scrapped = 0

    @titles = []
    @to_visit = [starting_url]
    @visited = []
  end

  def scrape
    while !@to_visit.empty? && @articles_scrapped < MAX_ARTICLES
      url = @to_visit.sample
      @visited.push url

      puts "Visiting #{url}"

      @current_article = Nokogiri::HTML URI.parse(url).open
      article = make_new_article(@current_article, url)
      article.save

      manage_links

      @articles_scrapped += 1
    end
  end

  private

    def manage_links
      new_internal_links = internal_links(links @current_article) - @visited
      @to_visit = (@to_visit + new_internal_links).uniq
    end
end

# To save scraped info
class WikiArticle
  ARTICLES_PATH = './articles'

  def initialize(title, url, references)
    @title = title
    @url = url
    @references = references
  end

  def save
    puts 'Saving article...'
    File.open("#{ARTICLES_PATH}/#{@title}.json","w") do |f|
      f.write(JSON.pretty_generate(to_hash))
    end
    puts "Article saved!\n\n"
  end

  private
    def to_hash
      puts 'Making a Hash'
      {
        'title' => @title,
        'url' => @url,
        'references' => @references
      }
    end
end

wikiscraper = WikiScraper.new('https://en.wikipedia.org/wiki/Kevin_Bacon')
wikiscraper.scrape
