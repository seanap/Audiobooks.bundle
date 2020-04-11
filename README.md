# Audiobooks (Audible) metadata agent

Metadata agent for Audiobooks stored in a music library.

This agent scrapes from Audible.com. It uses the `Album Artist` as the books Author and uses the `Album Title` as the Book Title. All audio files will need to be tagged correctly in order for this thing to do it's job. You can manually search for each book if you don't have them tagged ahead of time.

Download: https://github.com/seanap/Audiobooks.bundle/archive/master.zip


### Metadata supplied:

| id3 Tag       | Plex Tag|
| ------------- | ---------------- |
| ALBUM         | Title            |
| ALBUMARTIST   | Author           |

| Audible Data  | Plex Tag|
| ------------- | ---------------- |
| Narrator      | Style         |
| Release Date  | Originally Available |
| Publisher's Summary | Review     |
| Series Title  | Collection           |
| Production Studio | Record Label |
| Book/Album Cover | Poster        |
| Genres        | Genre |



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

Use mp3tag to auto tag and rename files https://github.com/seanap/Audible.com-Search-by-Album  
Set "Album" tag in audio file as the book title  
Set "Artist" tag in audio file as the book author    
Manual 'match' will use the Author/Artist field if it's present, but you cannot enter it manually.  Only the title.  
Make sure all the tracks have the same Artist/Albumartist and Album.  
Store each in a folder ``%author% \ %series% \ %year% - %album% \ %album% (%year%) - pt(%track%)``

### Notes:

-Title data in parens ()  such as (Unabridged) is automatically removed before search.  I've found this improves the results and matching.

-Currently, I don't have a great source for author data. What populates now (if any) is being done automatically from last.fm. You're welcome to go add some data there. This was kind of a happy accident.

-The first two genre tags show up in the top right when viewing the album/book.  Genre tags are listed in the following order: Genre1, Genre2

-You can filter by the various tags that are added to each book. Be it author, series, narrator, etc.

-Orignal code by Macr0dev https://github.com/macr0dev/Audiobooks.bundle
