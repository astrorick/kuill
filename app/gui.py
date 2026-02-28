# standard imports
import os
import platform
import re
import subprocess

# textual imports
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, DataTable, Footer, Header, Input, Label, Markdown
from textual.validation import Validator, ValidationResult

# custom validator to validate regular expressions
class RegexValidator(Validator):
    def __init__(self, failure_description: str | None = None) -> None:
        super().__init__(failure_description)
        self.Pattern: re.Pattern | None = None

    def validate(self, regex: str) -> ValidationResult:
        try:
            self.Pattern = re.compile(regex, re.IGNORECASE)
            return self.success()
        except re.error as exc:
            self.Pattern = None
            return self.failure(str(exc))

# kuill imports
import app.lib as lib

class KuillApp(App):
    ###* Constants *###

    CSS_PATH = "style.tcss" # CSS file containing the app style
    BINDINGS = [
        Binding("d", "toggle_dark", "dark mode", tooltip = "Toggle dark mode"),
        Binding("s", "focus_search", "search", tooltip = "Focus the search bar"),
    ]

    ###* Initialization *###

    def __init__(self, libraryFilePath: str) -> None:
        super().__init__() # init parent class
        self.Library = lib.Library(libraryFilePath = libraryFilePath) # load library from file
    
    ###* App Layout *###

    def compose(self) -> ComposeResult:
        # header
        self.Header = Header(id = "header", show_clock = True)
        yield self.Header

        # library info row
        self.LibraryInfoRow = Horizontal(id = "library_info_row")
        with self.LibraryInfoRow:
            self.LibraryInfoRowKeyLabel = Label(id = "library_info_row_key_label", content = "Library File:")
            self.LibraryInfoRowValueLabel = Label(id = "library_info_row_value_label", content = self.Library.LibraryFilePath)
            yield self.LibraryInfoRowKeyLabel
            yield self.LibraryInfoRowValueLabel

        # search row
        self.SearchRow = Horizontal(id = "search_row")
        with self.SearchRow:
            self.SearchRowKeyLabel = Label(id = "search_row_key_label", content = "Search:")
            self.SearchRowSearchInput = Input(id = "search_row_search_input", placeholder = "Author(s), Title, Venue, Year, Keywords", validators = [RegexValidator()])
            yield self.SearchRowKeyLabel
            yield self.SearchRowSearchInput

        # main app body
        self.MainBody = Horizontal(id = "main_body")
        with self.MainBody:
            self.ResultsBlock = Vertical(id = "results_block")
            with self.ResultsBlock:
                self.ResultsTable = DataTable(id = "results_table", cursor_type = "row", fixed_columns = 1)
                yield self.ResultsTable
            self.DetailsBlock = VerticalScroll(id = "details_block")
            with self.DetailsBlock:
                self.DetailsMarkdown = Markdown(id = "details_markdown")
                self.DetailsOpenPDFButton = Button(id = "details_open_pdf_button", label = "Open PDF")
                yield self.DetailsMarkdown
                yield self.DetailsOpenPDFButton

        # footer
        self.Footer = Footer(id = "footer", show_command_palette = False)
        yield self.Footer

    def on_mount(self) -> None:
        # set title and subtitle
        self.title = "Kuill v0.1.2"
        self.sub_title = "A simple open source tool to organize your scientific knowledge."

        # set border titles
        self.ResultsBlock.border_title = "Results Table"
        self.DetailsBlock.border_title = "Details"

        # populate the results table once at startup
        self.ResultsTable.add_columns("ID", "First Author", "Title", "Venue", "Year", "Keywords")
        self._refresh_results_table(self.Library.ArticlesList)
        
        # focus search bar
        self.SearchRowSearchInput.focus()

    ###* Search Row Logic *###

    @on(Input.Changed, "#search_row_search_input")
    def _on_search_row_search_input_changed(self) -> None:
        if self.SearchRowSearchInput.is_valid:
            filteredArticlesList = self.Library.FilteredArticlesList(self.SearchRowSearchInput.validators[0].Pattern)
            self._refresh_results_table(filteredArticlesList)

    ###* Results Table & Details Panel Logic *###

    # refresh results table entries
    def _refresh_results_table(self, articlesList: list[lib.Article]) -> None:
        self.ResultsBlock.border_title = f"Results Table - {len(articlesList)}/{len(self.Library.ArticlesList)}"
        self.ResultsTable.clear()
        for article in articlesList:
            self.ResultsTable.add_row(
                article.ID,
                article.Authors[0], # only display first author in the table
                article.Title,
                article.Venue,
                article.Year,
                ", ".join(article.Keywords),
            )
    
    # render the details of the selected element of the results table in the details panel
    def _render_article_details(self) -> None:
        article = self._get_article_by_ID(self.ResultsTable.get_row_at(self.ResultsTable.cursor_row)[0])
        self.DetailsMarkdown.update(
            "\n\n".join(
                [
                    f"# {article.Title}",
                    f"**Authors:** {', '.join(article.Authors)}",
                    f"**Venue:** {article.Venue}",
                    f"**Year:** {article.Year}",
                    f"**Keywords:** {', '.join(article.Keywords)}",
                    f"**Added**: {article.Added}",
                    f"**PDF Path:** {article.PDF}",
                    f"**Notes**: {article.Notes}"
                ]
            )
        )
    
    # action to execute when the selected row on the results table changes
    @on(DataTable.RowHighlighted, "#results_table")
    def _on_result_table_row_highlighted(self) -> None:
        self._render_article_details()

    # action to execute when the open pdf button is pressed
    @on(Button.Pressed, "#details_open_pdf_button")
    def _on_details_open_pdf_button_pressed(self) -> None:
        article = self._get_article_by_ID(self.ResultsTable.get_row_at(self.ResultsTable.cursor_row)[0])
        self._open_PDF_on_system("/".join([self.Library.LibraryFolderPath, article.PDF]))

    ###* Keybindings *###

    def action_toggle_dark(self) -> None:
        self.theme = ("textual-dark" if self.theme == "textual-light" else "textual-light")

    def action_focus_search(self) -> None:
        self.SearchRowSearchInput.focus()

    ###* Utilities *###

    # get article from library based on article ID
    def _get_article_by_ID(self, articleID: int) -> lib.Article:
        return next((a for a in self.Library.ArticlesList if a.ID == articleID), None)
    
    # open the pdf pointed at by the provided path using the appropriate system process
    def _open_PDF_on_system(self, pdfPath: str) -> bool:
        systemType = platform.system()

        if systemType not in ["Windows", "Linux", "Darwin"]:
            self.notify(title = "Warning!", message = f"Unsupported OS '{platform.system()}'", severity = "warning")
            return False
        
        if systemType == "Windows":
            os.startfile(pdfPath) #* TESTED
        elif systemType == "Linux":
            subprocess.call(('xdg-open', pdfPath)) #* TESTED
        elif systemType == "Darwin":
            subprocess.call(("open", pdfPath)) # TODO: to be tested
        
        return True
