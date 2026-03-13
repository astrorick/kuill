# standard imports
import os
import platform
import subprocess

# textual imports
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Button, DataTable, Footer, Header, Input, Label, Markdown

# kuill imports
from app import __version__
import app.lib as lib

class KuillApp(App):
    ###* Constants *###

    CSS_PATH = "style.tcss" # CSS file containing the app style
    BINDINGS = [
        Binding("d", "toggle_dark", "dark mode", tooltip = "Toggle dark mode"),
        Binding("s", "focus_search", "search", tooltip = "Focus the search bar"),
    ]

    ###* Initialization *###

    def __init__(self, library_file_path: str) -> None:
        super().__init__()

        # load library from file
        self.library = lib.Library(library_file_path = library_file_path)
    
    ###* App Layout *###

    def compose(self) -> ComposeResult:
        # header
        self.header = Header(id = "header", show_clock = True)
        yield self.header

        # library info row
        self.library_info_row = Horizontal(id = "library_info_row")
        with self.library_info_row:
            self.library_info_row_key_label = Label(id = "library_info_row_key_label", content = "Library File:")
            self.library_info_row_value_label = Label(id = "library_info_row_value_label", content = self.library.library_file_path)
            yield self.library_info_row_key_label
            yield self.library_info_row_value_label

        # search row
        self.search_row = Horizontal(id = "search_row")
        with self.search_row:
            self.search_row_key_label = Label(id = "search_row_key_label", content = "Search:")
            self.search_row_query_input = Input(id = "search_row_query_input", placeholder = "Author(s), Title, Venue, Year, Keywords")
            yield self.search_row_key_label
            yield self.search_row_query_input

        # main app body
        self.main_body = Horizontal(id = "main_body")
        with self.main_body:
            self.results_block = Vertical(id = "results_block")
            with self.results_block:
                self.results_table = DataTable(id = "results_table", cursor_type = "row", fixed_columns = 1)
                yield self.results_table
            self.details_block = VerticalScroll(id = "details_block")
            with self.details_block:
                self.details_markdown = Markdown(id = "details_markdown")
                self.details_open_pdf_button = Button(id = "details_open_pdf_button", label = "Open PDF")
                yield self.details_markdown
                yield self.details_open_pdf_button

        # footer
        self.footer = Footer(id = "footer", show_command_palette = False)
        yield self.footer

    def on_mount(self) -> None:
        # set title and subtitle
        self.title = f"Kuill v{__version__}"
        self.sub_title = "A simple open source tool to organize your scientific knowledge."

        # set border titles
        self.results_block.border_title = "Results Table"
        self.details_block.border_title = "Details"

        # prepare the results table and populate once at startup
        self.results_table.add_columns("ID", "First Author", "Title", "Venue", "Year", "Keywords")
        self._refresh_results_table(self.library.articles_list)
        
        # focus search bar
        self.search_row_query_input.focus()

    ###* Search Row Logic *###

    @on(Input.Changed, "#search_row_query_input")
    def _on_search_row_query_input_changed(self) -> None:
        valid, filtered_articles = self.library.filtered_articles_list(self.search_row_query_input.value)
        if valid:
            self.search_row_query_input.remove_class("-invalid")
            self.search_row_query_input.add_class("-valid")
            self._refresh_results_table(filtered_articles)
        else:
            self.search_row_query_input.remove_class("-valid")
            self.search_row_query_input.add_class("-invalid")

    ###* Results Table & Details Panel Logic *###

    # refresh results table entries
    def _refresh_results_table(self, articles_list: list[lib.Article]) -> None:
        self.results_block.border_title = f"Results Table - {len(articles_list)}/{len(self.library.articles_list)}"
        self.results_table.clear()
        for article in articles_list:
            self.results_table.add_row(
                article.id,
                article.authors[0], # only display first author in the table
                article.title,
                article.venue,
                article.year,
                ", ".join(article.keywords),
            )
    
    # render the details of the selected element of the results table in the details panel
    def _render_article_details(self) -> None:
        article = self._get_article_by_id(self.results_table.get_row_at(self.results_table.cursor_row)[0])

        # update markdown
        self.details_markdown.update(
            "\n\n".join(
                [
                    f"# {article.title}",
                    f"**Authors:** {', '.join(article.authors)}",
                    f"**Venue:** {article.venue}",
                    f"**Year:** {article.year}",
                    f"**DOI:** {article.doi}",
                    f"**Keywords:** {', '.join(article.keywords)}",
                    f"**Added**: {article.added}",
                    f"**PDF Path:** {article.pdf}",
                    f"**Notes**: {article.notes}"
                ]
            )
        )

        # enable/disable open pdf button based on pdf field
        if os.path.exists(article.pdf):
            self.details_open_pdf_button.disabled = False
        else:
            self.details_open_pdf_button.disabled = True
    
    # action to execute when the selected row on the results table changes
    @on(DataTable.RowHighlighted, "#results_table")
    def _on_result_table_row_highlighted(self) -> None:
        self._render_article_details()

    # action to execute when the open pdf button is pressed
    @on(Button.Pressed, "#details_open_pdf_button")
    def _on_details_open_pdf_button_pressed(self) -> None:
        article = self._get_article_by_id(self.results_table.get_row_at(self.results_table.cursor_row)[0])
        self._open_pdf_on_system(os.path.join(os.path.dirname(self.library.library_file_path), article.pdf))

    ###* Keybindings *###

    def action_toggle_dark(self) -> None:
        self.theme = ("textual-dark" if self.theme == "textual-light" else "textual-light")

    def action_focus_search(self) -> None:
        self.search_row_query_input.focus()

    ###* Utilities *###

    # get article from library based on article ID
    def _get_article_by_id(self, id: int) -> lib.Article:
        return next((a for a in self.library.articles_list if a.id == id), None)
    
    # open the pdf pointed at by the provided path using the appropriate system process
    def _open_pdf_on_system(self, pdf_path: str) -> bool:
        system_type = platform.system()

        if system_type not in ["Windows", "Linux", "Darwin"]:
            self.notify(title = "Warning!", message = f"Unsupported OS '{platform.system()}'", severity = "warning")
            return False

        if system_type == "Windows":
            os.startfile(pdf_path) #* TESTED
        elif system_type == "Linux":
            subprocess.call(('xdg-open', pdf_path)) #* TESTED
        elif system_type == "Darwin":
            subprocess.call(("open", pdf_path)) # TODO: to be tested

        return True
