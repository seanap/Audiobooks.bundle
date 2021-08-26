# Audiobooks (Audible)
# coding: utf-8
import json
import Queue
import re
import types
# Import internal tools
from logging import Logging
from urls import SiteUrl

VERSION_NO = '2021.08.25.1'

# Delay used when requesting HTML,
# may be good to have to prevent being banned from the site
REQUEST_DELAY = 10

# Starting value for score before deductions are taken.
INITIAL_SCORE = 100
# Score required to short-circuit matching and stop searching.
GOOD_SCORE = 98
# Any score lower than this will be ignored.
IGNORE_SCORE = 45

THREAD_MAX = 20

# Setup logger
log = Logging()


def Start():
    # HTTP.ClearCache()
    HTTP.CacheTime = CACHE_1WEEK
    HTTP.Headers['User-agent'] = (
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.2; Trident/4.0;'
        'SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729;'
        'Media Center PC 6.0'
    )
    HTTP.Headers['Accept-Encoding'] = 'gzip'
    log.separator(
        msg=(
            " - " + "Audible Audiobooks Agent v" + VERSION_NO
        ),
        log_level="info"
    )


class AudiobookArtist(Agent.Artist):
    name = 'Audiobooks'
    languages = [Locale.Language.English, 'de', 'fr', 'it']
    primary_provider = True
    accepts_from = ['com.plexapp.agents.localmedia']

    prev_search_provider = 0

    def getDateFromString(self, string):
        try:
            return Datetime.ParseDate(string).date()
        except AttributeError:
            return None

    def getStringContentFromXPath(self, source, query):
        return source.xpath('string(' + query + ')')

    def getAnchorUrlFromXPath(self, source, query):
        anchor = source.xpath(query)

        if len(anchor) == 0:
            return None

        return anchor[0].get('href')

    def getImageUrlFromXPath(self, source, query):
        img = source.xpath(query)

        if len(img) == 0:
            return None

        return img[0].get('src')

    def findDateInTitle(self, title):
        result = re.search(r'(\d+-\d+-\d+)', title)
        if result is not None:
            return Datetime.ParseDate(result.group(0)).date()
        return None

    def doSearch(self, url, ctx):

        html = HTML.ElementFromURL(url, sleep=REQUEST_DELAY)

        found = []

        for r in html.xpath('//div[a/img[@class="yborder"]]'):
            date = self.getDateFromString(
                self.getStringContentFromXPath(r, 'text()[1]')
            )
            title = self.getStringContentFromXPath(r, 'a[2]')
            murl = self.getAnchorUrlFromXPath(r, 'a[2]')
            thumb = self.getImageUrlFromXPath(r, 'a/img')

            found.append(
                {'url': murl, 'title': title, 'date': date, 'thumb': thumb}
            )

        return found

    def search(self, results, media, lang, manual=False):
        # Author data is pulling from last.fm automatically.
        # This will probably never be built out unless a good
        # author source is identified.

        # Log some stuff
        log.separator(msg='ARTIST SEARCH', log_level='debug')
        log.debug(
            '* Album:           %s', media.album
        )
        log.debug(
            '* Artist:           %s', media.artist
        )
        log.debug(
            '****************************************'
            'Not Ready For Artist Search Yet'
            '****************************************'
        )
        log.separator(log_level='debug')

    def hasProxy(self):
        return Prefs['imageproxyurl'] is not None

    def makeProxyUrl(self, url, referer):
        return Prefs['imageproxyurl'] + ('?url=%s&referer=%s' % (url, referer))

    def worker(self, queue, stoprequest):
        while not stoprequest.isSet():
            try:
                func, args, kargs = queue.get(True, 0.05)
                try:
                    func(*args, **kargs)
                except Exception as e:
                    log.info(e)
                queue.task_done()
            except Queue.Empty:
                continue

    def addTask(self, queue, func, *args, **kargs):
        queue.put((func, args, kargs))


