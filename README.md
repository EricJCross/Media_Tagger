# Media Tagger 0.1

A filesystem-driven Windows media tag editor prototype built with Python, PySide6, and Mutagen.

There is **no media database**. Files exist only in the current working set while the application is open.

## Version 0.1 Features

- Open individual files
- Open a directory
- Drag files or directories from Windows Explorer into the application
- Optional `Include Subdirectories`
- MP3 support
- MP4 / M4V / M4A / M4B support
- Read and write:
  - Artist
  - Title
  - Album
  - Album Artist
  - Genre
  - Year
  - Track
  - Disc
- Apple/iTunes MP4 Media Type (`stik`)
  - Home Video
  - Music
  - Audiobook
  - Music Video
  - Movie
  - TV Show
  - Booklet
  - Ringtone
  - Podcast
- Artwork preview
- Multi-file selection and bulk editing
- Only fields you actually edit are written during a bulk update
- Reload selected files after another application changes them
- Remember window/splitter/recursive-scan preferences

## Install

This assumes Python is already installed and the Windows `py` launcher is available.

Double-click:

    Install_Requirements.bat

Or run:

    py -m pip install -r requirements.txt

## Run

Double-click:

    Run_Media_Tagger.bat

Or run:

    py Main.py

## How Multi-File Editing Works

Select multiple rows.

If every selected file has the same value, that value is shown.

If selected files have different values, the field displays:

    <Multiple Values>

The program does **not** overwrite that field unless you actually edit it.

Example:

    Song.mp3   Genre = Kids Car
    Song.mp4   Genre = Kids Home

Select both files and change only Artist.

Only Artist is written. The two Genre values remain unchanged.

If you explicitly type a Genre while both files are selected, the new Genre is written to both files.

## Media Type

Media Type is an Apple/iTunes MP4 field stored in the `stik` atom.

`Music Video` is written as value `6`.

When an MP3 and MP4 are selected together, setting Media Type changes the MP4-family file only. The MP3 writer intentionally ignores Media Type.

## Track and Disc

Both fields accept:

    3

or:

    3/12

MP3 stores the familiar ID3 string form.

MP4 stores the corresponding iTunes tuple.

## Artwork

Version 0.1 displays the first embedded artwork image for a single selected file.

Artwork replacement/removal is not implemented yet.

## Current Limits

This is intentionally a first build.

Not yet implemented:

- Genre rules / custom Genre Manager
- MP3/MP4 pairing
- "Sync Common Fields"
- Filename -> tags
- Tags -> filename
- Artwork replacement/removal
- Undo/redo
- Column persistence
- Dedicated folder tree
- Search/filtering
- AtomicParsley fallback
- Installer packaging

## Testing

Before using the program across a large library, test it against copies of several real files that represent your library:

- MP3 with artwork
- MP4 music video
- MP4 with `Music Video` already set by MetaX
- MP4 with your custom genre
- Files with track totals such as `3/12`

Compare the results in iTunes/Apple software, MetaX, and Tag & Rename. That will tell us whether Mutagen's direct MP4 writer exactly matches the behavior you rely on or whether an AtomicParsley compatibility layer should be added.

## Project Structure

    Media_Tagger_v0_1/
        Main.py
        Media/
            Media_File.py
            Metadata_Model.py
            Mp3_Handler.py
            Mp4_Handler.py
        Services/
            File_Loader.py
            Settings_Manager.py
        UI/
            File_Table.py
            Main_Window.py
            Tag_Editor.py
        requirements.txt
        Install_Requirements.bat
        Run_Media_Tagger.bat

The UI knows about the application's common metadata fields. It does not need to know the ID3 frame names or MP4 atom names.

That separation is intentional so Genre rules, file pairing, and synchronization behavior can be added without rewriting the tagging GUI.
