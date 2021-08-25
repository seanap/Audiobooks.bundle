# Audiobooks (Audible)
# coding: utf-8
import json
import re
import types

import Queue


def json_decode(output):
    try:
        return json.loads(output, encoding="utf-8")
    except:
        return None


# URLs
VERSION_NO = '1.2021.08.24.1'

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

intl_sites = {
    'en': {
        'url': 'www.audible.com',
        'urltitle': u'title=',
        'rel_date': u'Release date',
        'nar_by': u'Narrated By',
        'nar_by2': u'Narrated by'
    },
    'fr': {
        'url': 'www.audible.fr',
        'urltitle': u'title=',
        'rel_date': u'Date de publication',
        'nar_by': u'Narrateur(s)',
        'nar_by2': u'Lu par'
    },
    'de': {
        'url': 'www.audible.de',
        'urltitle': u'title=',
        'rel_date': u'Erscheinungsdatum',
        'nar_by': u'Gesprochen von',
        'rel_date2': u'Veröffentlicht'
    },
    'it': {
        'url': 'www.audible.it',
        'urltitle': u'title=',
        'rel_date': u'Data di Pubblicazione',
        'nar_by': u'Narratore'
    },
}

sites_langs = {
    'www.audible.com': {'lang': 'en'},
    'www.audible.co.uk': {'lang': 'en'},
    'www.audible.com.au': {'lang': 'en'},
    'www.audible.fr': {'lang': 'fr'},
    'www.audible.de': {'lang': 'de'},
    'www.audible.it': {'lang': 'it'},
}


