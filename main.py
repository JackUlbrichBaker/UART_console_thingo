from textual.app import App, ComposeResult
from typing import TypeVar

from textual.screen import Screen
from textual.widgets import Placeholder, Log, Select
from textual.containers import Container, Horizontal, Vertical, Grid
from textual.widgets import Button, Footer, Header, Static, ListView, ListItem, Label
from time import sleep
from textual.binding import Binding
from textual import on
import serial
from serial.tools import list_ports
from textual.screen import ModalScreen


TEXT = "Do you want to learn about Textual CSS?"
SPEED_COMMAND_START = [0xAA, 0xCC, 0x0A, 0x00, 0x05]
SPEED_1000 = SPEED_COMMAND_START + [0xE8, 0x03, 0x00, 0x00]

def crc(data):
    crc = 0
    for byte in data:
        crc ^= byte
    return crc

def build_start_motor_command():
    data = bytearray()
    data.append(0xAA)              # Sync
    data.append(0xCC)              # Class
    data += (6).to_bytes(2, 'little')  # Length
    data.append(0x21)              # Command ID = Start motor
    data.append(0x00)              # Motor ID
    crc_append = crc(data[1:])           # Compute CRC
    data.append(crc_append)
    return bytes(data)
start_cmd = build_start_motor_command()

def build_speed_command(speed_rpm: int) -> bytes:
    # Construct MCP frame to set speed
    motor_id = 0
    command_id = 0x05
    payload = speed_rpm.to_bytes(4, 'little')  # 4 bytes speed

    data = bytearray()
    data.append(0xAA)                      # Sync byte
    data.append(0xCC)                      # Class
    data += (6 + len(payload)).to_bytes(2, 'little')  # Length
    data.append(command_id)
    data.append(motor_id)
    data += payload

    crc_calculated = crc(data[1:])  # Exclude sync byte (0xAA) from CRC
    data.append(crc_calculated)

    return bytes(data)

def build_get_state_command(motor_id=0x00) -> bytes:
    data = bytearray()
    data.append(0xAA)  # Sync
    data.append(0xCC)  # Class
    data += (6).to_bytes(2, 'little')  # Length
    data.append(0x01)  # Command ID: Get Motor State
    data.append(motor_id)
    crc_append = crc(data[1:])  # Exclude Sync from CRC
    data.append(crc_append)
    return bytes(data)
SPEED_COMMAND_TEST = build_speed_command(4000)

listitems = ["test", "two", "three", "four"]
Comm_options = listitems

class motor_driver_controller():
    def __init__(self, comm_port) -> None:

        self.timeout = 1
        self.baud_rate = 1843200
        self.ser_controller = serial.Serial(comm_port, timeout=self.timeout, baudrate=self.baud_rate)
    
    def read_mot(self):
        return self.ser_controller.read(100)
    def send_command(self, command):
        return self.ser_controller.write(command)

class SelectComPort(ModalScreen):
    """Screen with a dialog to select a com port."""

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Pick a Com Port to communicate with", id="question"),
            Select([(opt.product, opt.device) for opt in list_ports.comports(include_links=True)] + [("hard_coded", "/dev/pts/4")], allow_blank=False),
            Button("Quit", variant="error", id="quit"),
            Button("Select", variant="primary", id="cancel"),
            id="dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        sel = self.query_one(Select)
        if event.button.id == "quit":
            self.exit()
        if sel.selection == None:
            self.app.exit()
        self.dismiss(sel.selection)

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
        self.motor_driver_controller = None
    
    def add_commands_to_list(self):
        listview = self.query_one(ListView)
        for listitem in listitems:
            listview.append(ListItem(Label(listitem), name=listitem))
    
    async def print_serial_in(self) -> None:
        log = self.query_one(Log)
        ser = self.motor_driver_controller
        if ser is not None:
            data_in_buffer = str(ser.ser_controller.read_until())
            if data_in_buffer != "":
                log.write_line(data_in_buffer)

    async def print_stub(self) -> None:
        log = self.query_one(Log)
        log.write_line(TEXT)

    async def on_mount(self) -> None:
        self.theme = "gruvbox"
        self.title = "Motor Driver Console"
        self.sub_title = "useful tool for debugging and controlling my motor driver :)"
        self.add_commands_to_list()
        self.set_interval(0.1, self.print_serial_in)
        self.push_screen(SelectComPort(), self.check_comm_port_selected)


    @on(ListView.Selected, "#sidebar")
    def send_command(self, event: ListView):
        log = self.query_one(Log)
        log.write_line(f"TEST {event.item.name}, Comm Port: {self.comm_port}")
        ser = self.motor_driver_controller.ser_controller
        ser.write(start_cmd)
        ser.write(SPEED_COMMAND_TEST)

    def check_comm_port_selected(self, comm_port: str):
        self.comm_port = comm_port
        self.motor_driver_controller = motor_driver_controller(self.comm_port)

if __name__ == "__main__":
    print()
    app = ConsoleApp()
    app.run()
