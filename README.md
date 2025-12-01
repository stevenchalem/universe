# Universe Today Article Downloader

A Python script to download all articles from universetoday.com.

## Features

- Downloads articles from sitemap.xml or via pagination
- Saves articles as HTML files with metadata
- Resume capability - can continue if interrupted
- Rate limiting to be respectful to the server
- Progress tracking and reporting
- Test mode for trying before full download

## Installation

1. Install Python 3.7 or higher
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Download all articles using sitemap:

```bash
python download_articles.py
```

### Command Line Options

```bash
python download_articles.py --help
```

Options:
- `--output DIR` or `-o DIR`: Specify output directory (default: articles)
- `--email EMAIL` or `-e EMAIL`: Your contact email (included in User-Agent and From header)
- `--project-url URL` or `-p URL`: URL for your project/repository (included in User-Agent)
- `--user-agent STRING` or `-u STRING`: Custom User-Agent string (overrides default)
- `--no-sitemap`: Use pagination instead of sitemap
- `--max-pages N`: Maximum pages to crawl (pagination mode only)
- `--delay SECONDS`: Delay between requests (default: 2.0 seconds)
- `--test`: Test mode - only download first 10 articles

### Examples

Test with 10 articles first:
```bash
python download_articles.py --test
```

Download with your contact email (recommended for transparency):
```bash
python download_articles.py --email your.email@example.com
```

Download to custom directory with faster rate:
```bash
python download_articles.py --output my_articles --delay 1.5 --email you@example.com
```

Use pagination method instead of sitemap:
```bash
python download_articles.py --no-sitemap
```

Download first 50 pages only:
```bash
python download_articles.py --no-sitemap --max-pages 50
```

## Output Structure

The script creates an output directory (default: `articles/`) containing:

- `*.html` - Article HTML files
- `*.html.json` - Metadata files for each article (URL, download date, status)
- `download_progress.json` - Progress tracking file for resume capability

## How It Works

1. **Sitemap Method** (default): Fetches article URLs from sitemap.xml
2. **Pagination Method**: Crawls through paginated listing pages
3. Downloads each article as HTML
4. Saves metadata alongside each article
5. Tracks progress to allow resuming interrupted downloads
6. Uses 2-second delay between requests by default to be respectful

## Resume Capability

If the download is interrupted, simply run the script again. It will:
- Load the progress from `download_progress.json`
- Skip already downloaded articles
- Continue from where it left off

## Notes

- The default 2-second delay between requests is to be respectful to the server
- All articles are saved as HTML files with their original content
- Metadata files contain the original URL and download timestamp
- The script handles network errors gracefully and continues with remaining articles

## Proper Identification

The script includes several mechanisms to properly identify itself to server administrators:

### User-Agent Header

By default, the script uses: `UniverseTodayArchiver/1.0 (Personal archival project)`

You can customize this by adding your contact email and/or project URL:

```bash
python download_articles.py --email your.email@example.com
```

This will create: `UniverseTodayArchiver/1.0 (your.email@example.com) (Personal archival project)`

Or with a project URL:

```bash
python download_articles.py --email you@example.com --project-url https://github.com/yourname/your-repo
```

This will create: `UniverseTodayArchiver/1.0 (you@example.com) +https://github.com/yourname/your-repo`

### From Header

When you provide an email with `--email`, it's also added to the HTTP `From` header as recommended by RFC 7231 for automated agents.

### Custom User-Agent

You can provide a completely custom User-Agent:

```bash
python download_articles.py --user-agent "MyBot/1.0 (contact@example.com; +http://mysite.com/bot)"
```

### robots.txt Check

The script automatically fetches and displays the robots.txt file before starting the download, allowing you to verify compliance.

## Ethical Considerations

This script is designed to be respectful and transparent:

- **Proper identification**: Uses descriptive User-Agent and From headers
- **Rate limiting**: 2 seconds between requests by default (configurable)
- **robots.txt awareness**: Displays robots.txt at start for manual review
- **Resume capability**: Avoids re-downloading content after interruptions
- **Only public content**: Downloads publicly available articles

**IMPORTANT**: Before running this script:

1. Review the robots.txt output when the script starts
2. Ensure you comply with Universe Today's terms of service
3. Consider providing your contact email with `--email` for transparency
4. Adjust `--delay` if needed to be more conservative

Server administrators will be able to identify your scraper in their logs through the User-Agent and From headers.
