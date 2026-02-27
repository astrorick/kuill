# standard imports
import os
import subprocess
import sys

# textual imports
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Input, Label, Markdown, Select

# kuill imports
import app.lib as lib

class KuillApp(App):
    ###* Constants *###

    CSS_PATH = "style.tcss" # CSS file containing the app style
    BINDINGS = [
        Binding("d", "toggle_dark", "Toggle dark mode"), # toggle dark mode
        Binding("/", "focus_search", "Search", show = True), # focus the search bar
    ]

    ###* Initialization *###

    def __init__(self, libraryFilePath: str) -> None:
        super().__init__() # init parent class
        self.Library = lib.Library(libraryFilePath = libraryFilePath) # load library from file
    
    ###* App Layout *###

    def compose(self) -> ComposeResult:
        # header
        yield Header(id = "header", show_clock = True)

        # library info row
        yield Horizontal(
            Label(id = "library_info_row_key_label", content = "Library File:"),
            Label(id = "library_info_row_value_label", content = self.Library.LibraryFilePath),
            Button(id = "library_info_row_refresh_button", label = "Refresh"),
            id = "library_info_row",
        )

        # search row
        yield Horizontal(
            Label(id = "search_row_key_label", content = "Search:"),
            Input(id = "search_row_search_input", placeholder = "Author(s), Title, Venue, Year, Keywords"),
            id = "search_row"
        )

        # main app body
        yield Horizontal(
            Vertical(
                DataTable(id = "results_table", cursor_type = "row"),
                id = "results_block"
            ),
            Vertical(
                Markdown(id = "details_markdown"),
                Button(id = "details_open_button", label = "Open PDF"),
                id = "details_block"
            ),
            id = "main_body"
        )

        # footer
        yield Footer(id = "footer", show_command_palette = False)

    def on_mount(self) -> None:
        # set title and subtitle
        self.title = "Kuill v0.1.2"
        self.sub_title = "A simple open source tool to organize your scientific knowledge."

        # set border titles
        self.query_exactly_one("#results_block", Vertical).border_title = "Results Table"
        self.query_exactly_one("#details_block", Vertical).border_title = "Details"

        # populate the results table once at startup
        self.query_exactly_one("#results_table", DataTable).add_columns("First Author", "Title", "Venue", "Year", "Keywords")
        #for article in self.Library.ArticlesList:
        #    self.ResultsTable.add_row(
        #        article.Authors[0], # only display first author in the table
        #        article.Title,
        #        article.Venue,
        #        article.Year,
        #        ", ".join(article.Keywords),
        #    )

        # focus search bar
        self.query_exactly_one("#search_row_search_input", Input).focus()

    ###* Results Table & Details Panel Logic *###
    
    # render the details of the selected element in the results table in the details panel
    #def _render_details(self) -> None:
    #    # fallback to defaults if no valid row is selected
    #    if self.ResultsTable.cursor_row is None or self.ResultsTable.cursor_row < 0 or self.ResultsTable.cursor_row >= len(self.Library.ArticlesList):
    #        self.DetailsMarkdown.update("Select an entry to see detailed information here.")
    #        # disable open button when nothing selected
    #        self.OpenButton.disabled = True
    #        self._currently_selected_pdf_path = None
    #        return
    #    
    #    # extract info from table entry
    #    article = self.Library.ArticlesList[self.ResultsTable.cursor_row]
    #    self.OpenButton.disabled = False
    #    self._currently_selected_pdf_path = "/".join(["library", article.PDFPath])
    #    self.DetailsMarkdown.update(
    #        "\n\n".join(
    #            [
    #                f"# {article.Title}",
    #                f"**Authors:** {', '.join(article.Authors)}",
    #                f"**Venue:** {article.Venue}",
    #                f"**Year:** {article.Year}",
    #                f"**Keywords:** {', '.join(article.Keywords)}",
    #                f"**PDF Path:** {article.PDFPath}",
    #            ]
    #        )
    #    )
    
    # action to execute when the selected row on the results table changes
    #@on(DataTable.RowHighlighted, "#results_table")
    #def _on_row_highlighted(self) -> None:
    #    self._render_details()

    # open button pressed handler
    #@on(Button.Pressed, "#open_button")
    #def _on_open_pressed(self) -> None:
    #    """Launch the PDF associated with the currently selected entry."""
    #
    #    if self._currently_selected_pdf_path:
    #        try:
    #            if sys.platform.startswith("darwin"):
    #                subprocess.run(["open", self._currently_selected_pdf_path]) # TODO: test on Darwin
    #            elif sys.platform.startswith("win"):
    #                os.startfile(self._currently_selected_pdf_path) # TODO: test on Windows
    #            else:
    #                subprocess.run(["xdg-open", self._currently_selected_pdf_path]) #* TESTED
    #        except Exception:
    #            pass

    ###* Keybindings *###

    def action_toggle_dark(self) -> None:
        self.theme = ("textual-dark" if self.theme == "textual-light" else "textual-light")

    def action_focus_search(self) -> None:
        self.query_exactly_one("#search_row_search_input", Input).focus()
