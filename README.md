# SeaNap's Audiobook (Audible) metadata agent

## What is this?
A Plex Metadata Agent for Audiobooks stored in a music library.

This agent sets metadata for your Plex Audiobook library, scraping data from Audible.com. It uses the `Album Artist` tag as the books Author and uses the `Album Title` tag as the Book Title. All audio files will need to be tagged correctly in order for this thing to do it's job.

## Differences between my version and Macr0dev's
* The Narrator is mapped to Style.  
* Only Genres put in the Genre tag.  
* The series is currently pulled into AlbumSort tag.  

This version allows for better filtering and cleaner browsing in plex and various audiobook apps (such as PlexAmp), a must have for large libraries. Everything else is the same.
<!-- blank line -->
----
<!-- blank line -->
## Installation
1. Download my repo by clicking [Here](https://github.com/seanap/Audiobooks.bundle/archive/master.zip).  
   * Alternatively, click the green 'Code' dropdown button and select “Download Zip”.
2. The plug-in bundle will be located within a zip archive. Unzip the archive.
3. Edit the bundle’s folder name and remove "-master" so you are left with the foldername “Audiobooks.bundle”
   * Bundles downloaded from GitHub will usually have extra identifiers appended to the bundle’s filename, such as “-master”.
4. Copy or move the plug-in bundle into the Plug-Ins folder on the computer running Plex Media Server
   * Windows: `%LOCALAPPDATA%\Plex Media Server\Plug-ins`
   * macOS: `~/Library/Application Support/Plex Media Server/Plug-ins`
   * Linux: `$PLEX_HOME/Library/Application Support/Plex Media Server/Plug-ins`
5. Restart Plex Media Server to make sure that the new plugin will be loaded.
##### Return to Guide
[Plex Audiobook Guide](https://github.com/seanap/Plex-Audiobook-Guide#configure-metadata-agent-in-plex)

<!-- blank line -->
----
<!-- blank line -->
### Metadata supplied to Plex:

| id3 Tag       | Plex Tag|
| ------------- | ---------------- |
| ALBUM         | Title            |
| ALBUMARTIST   | Author           |
| ALBUMSORT     | Sort Album       |
| cover         | Poster           |

| Scrapped Audible Data  | Plex Tag|
| ------------- | ---------------- |
| Narrator      | Style            |
| Release Date  | Originally Available |
| Publisher's Summary | Review     |
| Series Title  | Collection       |
| Production Studio | Record Label |
| Book/Album Cover | Poster        |
| Genres        | Genre            |

### Library Creation Options:

- Create a `BASIC MUSIC LIBRARY` (not a premium Plex muisc library)
- **DO NOT** check `Use Embedded Tags`
- **DO** check `Store Track Progress`
- Agent - Select `Audiobooks`


### Agent Configuration Options:

If you're in the US and want to scrape from Audible.com - you're all set!

If you're NOT in the US, or just want more flexibility with your searches you have options:

- `Manually Select Audible Site`: This option allows you to manually select which site you're going to scrape.  
- If this is not checked, the language you selected for the library, or the language selected for a manual match will be used to select which site to scrape from.  

- `Select Audible site to use`: This option is ignored if `Manually Select Audible Site` box is not checked.  

### Tips for greatest success:

* Use mp3tag to auto tag and rename files https://github.com/seanap/Audible.com-Search-by-Album  
* Set "Album" tag in audio file as the book title  
* Set "Artist" tag in audio file as the book author    
* Manual 'match' will use the Author/Artist field if it's present, but you cannot enter it manually.  Only the title.  
* Make sure all the tracks have the same Albumartist and Album, and also have correct Track Number tags.  
* Store each in a folder `%author% \ %series% \ %year% - %album% \ %album% (%year%) - pt(%track%)`
* If this agent matches two different books as the same book, which looks like a duplicate in Plex, Unmatch BOTH books and start by manually matching the incorrect book, then re-match the book that was correct.

### Notes:

-Title data in parens ()  such as (Unabridged) is automatically removed before search.  I've found this improves the results and matching.

-Currently, I don't have a great source for author data. What populates now (if any) is being done automatically from last.fm. You're welcome to go add some data there. This was kind of a happy accident.

-The first two genre tags show up in the top right when viewing the album/book.  Genre tags are listed in the following order: Genre1, Genre2

-You can filter by the various tags that are added to each book. Be it author, series, narrator, etc.

-Orignal and bulk of code by Macr0dev https://github.com/macr0dev/Audiobooks.bundle
