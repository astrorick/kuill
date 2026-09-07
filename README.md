# Kuill

Kuill is a terminal-based bibliography manager written in python that lets you browse, search and organize your collection of scientific papers. It reads from a simple JSON database and provides a TUI (Terminal User Interface) built with [Textual](https://github.com/Textualize/textual) for visualization.

## Features

- Browse your library in an interactive results table with a details panel.
- Search across authors, titles, venues, years and keywords using regex.
- Open PDFs directly from the app using the default app for all major systems.
- Simple JSON database format, the only thing you'll need to maintain.

## Requirements

- Python >= 3.10
- Dependencies listed in `requirements.txt`

## Getting Started

1. Clone the repository:

```bash
git clone https://github.com/astrorick/kuill.git
cd kuill
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run `kuill.py` with a library file:

```bash
python kuill.py library/your_lib_file.json
```

A template library file is provided as `template_library.json` to help you get started.

## Kuill Library Format

The library is a JSON file containing an `articles_list` array. Each entry of the array must be a JSON object with the following fields:

```json
{
    "authors": ["First Author", "Second Author", "Third Author", "..."],
    "title": "Title of Article",
    "venue": "Conference or Journal",
    "year": 2000,
    "doi": "https://doi.org/XXXXXX",
    "keywords": ["first keyword", "second keyword"],
    "date_added": "YYYY-MM-DD HH:MM:SS",
    "read_status": "pending",
    "notes": "Your personal notes here.",
    "pdf": "article_filename.pdf"
}
```

All PDF paths are relative to the directory containing the library file (usually, the `library` folder).

## Contributing

Contributions are very welcome. Feel free to open an issue or submit a pull request on [GitHub](https://github.com/astrorick/kuill).

## License

This project is licensed under the [GNU General Public License v3.0](LICENSE).
