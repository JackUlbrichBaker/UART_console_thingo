from textual.app import App, ComposeResult
from textual.screen import Screen
from textual.widgets import Placeholder, Log
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Static, ListView, ListItem, Label
from time import sleep
from textual.binding import Binding


TEXT = "Do you want to learn about Textual CSS?"

listitems = ["one", "two", "three", "four"]

class Send_Motor_Command(ListView):
    def on_list_view_selected(self):
        do_somthing:

class ConsoleApp(App):
    CSS_PATH = "main.tcss"
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the app"),
        Binding(
            key="question_mark",
            action="help",
            description="Show help screen",
            key_display="?",
        ),
    ]
    def compose(self) -> ComposeResult:
        with Horizontal(classes="column"):
            yield ListView(name = "Sidebar", id="sidebar")
            yield Log(id="body")
        yield Header(show_clock=True, icon="🐟")
        yield Footer()
    
    def add_commands_to_list(self):
        listview = self.query_one(ListView)
        for listitem in listitems:
            listview.append(ListItem(Label(listitem)))
    
    async def print_stub(self) -> None:
        log = self.query_one(Log)
        log.write_line(TEXT)

    async def on_mount(self) -> None:
        self.theme = "tokyo-night"

        self.title = "Motor Driver Console"
        self.sub_title = "useful tool for debugging and controlling my motor driver :)"
        self.add_commands_to_list()
        self.set_interval(0.1, self.print_stub)


if __name__ == "__main__":
    app = ConsoleApp()
    app.run()