def SetupUrls(sitetype, base, lang='en'):
    Log('Library/Search language is : %s', lang)
    ctx = dict()
    if sitetype:
        Log('Manual Site Selection Enabled : %s', base)
        Log('Language being ignored due to manual site selection')
        if base in sites_langs:
            Log('Pulling language from sites array')
            lang = sites_langs[base]['lang']
            if lang in intl_sites:
                base = intl_sites[lang]['url']
                urlsearchtitle = intl_sites[lang]['urltitle']
                ctx['REL_DATE'] = intl_sites[lang]['rel_date']
                ctx['NAR_BY'] = intl_sites[lang]['nar_by']
                if 'rel_date2' in intl_sites[lang]:
                    ctx['REL_DATE_INFO'] = intl_sites[lang]['rel_date2']
                else:
                    ctx['REL_DATE_INFO'] = ctx['REL_DATE']
                if 'nar_by2' in intl_sites[lang]:
                    ctx['NAR_BY_INFO'] = intl_sites[lang]['nar_by2']
                else:
                    ctx['NAR_BY_INFO'] = ctx['NAR_BY']
            else:
                ctx['REL_DATE'] = 'Release date'
                ctx['REL_DATE_INFO'] = ctx['REL_DATE']
                ctx['NAR_BY'] = 'Narrated By'
                ctx['NAR_BY_INFO'] = 'Narrated by'
        Log(
            'Sites language is : %s', lang
            )
        Log(
            '/************************************'
            'LANG DEBUGGING'
            '************************************/'
            )
        Log(
            '/* REL_DATE = %s', ctx['REL_DATE']
            )
        Log(
            '/* REL_DATE_INFO = %s', ctx['REL_DATE_INFO']
            )
        Log(
            '/* NAR_BY = %s', ctx['NAR_BY']
            )
        Log(
            '/* NAR_BY_INFO = %s', ctx['NAR_BY_INFO']
            )
        Log(
            '/****************************************'
            '****************************************/'
            )
    else:
        Log(
            'Audible site will be chosen by library language'
            )
        Log(
            'Library Language is %s', lang
            )
        if base is None:
            base = 'www.audible.com'
        if lang in intl_sites:
            base = intl_sites[lang]['url']
            urlsearchtitle = intl_sites[lang]['urltitle']
            ctx['REL_DATE'] = intl_sites[lang]['rel_date']
            ctx['NAR_BY'] = intl_sites[lang]['nar_by']
            if 'rel_date2' in intl_sites[lang]:
                ctx['REL_DATE_INFO'] = intl_sites[lang]['rel_date2']
            else:
                ctx['REL_DATE_INFO'] = ctx['REL_DATE']
            if 'nar_by2' in intl_sites[lang]:
                ctx['NAR_BY_INFO'] = intl_sites[lang]['nar_by2']
            else:
                ctx['NAR_BY_INFO'] = ctx['NAR_BY']
        else:
            ctx['REL_DATE'] = 'Release date'
            ctx['REL_DATE_INFO'] = ctx['REL_DATE']
            ctx['NAR_BY'] = 'Narrated By'
            ctx['NAR_BY_INFO'] = 'Narrated by'

    AUD_BASE_URL = 'https://' + str(base) + '/'
    AUD_TITLE_URL = urlsearchtitle

    AUD_BOOK_INFO_ARR = [
        AUD_BASE_URL,
        'pd/%s?ipRedirectOverride=true',
    ]
    ctx['AUD_BOOK_INFO'] = ''.join(AUD_BOOK_INFO_ARR)

    AUD_ARTIST_SEARCH_URL_ARR = [
        AUD_BASE_URL,
        'search?searchAuthor=%s&ipRedirectOverride=true',
    ]
    ctx['AUD_ARTIST_SEARCH_URL'] = ''.join(AUD_ARTIST_SEARCH_URL_ARR)

    AUD_ALBUM_SEARCH_URL_ARR = [
        AUD_BASE_URL,
        'search?',
        AUD_TITLE_URL,
        '%s&x=41&ipRedirectOverride=true',
    ]
    ctx['AUD_ALBUM_SEARCH_URL'] = ''.join(AUD_ALBUM_SEARCH_URL_ARR)

    AUD_KEYWORD_SEARCH_URL_ARR = [
        AUD_BASE_URL,
        ('search?filterby=field-keywords&advsearchKeywords=%s'
            '&x=41&ipRedirectOverride=true'),
    ]
    ctx['AUD_KEYWORD_SEARCH_URL'] = ''.join(AUD_KEYWORD_SEARCH_URL_ARR)

    AUD_SEARCH_URL_ARR = [
        AUD_BASE_URL,
        'search?',
        AUD_TITLE_URL,
        '{0}&searchAuthor={1}&x=41&ipRedirectOverride=true',
    ]
    ctx['AUD_SEARCH_URL'] = ''.join(AUD_SEARCH_URL_ARR)

    return ctx


def Start():
    # HTTP.ClearCache()
    HTTP.CacheTime = CACHE_1WEEK
    HTTP.Headers['User-agent'] = (
        'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.2; Trident/4.0;'
        'SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729;'
        'Media Center PC 6.0'
    )
    HTTP.Headers['Accept-Encoding'] = 'gzip'


