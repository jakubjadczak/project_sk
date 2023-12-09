import sys
from PyQt5.QtCore import Qt, QByteArray
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QSlider
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtNetwork import QTcpSocket
from pydub import AudioSegment
from pydub.playback import play
from io import BytesIO, StringIO

class MusicPlayer(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()
        self.init_socket()

    def init_ui(self):
        self.setWindowTitle('Music Streaming Client')

        self.play_button = QPushButton('Play')
        self.play_button.clicked.connect(self.toggle_play_streamed_music)

        self.test_button = QPushButton('Test')
        self.test_button.clicked.connect(self.send_test_request)

        self.volume_slider = QSlider(Qt.Vertical)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.set_volume)

        layout = QVBoxLayout()
        layout.addWidget(self.play_button)
        layout.addWidget(self.test_button)
        layout.addWidget(self.volume_slider)

        self.setLayout(layout)

        self.streaming = False
        self.buffer = QByteArray()

    def init_socket(self):
        self.tcp_socket = QTcpSocket(self)
        self.tcp_socket.connected.connect(self.on_connected)
        self.tcp_socket.readyRead.connect(self.on_ready_read)
        self.tcp_socket.errorOccurred.connect(self.on_error)

        server_address = "127.0.0.1"  # Replace with the server's IP address
        server_port = 8081  # Replace with the server's port

        self.tcp_socket.connectToHost(server_address, server_port)

    def toggle_play_streamed_music(self):
        print('toggle play')
        if not self.streaming:
            self.tcp_socket.write(b"request_stream")
            print("Wysłano żądanie strumieniowania do serwera")

        else:
            self.tcp_socket.disconnectFromHost()

    def send_test_request(self):
        self.tcp_socket.write(b"test")
        print("Wysłano żądanie test do serwera")

    def on_connected(self):
        print("Połączono z serwerem")

    def on_ready_read(self):
        try:
            self.buffer += self.tcp_socket.readAll()
            print(f"Received new batch of data. Current buffer size: {len(self.buffer)} bytes")
            if len(self.buffer) > 1024 * 10 and not self.streaming:  # Adjust the multiplier based on your needs
                print("Rozpoczęto odtwarzanie strumienia")
                self.streaming = True
                self.start_continuous_playback()

        except Exception as e:
            print(f"Błąd przy odbieraniu danych: {e}")

    def on_error(self, socket_error):
        print(f"Błąd gniazda: {socket_error}")

    def start_continuous_playback(self):
        try:
            buffer_data = self.buffer.data()

            # Convert the buffer data to an AudioSegment
            audio_segment = AudioSegment.from_mp3(BytesIO(buffer_data))

            # Play the audio segment
            play(audio_segment)

            self.buffer.clear()

        except Exception as e:
            print(f"Error during continuous playback: {e}")

    def set_volume(self):
        # Adjust the volume using a system-level volume control
        volume = self.volume_slider.value()
        # You may need to implement a system-level volume adjustment here
        print(f"Setting volume to {volume}")

if __name__ == '__main__':
    app = QApplication([])
    player = MusicPlayer()
    player.show()
    sys.exit(app.exec_())
