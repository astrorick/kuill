from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Label, Input, DataTable, Markdown

import database

class KuillApp(App):
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

    def __init__(self, databasePath: str) -> None:
        super().__init__()

        self.DatabasePath = databasePath
    
    ##########################################
    # App Layout
    ##########################################

    def compose(self) -> ComposeResult:
        # set title and subtitle
        self.title = "Kuill v0.1.0"
        self.sub_title = "A simple open source tool to organize your scientific knowledge."

        # header
        self.Header = Header()
        yield self.Header

        # search row (label + input)
        self.SearchRow = Horizontal(id = "search_row") # horizontal search row
        with self.SearchRow:
            self.SearchLabel = Label(id = "search_label", content = "Search:")
            self.SearchInput = Input(id = "search_input", placeholder = "Author(s), Title, Venue, Year, Keywords")
            yield self.SearchLabel
            yield self.SearchInput

        # app body (results table + details panel)
        self.MainBody = Horizontal(id = "main_body") # stack main body panes horizontally
        with self.MainBody:
            # results block (label + table)
            self.ResultsBlock = Vertical(id = "results_block") # stack results block elements vertically
            self.ResultsBlock.border_title = "Results"
            with self.ResultsBlock:
                self.ResultsTable = DataTable(id = "results_table")
                self.ResultsTable.cursor_type = "row"
                self.ResultsTable.add_columns("First Author", "Title", "Venue", "Year", "Keywords")
                yield self.ResultsTable

            # details block (label + panel)
            self.DetailsBlock = Vertical(id = "details_block") # stack details block elements vertically
            self.DetailsBlock.border_title = "Details"
            with self.DetailsBlock:
                self.DetailsMarkdown = Markdown(id = "details_markdown", markdown = "Select an entry to see detailed information here.")
                yield self.DetailsMarkdown

        # footer
        self.Footer = Footer()
        yield self.Footer

    def on_mount(self) -> None:
        # load database once at startup
        self._load_database()

    ##########################################
    # Database Handling
    ##########################################

    # load database from JSON file and populate results table
    def _load_database(self):
        # load JSON file
        self.Database = database.LoadJSON(self.DatabasePath)

        # populate results tabel
        for article in self.Database.ArticlesList:
            self.ResultsTable.add_row(
                ", ".join(article.Authors),
                article.Title,
                article.Venue,
                article.Year,
                ", ".join(article.Keywords)
            )

    ##########################################
    # Results Table and Info Panel Logic
    ##########################################
    
    # render the details of the selected element in the results table in the details panel
    def _render_details(self) -> None:
        # fallback to defaults if no valid row is selected
        if self.ResultsTable.cursor_row is None or self.ResultsTable.cursor_row < 0 or self.ResultsTable.cursor_row >= len(self.Database.ArticlesList):
            self.DetailsMarkdown.update("Select a paper to see details here.")
            return
        
        # extract info from table entry
        article = self.Database.ArticlesList[self.ResultsTable.cursor_row]
        self.DetailsMarkdown.update(
            "\n\n".join(
                [
                    f"# {article.Title}",
                    f"**Authors:** {', '.join(article.Authors)}",
                    f"**Venue:** {article.Venue}",
                    f"**Year:** {article.Year}",
                    f"**Keywords:** {', '.join(article.Keywords)}",
                    f"**PDF:** {article.PDF}",
                ]
            )
        )
    
    # action to execute when the selected row on the results table changes
    @on(DataTable.RowHighlighted, "#results_table")
    def _on_row_highlighted(self) -> None:
        self._render_details()

    ##########################################
    # Keybindings
    ##########################################

    def action_focus_search(self) -> None:
        self.query_one("#search_input", Input).focus()
