# :bangbang:Updated to new agent Audnexus:bangbang:

# Audiobook (Audible) metadata agent

[![CodeFactor](https://www.codefactor.io/repository/github/seanap/audiobooks.bundle/badge)](https://www.codefactor.io/repository/github/seanap/audiobooks.bundle)
## What is this?
A Plex Metadata Agent for Audiobooks stored in a music library.

This agent sets metadata for your Plex Audiobook library by pulling directly from the internal Audible API. It uses the `Album Artist` file tag as the books Author and uses the `Album Title` file tag as the Book Title. All audio files will need to have these two tags tagged correctly in order for this thing to do its job.

## Differences between Audnexus and Macr0dev's
* The Narrator is mapped to Style.  
* Set's upto 6 meaningfull genres.  
* The series is mapped to Mood, and into AlbumSort tag.  
* Audnexus uses a [database](https://github.com/djdembeck/audnexus) and connects directly to the Audible API
* Audnexus also sets the Author metadata in Plex

This version allows for better filtering and cleaner browsing in plex and various audiobook apps (such as PlexAmp, BookCamp, Prologue), a must have for large libraries. Everything else is the same.
<!-- blank line -->
----
<!-- blank line -->
## Installation
1. Download the plug-in by clicking [Here](https://github.com/djdembeck/Audnexus.bundle/archive/refs/heads/main.zip).  
   * `https://github.com/djdembeck/Audnexus.bundle/archive/refs/heads/main.zip`
2. The plug-in bundle will be located within a zip archive. Unzip the archive.
3. Edit the bundle’s folder name and remove "-main" so you are left with the foldername “Audnexus.bundle”
   * Bundles downloaded from GitHub will usually have extra identifiers appended to the bundle’s filename, such as “-master”, it is importaint that the folder name ends in .bundle  
4. Copy or move the plug-in bundle into the Plug-Ins folder on the computer running Plex Media Server
   * Windows: `%LOCALAPPDATA%\Plex Media Server\Plug-ins`
   * macOS: `~/Library/Application Support/Plex Media Server/Plug-ins`
   * Linux: `$PLEX_HOME/Library/Application Support/Plex Media Server/Plug-ins`
5. Go you your Audiobook Library > Edit > Advanced - This will load the plug in, return to guide for initial config settings.
##### Return to Guide
[Plex Audiobook Guide](https://github.com/seanap/Plex-Audiobook-Guide#configure-metadata-agent-in-plex)

<!-- blank line -->
----
<!-- blank line -->
### Metadata supplied to Plex:

| id3 Tag       | Plex Tag|
| ------------- | ---------------- |
| ALBUM         | Title            |
| ALBUMARTIST   | Author of Album  |
| ALBUMSORT     | Sort Album       |
| ALBUMARTISTSORT | Sort Name [Not used] |
| Genre1/Genre2 | Genre1, Genre2 [Not used]  |
| cover         | Poster  [Not used]         |
| ARTIST        | Artists on Track |

| Set by Audible Agent | Plex Tag|
| ------------- | ---------------- |
| Narrators      | Style            |
| Series        | Mood             |
| Release Date  | Publication Date |
| Publisher's Summary | Review     |
| Production Studio | Record Label |
| Genres    | Genre  |
| Rating | :star::star::star::star::star: |


### Library Creation Options:

 * **General** select `Music`  
 * **Add folders** browse to your Audiobook folders  
 * **Advanced** set the following:  
   * Agent = Audnexus Agents  
   * Keep existing genre's - The new agent pulls 4-6 meaningful genres but if you want to keep your existing CHECK this box  
   * Album sorting - By Name (This uses the Albumsort tag to keep series together and in order)  
   * *UNCHECK* Prefer Local Metadata  
   * *CHECK* Store track progress  
   * *UNCHECK* Author Bio  
   * Genres = None  
   * Album Art = Local Files Only


### Tips for greatest success:

* Use mp3tag to auto tag and rename files https://github.com/seanap/Audible.com-Search-by-Album  
* Set "Album" tag in audio file as the book title  
* Set "Artist" tag in audio file as the book author    
* Manual match for both Album and Author can accept ASIN 
* Make sure all the tracks have the same Albumartist and Album, and also have correct Track Number tags.  
* Store each in a folder `%author% \ %series% \ %year% - %album% \ %album% (%year%).m4b`

### Notes:

-Title data in parens ()  such as (Unabridged) is automatically removed before search.

-The first two genre tags show up in the top right when viewing the album/book.  Genre tags are listed in the following order: Genre1, Genre2, Genre3... etc.

-You can filter by the various tags that are added to each book. Be it author, series, narrator, etc.

-Orignal code by [djdembeck](https://github.com/djdembeck)