class AudiobookAlbum(Agent.Album):
    name = 'Audiobooks'
    languages = [
        Locale.Language.English,
        'de',
        'fr',
        'it'
    ]
    primary_provider = True
    accepts_from = ['com.plexapp.agents.localmedia']

    prev_search_provider = 0

    def getDateFromString(self, string):
        try:
            return Datetime.ParseDate(string).date()
        except AttributeError:
            return None

    def getStringContentFromXPath(self, source, query):
        return source.xpath('string(' + query + ')')

    def getAnchorUrlFromXPath(self, source, query):
        anchor = source.xpath(query)

        if len(anchor) == 0:
            return None

        return anchor[0].get('href')

    def getImageUrlFromXPath(self, source, query):
        img = source.xpath(query)

        if len(img) == 0:
            return None

        return img[0].get('src')

    def findDateInTitle(self, title):
        result = re.search(r'(\d+-\d+-\d+)', title)
        if result is not None:
            return Datetime.ParseDate(result.group(0)).date()
        return None

    def before_xpath(self):
        for r in self.html.xpath(
            '//ul//li[contains(@class,"productListItem")]'
        ):
            datetext = self.getStringContentFromXPath(
                r, (
                    u'div/div/div/div/div/div/span/ul/li'
                    '[contains (@class,"releaseDateLabel")]/span'
                    )
            )
            datetext = re.sub(r'[^0-9\-]', '', datetext)
            date = self.getDateFromString(datetext)
            title = self.getStringContentFromXPath(
                r, (
                    'div/div/div/div/div/div/span/ul//a'
                    '[contains (@class,"bc-link")][1]'
                    )
            )
            murl = self.getAnchorUrlFromXPath(
                r, 'div/div/div/div/div/div/span/ul/li/h3//a[1]'
            )
            thumb = self.getImageUrlFromXPath(
                r, 'div/div/div/div/div/div/div'
                '[contains(@class,"responsive-product-square")]/div/a/img'
            )
            author = self.getStringContentFromXPath(
                r, (
                    'div/div/div/div/div/div/span/ul'
                    '/li[contains (@class,"authorLabel")]/span/a[1]'
                )
            )
            narrator = self.getStringContentFromXPath(
                r, (
                    u'div/div/div/div/div/div/span/ul/li'
                    '[contains (@class,"narratorLabel")]/span//a[1]'
                ).format(self.ctx['NAR_BY'])
            )
            log.separator(msg='XPATH SEARCH HIT', log_level="debug")

            self.found.append(
                {
                    'url': murl,
                    'title': title,
                    'date': date,
                    'thumb': thumb,
                    'author': author,
                    'narrator': narrator
                }
            )

    def after_xpath(self):
        for r in self.html.xpath(
            '//div[contains (@class, "adbl-search-result")]'
        ):
            date = self.getDateFromString(
                self.getStringContentFromXPath(
                    r, (
                        u'div/div/ul/li[contains (., "{0}")]'
                        '/span[2]//text()'
                        ).format(
                        self.ctx['REL_DATE']
                    )
                )
            )
            title = self.getStringContentFromXPath(
                r, 'div/div/div/div/a[1]'
            )
            murl = self.getAnchorUrlFromXPath(
                r, 'div/div/div/div/a[1]'
            )
            thumb = self.getImageUrlFromXPath(
                r, 'div[contains (@class,"adbl-prod-image-sample-cont")]/a/img'
            )
            author = self.getStringContentFromXPath(
                r, (
                        'div/div/ul/li/'
                        '/a[contains (@class,"author-profile-link")][1]'
                    )
            )
            narrator = self.getStringContentFromXPath(
                r, u'div/div/ul/li[contains (., "{0}")]//a[1]'.format(
                    self.ctx['NAR_BY']
                )
            )
            log.separator(msg='XPATH SEARCH HIT', log_level="debug")

            self.found.append(
                {
                    'url': murl,
                    'title': title,
                    'date': date,
                    'thumb': thumb,
                    'author': author,
                    'narrator': narrator
                }
            )

    def doSearch(self, url, ctx):
        self.html = HTML.ElementFromURL(url, sleep=REQUEST_DELAY)
        self.found = []
        self.ctx = ctx

        log.separator(msg='just before new xpath line', log_level="debug")
        self.before_xpath()

        log.separator(msg='just after new xpath line', log_level="debug")
        self.after_xpath()

        return self.found

    def pre_search(self):
        log.separator(msg='ALBUM SEARCH', log_level="info")
        # Log basic metadata
        data_to_log = [
            {'ID': self.media.parent_metadata.id},
            {'Title': self.media.title},
            {'Name': self.media.name},
            {'Album': self.media.album},
            {'Artist': self.media.artist},
        ]
        log.metadata(data_to_log)
        log.separator(log_level="info")

        # Handle a couple of edge cases where
        # album search will give bad results.
        if self.media.album is None and not self.manual:
            log.info('Album Title is NULL on an automatic search.  Returning')
            return
        if self.media.album == '[Unknown Album]' and not self.manual:
            log.info(
                'Album Title is [Unknown Album]'
                ' on an automatic search.  Returning'
            )
            return

        if self.manual:
            log.separator(msg="NOTE", log_level="info")
            log.info(
                'You clicked \'fix match\'. '
                'This may have returned no useful results because '
                'it\'s searching using the title of the first track.'
            )
            log.info(
                'There\'s not currently a way around this initial failure. '
                'But clicking \'Search Options\' and '
                'entering the title works just fine.'
            )
            log.info(
                'This message will appear during the initial '
                'search and the actual manual search.'
            )
            # If this is a custom search,
            # use the user-entered name instead of the scanner hint.
            if self.media.name:
                log.info(
                    'Custom album search for: ' + self.media.name
                )
                self.media.album = self.media.name
        else:
            log.info('Album search: ' + self.media.title)

    def format_title(self):
        # Normalize the name
        self.normalizedName = String.StripDiacritics(
            self.media.album
        )
        if len(self.normalizedName) == 0:
            self.normalizedName = self.media.album
        log.debug(
            'normalizedName = %s', self.normalizedName
        )

        # Chop off "unabridged"
        self.normalizedName = re.sub(
            r"[\(\[].*?[\)\]]", "", self.normalizedName
        )
        log.debug(
            'chopping bracketed text = %s', self.normalizedName
        )
        self.normalizedName = self.normalizedName.strip()
        log.debug(
            'normalizedName stripped = %s', self.normalizedName
        )

        log.separator(
            msg=(
                "SEARCHING FOR " + '"' + self.normalizedName + '"'
            ),
            log_level="info"
        )

    def run_search(self):
        # Walk the found items and gather extended information
        info = []
        i = 1
        itemId_full = None
        itemId = None
        valid_itemId = None

        log.separator(msg="Search results", log_level="info")
        for i, f in enumerate(self.found):
            url = f['url']
            log.debug('URL For Breakdown: %s', url)

            # Get the id
            for item in url.split('/'):
                # IDs No longer start with just 'B0'
                if re.match(r'^[0-9A-Z]{10,10}', item):
                    itemId_full = item
                    break

            # New Search results contain question marks after the ID
            for itemId in itemId_full.split('?'):
                # IDs No longer start with just 'B0'
                if re.match(r'^[0-9A-Z]{10,10}', itemId):
                    valid_itemId = itemId
                    break

            if len(valid_itemId) == 0:
                log.info('No Match: %s', url)
                continue

            title = f['title']
            thumb = f['thumb']
            date = f['date']
            year = ''
            author = f['author']
            narrator = f['narrator']

            if date is not None:
                year = date.year

            # Score the album name
            scorebase1 = self.media.album
            scorebase2 = title.encode('utf-8')

            score = INITIAL_SCORE - Util.LevenshteinDistance(
                scorebase1, scorebase2
            )

            if self.media.artist:
                scorebase3 = self.media.artist
                scorebase4 = author
                score = INITIAL_SCORE - Util.LevenshteinDistance(
                    scorebase3, scorebase4
                )

            log.info(msg=("Result #" + i), log_level="info")
            # Log basic metadata
            data_to_log = [
                {'ID is': valid_itemId},
                {'Title is': title},
                {'Author is': author},
                {'Narrator is': narrator},
                {'Date is ': str(date)},
                {'Score is': str(score)},
                {'Thumb is': thumb},
            ]
            log.metadata(data_to_log, log_level="info")

            if score >= self.LCL_IGNORE_SCORE:
                info.append(
                    {
                        'id': valid_itemId,
                        'title': title,
                        'year': year,
                        'date': date,
                        'score': score,
                        'thumb': thumb,
                        'artist': author
                    }
                )
            else:
                log.info(
                    '# Score is below ignore boundary (%s)... Skipping!',
                    self.LCL_IGNORE_SCORE
                )

            # Print separators for easy reading
            if i <= len(self.found):
                log.separator(log_level="info")

        info = sorted(info, key=lambda inf: inf['score'], reverse=True)
        return info

    def search(self, results, media, lang, manual):
        url_info = SiteUrl(Prefs['sitetype'], Prefs['site'], lang)
        self.ctx = url_info.SetupUrls()
        self.LCL_IGNORE_SCORE = IGNORE_SCORE
        self.results = results
        self.media = media
        self.lang = lang
        self.manual = manual

        self.pre_search()

        self.format_title()

        # Make the URL
        if self.media.artist is not None:
            searchUrl = self.ctx['AUD_SEARCH_URL'].format(
                (
                    String.Quote((self.normalizedName).encode('utf-8'), usePlus=True)
                ),
                (
                    String.Quote((self.media.artist).encode('utf-8'), usePlus=True)
                )
            )
        else:
            searchUrl = self.ctx['AUD_KEYWORD_SEARCH_URL'] % (
                String.Quote((self.normalizedName).encode('utf-8'), usePlus=True)
            )
        self.result = self.doSearch(searchUrl, self.ctx)

        # Write search result status to log
        if len(self.result) == 0:
            log.info(
                'No results found for query "%s"',
                self.normalizedName
            )
            return

        log.debug(
            'Found %s result(s) for query "%s"',
            len(self.result),
            self.normalizedName
        )

        info = self.run_search()

        # Output the final results.
        log.separator(log_level="debug")
        log.debug('Final result:')
        i = 1
        for r in info:
            description = '\"%s\" by %s [%s]' % (
                r['title'], r['artist'], r['year']
            )
            log.debug(
                '    [%s]    %s. %s (%s) %s {%s} [%s]',
                r['score'], i, r['title'], r['year'],
                r['artist'], r['id'], r['thumb']
            )
            results.Append(
                MetadataSearchResult(
                    id=r['id'],
                    name=description,
                    score=r['score'],
                    thumb=r['thumb'],
                    lang=lang
                )
            )

            # If there are more than one result,
            # and this one has a score that is >= GOOD SCORE,
            # then ignore the rest of the results
            if not manual and len(info) > 1 and r['score'] >= GOOD_SCORE:
                log.info(
                    '            *** The score for these results are great, '
                    'so we will use them, and ignore the rest. ***'
                )
                break
            i += 1

    def use_copyright_date(self):
        cstring = None

        for r in self.html.xpath(u'//span[contains(text(), "\xA9")]'):
            cstring = self.getStringContentFromXPath(
                r, u'normalize-space(//span[contains(text(), "\xA9")])'
            )
            # only contains Audible copyright
            if cstring.startswith(u"\xA9 "):
                cstring = ""
                date = date[:4]

        if cstring:
            if "Public Domain" in cstring:
                date = re.match(".*\(P\)(\d{4})", cstring).group(1)
            else:
                if cstring.startswith(u'\xA9'):
                    cstring = cstring[1:]
                if "(P)" in cstring:
                    cstring = re.match("(.*)\(P\).*", cstring).group(1)
                if ";" in cstring:
                    date = str(
                        min(
                            [int(i) for i in cstring.split() if i.isdigit()]
                        )
                    )
                else:
                    date = re.match(".?(\d{4}).*", cstring).group(1)

    def update_scrape(self):
        for r in self.html.xpath('//div[contains (@id, "adbl_page_content")]'):
            self.date = self.getDateFromString(
                self.getStringContentFromXPath(
                    r, u'//li[contains (., "{0}")]/span[2]//text()'.format(
                        self.ctx['REL_DATE_INFO']
                    )
                )
            )
            self.title = self.getStringContentFromXPath(
                r, '//h1[contains (@class, "adbl-prod-h1-title")]/text()'
            )
            self.murl = self.getAnchorUrlFromXPath(
                r, 'div/div/div/div/a[1]'
            )
            self.thumb = self.getImageUrlFromXPath(
                r, 'div/div/div/div/div/img'
            )
            self.author = self.getStringContentFromXPath(
                r, '//li//a[contains (@class,"author-profile-link")][1]'
            )
            self.narrator = self.getStringContentFromXPath(
                r, '//li[contains (., "{0}")]//span[2]'.format(
                    self.ctx['NAR_BY_INFO']
                )
            ).strip().decode('utf-8')
            self.studio = self.getStringContentFromXPath(
                r, '//li//a[contains (@id,"PublisherSearchLink")][1]'
            )
            self.synopsis = self.getStringContentFromXPath(
                r, '//div[contains (@class, "disc-summary")]/div[*]'
            ).strip()
            self.series = self.getStringContentFromXPath(
                r, '//div[contains (@class, "adbl-series-link")]//a[1]'
            )
            self.genre_parent = self.getStringContentFromXPath(
                r, (
                    '//div[contains(@class,"adbl-pd-breadcrumb")]'
                    '/div[2]/a/span/text()'
                )
            )
            self.genre_child = self.getStringContentFromXPath(
                r, (
                    '//div[contains(@class,"adbl-pd-breadcrumb")]'
                    '/div[3]/a/span/text()'
                )
            )
            log.separator(msg='XPATH SEARCH HIT', log_level="debug")

    def date_missing(self):
        for r in self.html.xpath(
            '//script[contains (@type, "application/ld+json")]'
        ):
            page_content = r.text_content()
            page_content = page_content.replace('\n', '')
            # Remove any backslashes that aren't
            # escaping a character JSON needs escaped
            remove_inv_json_esc = re.compile(
                r'([^\\])(\\(?![bfnrt\'\"\\/]|u[A-Fa-f0-9]{4}))'
            )
            page_content = remove_inv_json_esc.sub(r'\1\\\2', page_content)
            log.debug(page_content)
            json_data = json_decode(page_content)
            for json_data in json_data:
                if 'datePublished' in json_data:
                    self.date = json_data['datePublished']
                    self.title = json_data['name']
                    self.thumb = json_data['image']
                    # Set rating when available
                    if 'aggregateRating' in json_data:
                        self.rating = (
                            json_data['aggregateRating']['ratingValue']
                        )
                    author_array = []
                    for c in json_data['author']:
                        author_array.append(c['name'])
                    self.author = ",".join(author_array)

                    narrator_array = []
                    for c in json_data['readBy']:
                        narrator_array.append(c['name'])
                    self.narrator = ",".join(narrator_array)
                    self.studio = json_data['publisher']
                    self.synopsis = json_data['description']
                if 'itemListElement' in json_data:
                    self.genre_parent = (
                        json_data['itemListElement'][1]['item']['name']
                    )
                    try:
                        self.genre_child = (
                            json_data['itemListElement'][2]['item']['name']
                        )
                    except AttributeError:
                        continue

    def handle_series(self):
        for r in self.html.xpath('//span[contains(@class, "seriesLabel")]'):
            self.series = self.getStringContentFromXPath(
                r, '//li[contains(@class, "seriesLabel")]//a[1]'
            )
            self.series2 = self.getStringContentFromXPath(
                r, '//li[contains(@class, "seriesLabel")]//a[2]'
            )

            self.series_def = self.series2 if self.series2 else self.series

            self.volume = self.getStringContentFromXPath(
                r, '//li[contains(@class, "seriesLabel")]/text()[2]'
            ).strip()
            if self.volume == ",":
                self.volume = ""
            self.volume2 = self.getStringContentFromXPath(
                r, '//li[contains(@class, "seriesLabel")]/text()[3]'
            ).strip()
            if self.volume2 == ",":
                self.volume2 = ""

            self.volume_def = self.volume2 if self.volume2 else self.volume

        # fix series when audible 'forgets' the series link…
        if not self.series_def:
            for r in self.html.xpath('//div[contains(@class, "adbl-main")]'):
                self.subtitle = self.getStringContentFromXPath(
                    r, 'normalize-space(//li[contains'
                    '(@class, "authorLabel")]'
                    '//preceding::li[1]//span//text())'
                ).strip()

            w = re.match("(.*)(, Book \d+)", self.subtitle)
            if not self.series_def and w:
                self.series_def = w.group(1)
                self.volume_def = w.group(2)

    def parse_author_narrator(self):
        # Add Narrators to Styles
        narrators_list = self.narrator.split(",")
        narr_contributors_list = [
            'full cast'
        ]
        self.metadata.styles.clear()
        # Loop through narrators to check if it has contributor wording
        for narrator in narrators_list:
            if not [
                contrib for contrib in narr_contributors_list if (
                    contrib in narrator.lower()
                )
            ]:
                self.metadata.styles.add(narrator.strip())

        # Add Authors to Moods
        author_list = self.author.split(",")
        author_contributers_list = [
            'contributor',
            'translator',
            'foreword',
            'translated',
            'full cast',
        ]
        self.metadata.moods.clear()
        # Loop through authors to check if it has contributor wording
        for author in author_list:
            if not [
                contrib for contrib in author_contributers_list if (
                    contrib in author.lower()
                )
            ]:
                self.metadata.moods.add(author.strip())

    def parse_series(self):
        # Clean series
        x = re.match("(.*)(: A .* Series)", self.series_def)
        if x:
            self.series_def = x.group(1)

        # Clean title
        seriesshort = self.series_def
        checkseries = " Series"
        # Handle edge cases in titles
        if self.series_def.endswith(checkseries):
            seriesshort = self.series_def[:-len(checkseries)]

            y = re.match(
                "(.*)((: .* " + self.volume_def[2:] + ": A .* Series)|"
                "(((:|,|-) )((" + seriesshort + self.volume_def + ")|"
                "((?<!" + seriesshort + ", )(" + self.volume_def[2:] + "))|"
                "((The .*|Special) Edition)|"
                "((?<!" + self.volume_def[2:] + ": )An? .* "
                "(Adventure|Novella|Series|Saga))|"
                "(A Novel of the .*))|"
                "( \(" + seriesshort + ", Book \d+; .*\))))$",
                self.title
            )

            if y:
                self.title = y.group(1)

    def compile_metadata(self):
        # Set the date and year if found.
        if self.date is not None:
            self.metadata.originally_available_at = self.date

        # Add the genres
        self.metadata.genres.clear()
        self.metadata.genres.add(self.genre_parent)
        self.metadata.genres.add(self.genre_child)

        self.parse_author_narrator()

        self.parse_series()

        # Other metadata
        self.metadata.title = self.title
        self.metadata.title_sort = ' - '.join(
            filter(None, [(self.series_def + self.volume_def), self.title])
        )
        self.metadata.studio = self.studio
        self.metadata.summary = self.synopsis
        self.metadata.posters[1] = Proxy.Media(HTTP.Request(self.thumb))
        self.metadata.posters.validate_keys(self.thumb)
        # Use rating only when available
        if self.rating:
            self.metadata.rating = float(self.rating) * 2

        # Collections if/when Plex supports them
        # https://github.com/seanap/Audiobooks.bundle/issues/1#issuecomment-713191070
        self.metadata.collections.clear()
        self.metadata.collections.add(self.series)
        if self.series2:
            self.metadata.collections.add(self.series2)
        self.writeInfo()

    def update(self, metadata, media, lang, force=False):
        url_info = SiteUrl(Prefs['sitetype'], Prefs['site'], lang)
        self.ctx = url_info.SetupUrls()
        self.metadata = metadata
        self.media = media
        self.lang = lang
        log.separator(
            msg=(
                "UPDATING" + ' "' + self.media.title + '" ' + (
                    "ID: " + self.metadata.id
                )
            ),
            log_level="info"
        )

        # Make url
        self.url = self.ctx['AUD_BOOK_INFO'] % self.metadata.id

        try:
            self.html = HTML.ElementFromURL(self.url, sleep=REQUEST_DELAY)
        except Exception as e:
            log.info(e)

        self.date = None
        self.rating = None
        self.series = ''
        self.series2 = ''
        self.series_def = ''
        self.genre_parent = None
        self.genre_child = None
        self.volume = ''
        self.volume2 = ''
        self.volume_def = ''

        self.update_scrape()

        if self.date is None:
            self.date_missing()

            # prefer copyright year over datePublished
            if Prefs['copyyear']:
                self.use_copyright_date()

            self.date = self.getDateFromString(self.date)

            self.handle_series()

        # cleanup synopsis
        self.synopsis = (
            self.synopsis.replace("<i>", "")
            .replace("</i>", "")
            .replace("<em>", "")
            .replace("</em>", "")
            .replace("<u>", "")
            .replace("</u>", "")
            .replace("<b>", "")
            .replace("</b>", "")
            .replace("<strong>", "")
            .replace("</strong>", "")
            .replace("<ul>", "")
            .replace("</ul>", "\n")
            .replace("<ol>", "")
            .replace("</ol>", "\n")
            .replace("<li>", " • ")
            .replace("</li>", "\n")
            .replace("<br />", "")
            .replace("<p>", "")
            .replace("</p>", "\n")
        )

        # Setup logging of all data in the array
        data_to_log = [
            {'date': self.date},
            {'title': self.title},
            {'author': self.author},
            {'series': self.series},
            {'narrator': self.narrator},
            {'studio': self.studio},
            {'thumb': self.thumb},
            {'rating': self.rating},
            {'genres': self.genre_parent + ', ' + self.genre_child},
            {'synopsis': self.synopsis},
            {'volume': self.volume},
            {'series2': self.series2},
            {'volume2': self.volume2},
            {'series def': self.series_def},
            {'volume def': self.volume_def},
        ]
        log.metadata(data_to_log, log_level="debug")

        self.compile_metadata()

    def hasProxy(self):
        return Prefs['imageproxyurl'] is not None

    def makeProxyUrl(self, url, referer):
        return Prefs['imageproxyurl'] + ('?url=%s&referer=%s' % (url, referer))

    def worker(self, queue, stoprequest):
        while not stoprequest.isSet():
            try:
                func, args, kargs = queue.get(True, 0.05)
                try:
                    func(*args, **kargs)
                except Exception as e:
                    log.info(e)
                queue.task_done()
            except Queue.Empty:
                continue

    def addTask(self, queue, func, *args, **kargs):
        queue.put((func, args, kargs))

    # Writes metadata information to log.
    def writeInfo(self):
        log.separator(msg='New data', log_level="info")

        # Log basic metadata
        data_to_log = [
            {'ID': self.metadata.id},
            {'URL': self.url},
            {'Title': self.metadata.title},
            {'Release date': str(self.metadata.originally_available_at)},
            {'Studio': self.metadata.studio},
            {'Summary': self.metadata.summary},
            {'Poster URL': self.thumb},
        ]
        log.metadata(data_to_log, log_level="info")

        # Log basic metadata stored in arrays
        multi_arr = [
            # {'Collection': self.metadata.collections},
            {'Genre': self.metadata.genres},
            {'Moods(Authors)': self.metadata.moods},
            {'Styles(Narrators)': self.metadata.styles},
            # {'Fan art URL': self.metadata.art},
        ]
        log.metadata_arrs(multi_arr, log_level="info")

        log.separator(log_level="info")


def json_decode(output):
    try:
        return json.loads(output, encoding="utf-8")
    except AttributeError:
        return None