class AudiobookArtist(Agent.Artist):
    name = 'Audiobooks'
    languages = [Locale.Language.English, 'de', 'fr', 'it']
    primary_provider = True
    accepts_from = ['com.plexapp.agents.localmedia']

    prev_search_provider = 0

    def Log(self, message, *args):
        if Prefs['debug']:
            Log(message, *args)

    def getDateFromString(self, string):
        try:
            return Datetime.ParseDate(string).date()
        except:
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
        self.Log(
            '------------------------------------------------'
            'ARTIST SEARCH'
            '------------------------------------------------'
        )
        self.Log(
            '* Album:           %s', media.album
        )
        self.Log(
            '* Artist:           %s', media.artist
        )
        self.Log(
            '****************************************'
            'Not Ready For Artist Search Yet'
            '****************************************'
        )
        self.Log(
            '------------------------------------------------'
            '------------------------------------------------'
        )
        return

    def update(self, metadata, media, lang, force=False):
        return

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
                    self.Log(e)
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

    def Log(self, message, *args):
        if Prefs['debug']:
            Log(message, *args)

    def getDateFromString(self, string):
        try:
            return Datetime.ParseDate(string).date()
        except:
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
        self.Log(
            '-----------------------------------------'
            'just before new xpath line'
            '-----------------------------------------'
            )
        for r in html.xpath('//ul//li[contains(@class,"productListItem")]'):
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
                ).format(ctx['NAR_BY'])
            )
            self.Log(
                '-----------------------------------------------'
                'XPATH SEARCH HIT'
                '-----------------------------------------------'
            )

            found.append(
                {
                    'url': murl,
                    'title': title,
                    'date': date,
                    'thumb': thumb,
                    'author': author,
                    'narrator': narrator
                }
            )

        self.Log(
            '-----------------------------------------'
            'just after new xpath line'
            '-----------------------------------------'
            )

        for r in html.xpath('//div[contains (@class, "adbl-search-result")]'):
            date = self.getDateFromString(
                self.getStringContentFromXPath(
                    r, (
                        u'div/div/ul/li[contains (., "{0}")]'
                        '/span[2]//text()'
                        ).format(
                        ctx['REL_DATE']
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
                    ctx['NAR_BY']
                )
            )
            self.Log(
                '-----------------------------------------------'
                'XPATH SEARCH HIT'
                '-----------------------------------------------'
            )

            found.append(
                {
                    'url': murl,
                    'title': title,
                    'date': date,
                    'thumb': thumb,
                    'author': author,
                    'narrator': narrator
                }
            )

        return found

    def search(self, results, media, lang, manual):
        ctx = SetupUrls(Prefs['sitetype'], Prefs['site'], lang)
        LCL_IGNORE_SCORE = IGNORE_SCORE

        self.Log(
            '-----------------------------------------------'
            'ALBUM SEARCH'
            '-----------------------------------------------'
        )
        self.Log('* ID:              %s', media.parent_metadata.id)
        self.Log('* Title:           %s', media.title)
        self.Log('* Name:            %s', media.name)
        self.Log('* Album:           %s', media.album)
        self.Log('* Artist:          %s', media.artist)
        self.Log(
            '-------------------------------------------------'
            '-------------------------------------------------'
        )

        # Handle a couple of edge cases where
        # album search will give bad results.
        if media.album is None and not manual:
            self.Log('Album Title is NULL on an automatic search.  Returning')
            return
        if media.album == '[Unknown Album]' and not manual:
            self.Log(
                'Album Title is [Unknown Album]'
                ' on an automatic search.  Returning'
            )
            return

        if manual:
            Log(
                'You clicked \'fix match\'. '
                'This may have returned no useful results because '
                'it\'s searching using the title of the first track.'
            )
            Log(
                'There\'s not currently a way around this initial failure. '
                'But clicking \'Search Options\' and '
                'entering the title works just fine.'
            )
            Log(
                'This message will appear during the initial '
                'search and the actual manual search.'
            )
            # If this is a custom search,
            # use the user-entered name instead of the scanner hint.
            if media.name:
                Log(
                    'Custom album search for: ' + media.name
                )
                media.album = media.name
        else:
            Log('Album search: ' + media.title)

        # Log some stuff for troubleshooting detail
        self.Log(
            '-----------------------------------'
            '------------------------------------'
        )
        self.Log('* ID:              %s', media.parent_metadata.id)
        self.Log('* Title:           %s', media.title)
        self.Log('* Name:            %s', media.name)
        self.Log('* Album:           %s', media.album)
        self.Log(
            '-----------------------------------'
            '------------------------------------'
        )

        # Normalize the name
        normalizedName = String.StripDiacritics(media.album)
        if len(normalizedName) == 0:
            normalizedName = media.album
        Log(
            'normalizedName = %s', normalizedName
        )

        # Chop off "unabridged"
        normalizedName = re.sub(r"[\(\[].*?[\)\]]", "", normalizedName)
        Log(
            'chopping bracketed text = %s', normalizedName
        )
        normalizedName = normalizedName.strip()
        Log(
            'normalizedName stripped = %s', normalizedName
        )

        self.Log(
            '***** SEARCHING FOR "%s" - AUDIBLE v.%s *****',
            normalizedName, VERSION_NO
        )

        # Make the URL
        if media.artist is not None:
            searchUrl = ctx['AUD_SEARCH_URL'].format(
                (
                    String.Quote((normalizedName).encode('utf-8'), usePlus=True)
                ),
                (
                    String.Quote((media.artist).encode('utf-8'), usePlus=True)
                )
            )
        else:
            searchUrl = ctx['AUD_KEYWORD_SEARCH_URL'] % (
                String.Quote((normalizedName).encode('utf-8'), usePlus=True)
            )
        found = self.doSearch(searchUrl, ctx)

        # Write search result status to log
        if len(found) == 0:
            self.Log('No results found for query "%s"', normalizedName)
            return
        else:
            self.Log(
                'Found %s result(s) for query "%s"', len(found), normalizedName
            )
            i = 1
            for f in found:
                self.Log(
                    '    %s. (title) %s (author) %s (url)[%s]'
                    ' (date)(%s) (thumb){%s}',
                    i, f['title'], f['author'],
                    f['url'], str(f['date']), f['thumb']
                )
                i += 1

        self.Log(
            '-----------------------------------'
            '------------------------------------'
        )
        # Walk the found items and gather extended information
        info = []
        i = 1
        for f in found:
            url = f['url']
            self.Log('URL For Breakdown: %s', url)

            # Get the id
            for itemId in url.split('/'):
                # IDs No longer start with just 'B0'
                if re.match(r'^[0-9A-Z]{10,10}', itemId):
                    break
                itemId = None

            # New Search results contain question marks after the ID
            for q_itemId in itemId.split('?'):
                # IDs No longer start with just 'B0'
                if re.match(r'^[0-9A-Z]{10,10}', q_itemId):
                    break

            if len(itemId) == 0:
                Log('No Match: %s', url)
                continue

            self.Log('* ID is                 %s', itemId)

            title = f['title']
            thumb = f['thumb']
            date = f['date']
            year = ''
            author = f['author']
            narrator = f['narrator']

            if date is not None:
                year = date.year

            # Score the album name
            scorebase1 = media.album
            scorebase2 = title.encode('utf-8')
            # self.Log('scorebase1:    %s', scorebase1)
            # self.Log('scorebase2:    %s', scorebase2)

            score = INITIAL_SCORE - Util.LevenshteinDistance(
                scorebase1, scorebase2
            )

            if media.artist:
                scorebase3 = media.artist
                scorebase4 = author
                # self.Log('scorebase3:    %s', scorebase3)
                # self.Log('scorebase4:    %s', scorebase4)
                score = INITIAL_SCORE - Util.LevenshteinDistance(
                    scorebase3, scorebase4
                )

            self.Log('* Title is              %s', title)
            self.Log('* Author is             %s', author)
            self.Log('* Narrator is           %s', narrator)
            self.Log('* Date is               %s', str(date))
            self.Log('* Score is              %s', str(score))
            self.Log('* Thumb is              %s', thumb)

            if score >= LCL_IGNORE_SCORE:
                info.append(
                    {
                        'id': itemId,
                        'title': title,
                        'year': year,
                        'date': date,
                        'score': score,
                        'thumb': thumb,
                        'artist': author
                    }
                )
            else:
                self.Log(
                    '# Score is below ignore boundary (%s)... Skipping!',
                    LCL_IGNORE_SCORE
                )

            if i != len(found):
                self.Log(
                    '-----------------------------------'
                    '------------------------------------'
                )

            i += 1

        info = sorted(info, key=lambda inf: inf['score'], reverse=True)

        # Output the final results.
        self.Log(
            '***********************************'
            '************************************'
        )
        self.Log('Final result:')
        i = 1
        for r in info:
            description = '\"%s\" by %s [%s]' % (
                r['title'], r['artist'], r['year']
            )
            self.Log(
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
                self.Log(
                    '            *** The score for these results are great, '
                    'so we will use them, and ignore the rest. ***'
                )
                break
            i += 1

    def update(self, metadata, media, lang, force=False):
        self.Log(
            '***** UPDATING "%s" ID: %s - AUDIBLE v.%s *****',
            media.title, metadata.id, VERSION_NO
        )
        ctx = SetupUrls(Prefs['sitetype'], Prefs['site'], lang)

        # Make url
        url = ctx['AUD_BOOK_INFO'] % metadata.id

        try:
            html = HTML.ElementFromURL(url, sleep=REQUEST_DELAY)
        except NetworkError:
            pass

        date = None
        rating = None
        series = ''
        series2 = ''
        series_def = ''
        genre_parent = None
        genre_child = None
        volume = ''
        volume2 = ''
        volume_def = ''

        for r in html.xpath('//div[contains (@id, "adbl_page_content")]'):
            date = self.getDateFromString(
                self.getStringContentFromXPath(
                    r, u'//li[contains (., "{0}")]/span[2]//text()'.format(
                        ctx['REL_DATE_INFO']
                    )
                )
            )
            title = self.getStringContentFromXPath(
                r, '//h1[contains (@class, "adbl-prod-h1-title")]/text()'
            )
            murl = self.getAnchorUrlFromXPath(
                r, 'div/div/div/div/a[1]'
            )
            thumb = self.getImageUrlFromXPath(
                r, 'div/div/div/div/div/img'
            )
            author = self.getStringContentFromXPath(
                r, '//li//a[contains (@class,"author-profile-link")][1]'
            )
            narrator = self.getStringContentFromXPath(
                r, '//li[contains (., "{0}")]//span[2]'.format(
                    ctx['NAR_BY_INFO']
                )
            ).strip().decode('utf-8')
            studio = self.getStringContentFromXPath(
                r, '//li//a[contains (@id,"PublisherSearchLink")][1]'
            )
            synopsis = self.getStringContentFromXPath(
                r, '//div[contains (@class, "disc-summary")]/div[*]'
            ).strip()
            series = self.getStringContentFromXPath(
                r, '//div[contains (@class, "adbl-series-link")]//a[1]'
            )
            genre_parent = self.getStringContentFromXPath(
                r, (
                    '//div[contains(@class,"adbl-pd-breadcrumb")]'
                    '/div[2]/a/span/text()'
                )
            )
            genre_child = self.getStringContentFromXPath(
                r, (
                    '//div[contains(@class,"adbl-pd-breadcrumb")]'
                    '/div[3]/a/span/text()'
                )
            )
            self.Log(
                '-----------------------------------------------'
                'XPATH SEARCH HIT'
                '-----------------------------------------------'
            )

        if date is None:
            for r in html.xpath(
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
                self.Log(page_content)
                json_data = json_decode(page_content)
                for json_data in json_data:
                    if 'datePublished' in json_data:
                        date = json_data['datePublished']
                        title = json_data['name']
                        thumb = json_data['image']
                        # Set rating when available
                        if 'aggregateRating' in json_data:
                            rating = (
                                json_data['aggregateRating']['ratingValue']
                            )
                        author = ''
                        counter = 0
                        for c in json_data['author']:
                            counter += 1
                            if counter > 1:
                                author += ', '
                            author += c['name']
                        narrator = ''
                        counter = 0
                        for c in json_data['readBy']:
                            counter += 1
                            if counter > 1:
                                narrator += ','
                            narrator += c['name']
                        studio = json_data['publisher']
                        synopsis = json_data['description']
                    if 'itemListElement' in json_data:
                        genre_parent = (
                            json_data['itemListElement'][1]['item']['name']
                        )
                        try:
                            genre_child = (
                                json_data['itemListElement'][2]['item']['name']
                            )
                        except:
                            continue

            # prefer copyright year over datePublished
            if Prefs['copyyear']:
                cstring = None

                for r in html.xpath(u'//span[contains(text(), "\xA9")]'):
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

            date = self.getDateFromString(date)

            for r in html.xpath('//span[contains(@class, "seriesLabel")]'):
                series = self.getStringContentFromXPath(
                    r, '//li[contains(@class, "seriesLabel")]//a[1]'
                )
                series2 = self.getStringContentFromXPath(
                    r, '//li[contains(@class, "seriesLabel")]//a[2]'
                )

                series_def = series2 if series2 else series

                volume = self.getStringContentFromXPath(
                    r, '//li[contains(@class, "seriesLabel")]/text()[2]'
                ).strip()
                if volume == ",":
                    volume = ""
                volume2 = self.getStringContentFromXPath(
                    r, '//li[contains(@class, "seriesLabel")]/text()[3]'
                ).strip()
                if volume2 == ",":
                    volume2 = ""

                volume_def = volume2 if volume2 else volume

            # fix series when audible 'forgets' the series link…
            if not series_def:
                for r in html.xpath('//div[contains(@class, "adbl-main")]'):
                    subtitle = self.getStringContentFromXPath(
                        r, 'normalize-space(//li[contains'
                        '(@class, "authorLabel")]'
                        '//preceding::li[1]//span//text())'
                    ).strip()

                w = re.match("(.*)(, Book \d+)", subtitle)
                if not series_def and w:
                    series_def = w.group(1)
                    volume_def = w.group(2)

        # cleanup synopsis
        synopsis = synopsis.replace("<i>", "")
        synopsis = synopsis.replace("</i>", "")
        synopsis = synopsis.replace("<em>", "")
        synopsis = synopsis.replace("</em>", "")
        synopsis = synopsis.replace("<u>", "")
        synopsis = synopsis.replace("</u>", "")
        synopsis = synopsis.replace("<b>", "")
        synopsis = synopsis.replace("</b>", "")
        synopsis = synopsis.replace("<strong>", "")
        synopsis = synopsis.replace("</strong>", "")
        synopsis = synopsis.replace("<ul>", "")
        synopsis = synopsis.replace("</ul>", "\n")
        synopsis = synopsis.replace("<ol>", "")
        synopsis = synopsis.replace("</ol>", "\n")
        synopsis = synopsis.replace("<li>", " • ")
        synopsis = synopsis.replace("</li>", "\n")
        synopsis = synopsis.replace("<br />", "")
        synopsis = synopsis.replace("<p>", "")
        synopsis = synopsis.replace("</p>", "\n")

        self.Log('date:        %s', date)
        self.Log('title:       %s', title)
        self.Log('author:      %s', author)
        self.Log('series:      %s', series)
        self.Log('narrator:    %s', narrator)
        self.Log('studio:      %s', studio)
        self.Log('thumb:       %s', thumb)
        self.Log('rating:      %s', rating)
        self.Log('genres:      %s, %s', genre_parent, genre_child)
        self.Log('synopsis:    %s', synopsis)
        self.Log('Series:      %s', series)
        self.Log('Volume:      %s', volume)
        self.Log('Series2:     %s', series2)
        self.Log('Volume2:     %s', volume2)
        self.Log('Series_def:  %s', series_def)
        self.Log('Volume_def:  %s', volume_def)

        # Set the date and year if found.
        if date is not None:
            metadata.originally_available_at = date

        # Add the genres
        metadata.genres.clear()
        metadata.genres.add(genre_parent)
        metadata.genres.add(genre_child)

        # Add Narrators to Styles
        narrators_list = narrator.split(",")
        contributors_list = ['full cast']
        metadata.styles.clear()
        for narrator in narrators_list:
            if narrator.lower() not in contributors_list:
                metadata.styles.add(narrator.strip())

        # Add Authors to Moods
        author_list = author.split(",")
        contributers_list = [
            'contributor',
            'translator',
            'foreword',
            'translated',
            'full cast',
        ]
        metadata.moods.clear()
        for author in author_list:
            if author.lower() not in contributers_list:
                metadata.moods.add(author.strip())

        # Clean series
        x = re.match("(.*)(: A .* Series)", series_def)
        if x:
            series_def = x.group(1)

        # Clean title
        seriesshort = series_def
        checkseries = " Series"
        # Handle edge cases in titles
        if series_def.endswith(checkseries):
            seriesshort = series_def[:-len(checkseries)]

            y = re.match(
                "(.*)((: .* " + volume_def[2:] + ": A .* Series)|"
                "(((:|,|-) )((" + seriesshort + volume_def + ")|"
                "((?<!" + seriesshort + ", )(" + volume_def[2:] + "))|"
                "((The .*|Special) Edition)|"
                "((?<!" + volume_def[2:] + ": )An? .* "
                "(Adventure|Novella|Series|Saga))|"
                "(A Novel of the .*))|"
                "( \(" + seriesshort + ", Book \d+; .*\))))$",
                title
            )

            if y:
                title = y.group(1)

        # Other metadata
        metadata.title = title
        metadata.title_sort = ' - '.join(
            filter(None, [(series_def + volume_def), title])
        )
        metadata.studio = studio
        metadata.summary = synopsis
        metadata.posters[1] = Proxy.Media(HTTP.Request(thumb))
        metadata.posters.validate_keys(thumb)
        # Use rating only when available
        if rating:
            metadata.rating = float(rating) * 2

        # Collections if/when Plex supports them
        # https://github.com/seanap/Audiobooks.bundle/issues/1#issuecomment-713191070
        metadata.collections.clear()
        metadata.collections.add(series)
        if series2:
            metadata.collections.add(series2)
        self.writeInfo('New data', url, metadata)

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
                    self.Log(e)
                queue.task_done()
            except Queue.Empty:
                continue

    def addTask(self, queue, func, *args, **kargs):
        queue.put((func, args, kargs))

    # Writes metadata information to log.
    def writeInfo(self, header, url, metadata):
        self.Log(header)
        self.Log(
            '-----------------------------------'
            '------------------------------------'
        )
        self.Log(
            '* ID:              %s', metadata.id
        )
        self.Log(
            '* URL:             %s', url
        )
        self.Log(
            '* Title:           %s', metadata.title
        )
        self.Log(
            '* Release date:    %s', str(metadata.originally_available_at)
        )
        self.Log(
            '* Studio:          %s', metadata.studio
        )
        self.Log(
            '* Summary:         %s', metadata.summary
        )

        if len(metadata.collections) > 0:
            self.Log('|\\')
            for i, item in enumerate(metadata.collections):
                self.Log('| * Collection:    %s', metadata.collections[i])

        if len(metadata.genres) > 0:
            self.Log('|\\')
            for i, item in enumerate(metadata.genres):
                self.Log('| * Genre:         %s', metadata.genres[i])

        if len(metadata.moods) > 0:
            self.Log('|\\')
            for i, item in enumerate(metadata.moods):
                self.Log('| * Moods:         %s', metadata.moods[i])

        if len(metadata.styles) > 0:
            self.Log('|\\')
            for i, item in enumerate(metadata.styles):
                self.Log('| * Styles:        %s', metadata.styles[i])

        if len(metadata.posters) > 0:
            self.Log('|\\')
            for poster in metadata.posters.keys():
                self.Log('| * Poster URL:    %s', poster)

        if len(metadata.art) > 0:
            self.Log('|\\')
            for art in metadata.art.keys():
                self.Log('| * Fan art URL:   %s', art)

        self.Log(
            '***********************************'
            '************************************'
            )


def safe_unicode(s, encoding='utf-8'):
    if s is None:
        return None
    if isinstance(s, basestring):
        if isinstance(s, types.UnicodeType):
            return s
        else:
            return s.decode(encoding)
    else:
        return str(s).decode(encoding)
