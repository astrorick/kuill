from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Label, Input, DataTable, Markdown


class Kuill(App):
    ##########################################
    # Constants
    ##########################################

    # define CSS path to load app styles
    CSS_PATH = "styles.tcss"

    # define keybindings
    BINDINGS = [
        Binding("/", "focus_search", "Search", show = True), # focus the search bar
    ]

    ##########################################
    # Initialization
    ##########################################

    def __init__(self) -> None:
        super().__init__()

        # DEBUG
        self._papers: list[dict] = [
            {
                "authors": ["Ada Lovelace", "Alan Turing"],
                "title": "Example Paper One",
                "year": 2024,
                "venue": "ExampleConf",
                "keywords": ["example", "systems"],
                "pdf": "library/example1.pdf",
            },
            {
                "authors": ["Grace Hopper"],
                "title": "Example Paper Two",
                "year": 2022,
                "venue": "ExampleJournal",
                "keywords": ["compilers"],
                "pdf": "library/example2.pdf",
            },
        ]
    
    ##########################################
    # Layout
    ##########################################

    def compose(self) -> ComposeResult:
        # header
        yield Header()

        # search row (label + input)
        with Horizontal(id = "search_row"):
            yield Label("Search: ", id = "search_label")
            yield Input(
                placeholder = "Author, Title, Venue, Year, Keyword",
                id = "search_input",
            )

        # app body (results table + details panel)
        with Horizontal(id = "body"): # stack horizontally
            # results block (label + table)
            with Vertical(id = "results_block"): # stack vertically
                yield Label("Results", id = "results_label")
                table = DataTable(id = "results_table")
                table.cursor_type = "row"
                table.add_columns("First Author", "Title", "Venue", "Year", "Keywords")
                yield table

            # details block (label + panel)
            with Vertical(id = "details_block"): # stack vertically
                yield Label("Details", id = "details_label")
                yield Markdown(
                    "Select an entry to see detailed information here.",
                    id = "details_md",
                )

        # footer
        yield Footer()

    ##########################################
    # Results Table and Info Panel Logic
    ##########################################

    # executes after layout definition
    def on_mount(self) -> None:
        table = self.query_one("#results_table", DataTable)
        for p in self._papers:
            table.add_row(
                p["authors"][0],
                p["title"],
                p["venue"],
                p["year"],
                p["keywords"],
            )
    
    # action to execute when the selected row on the results table changes
    @on(DataTable.RowHighlighted, "#results_table")
    def _on_row_highlighted(self) -> None:
        """When the user moves the cursor in the results table, update details."""
        self._render_details()
    
    # render details of selected element of results table to info panel
    def _render_details(self) -> None:
        md = self.query_one("#details_md", Markdown)
        table = self.query_one("#results_table", DataTable)

        row = table.cursor_row
        if row is None or row < 0 or row >= len(self._papers):
            md.update("Select a paper to see details here.")
            return
        
        p = self._papers[row]
        authors = ", ".join(p["authors"]) if p["authors"] else "-"
        keywords = ", ".join(p["keywords"]) if p["keywords"] else "-"
        year = str(p["year"]) if p.get("year") is not None else "-"

        md.update(
            "\n".join(
                [
                    f"### {p['title']}",
                    "",
                    f"**Authors:** {authors}",
                    "",
                    f"**Year:** {year}",
                    "",
                    f"**Venue:** {p['venue'] or '-'}",
                    "",
                    f"**Keywords:** {keywords}",
                    "",
                    f"**PDF:** {p['pdf'] or '-'}",
                ]
            )
        )

    ##########################################
    # Keybindings
    ##########################################

    def action_focus_search(self) -> None:
        self.query_one("#search_input", Input).focus()
