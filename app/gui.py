# standard imports
import os
import subprocess
import sys

# textual imports
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Label, Input, DataTable, Markdown, Button

# kuill imports
import app.kdb as kdb

class KuillApp(App):
    ###* Constants *###

    CSS_PATH = "styles.tcss" # CSS file containing the app style
    BINDINGS = [
        Binding("/", "focus_search", "Search", show = True), # kb to focus the search bar
    ]

    ###* Initialization *###

    def __init__(self, databasePath: str) -> None:
        super().__init__() # init parent class

        self.DatabasePath = databasePath
        self.Library = kdb.Library(databasePath = databasePath) # load database from path
    
    ###* App Layout *###

    def compose(self) -> ComposeResult:
        # set title and subtitle
        self.title = "Kuill v0.1.2"
        self.sub_title = "A simple open source tool to organize your scientific knowledge."

        # header
        self.Header = Header()
        yield self.Header

        # search row (label + input)
        self.SearchRow = Horizontal(id = "search_row")
        with self.SearchRow:
            self.SearchLabel = Label(id = "search_label", content = "Search:")
            self.SearchInput = Input(id = "search_input", placeholder = "Author(s), Title, Venue, Year, Keywords")
            yield self.SearchLabel
            yield self.SearchInput

        # app body (results table + details panel)
        self.MainBody = Horizontal(id = "main_body") # stack main body panes horizontally
        with self.MainBody:
            # results block (table)
            self.ResultsBlock = Vertical(id = "results_block") # container for data table
            self.ResultsBlock.border_title = "Results Table"
            with self.ResultsBlock:
                self.ResultsTable = DataTable(id = "results_table")
                self.ResultsTable.cursor_type = "row"
                self.ResultsTable.add_columns("First Author", "Title", "Venue", "Year", "Keywords")
                yield self.ResultsTable

            # details block (markdown)
            self.DetailsBlock = Vertical(id = "details_block") # container for details panel
            self.DetailsBlock.border_title = "Details"
            with self.DetailsBlock:
                self.DetailsMarkdown = Markdown(id = "details_markdown", markdown = "Select an entry to see detailed information here.")
                yield self.DetailsMarkdown

                # open PDF button (starts disabled until an entry is selected)
                self.OpenButtonBlock = Horizontal(id = "open_button_block")
                with self.OpenButtonBlock:
                    self.OpenButton = Button(label = "Open PDF", id = "open_button", disabled = True)
                    yield self.OpenButton

        # footer
        self.Footer = Footer()
        yield self.Footer

    def on_mount(self) -> None:
        """Populate the results table once at strartup."""

        for article in self.Library.ArticlesList:
            self.ResultsTable.add_row(
                article.Authors[0], # only display first author in the table
                article.Title,
                article.Venue,
                article.Year,
                ", ".join(article.Keywords),
            )

    ###* Results Table & Details Panel Logic *###
    
    # render the details of the selected element in the results table in the details panel
    def _render_details(self) -> None:
        # fallback to defaults if no valid row is selected
        if self.ResultsTable.cursor_row is None or self.ResultsTable.cursor_row < 0 or self.ResultsTable.cursor_row >= len(self.Library.ArticlesList):
            self.DetailsMarkdown.update("Select an entry to see detailed information here.")
            # disable open button when nothing selected
            self.OpenButton.disabled = True
            self._currently_selected_pdf_path = None
            return
        
        # extract info from table entry
        article = self.Library.ArticlesList[self.ResultsTable.cursor_row]
        self.OpenButton.disabled = False
        self._currently_selected_pdf_path = "/".join(["library", article.PDFPath])
        self.DetailsMarkdown.update(
            "\n\n".join(
                [
                    f"# {article.Title}",
                    f"**Authors:** {', '.join(article.Authors)}",
                    f"**Venue:** {article.Venue}",
                    f"**Year:** {article.Year}",
                    f"**Keywords:** {', '.join(article.Keywords)}",
                    f"**PDF Path:** {article.PDFPath}",
                ]
            )
        )
    
    # action to execute when the selected row on the results table changes
    @on(DataTable.RowHighlighted, "#results_table")
    def _on_row_highlighted(self) -> None:
        self._render_details()

    # open button pressed handler
    @on(Button.Pressed, "#open_button")
    def _on_open_pressed(self) -> None:
        """Launch the PDF associated with the currently selected entry."""

        if self._currently_selected_pdf_path:
            try:
                if sys.platform.startswith("darwin"):
                    subprocess.run(["open", self._currently_selected_pdf_path]) # TODO: test on Darwin
                elif sys.platform.startswith("win"):
                    os.startfile(self._currently_selected_pdf_path) # TODO: test on Windows
                else:
                    subprocess.run(["xdg-open", self._currently_selected_pdf_path]) #* TESTED
            except Exception:
                pass

    ###* Keybindings *###

    def action_focus_search(self) -> None:
        self.query_one("#search_input", Input).focus()
