import asyncio
import os
import time
from aioquic.asyncio import serve, connect
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived

class EchoQuicProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def quic_event_received(self, event):
        print("Received: ", event)
        if isinstance(event, StreamDataReceived):
            self._quic.send_stream_data(event.stream_id, b"Hole Punching", end_stream=True)
            # run_quic_client(self)
            if event.end_stream:
                self.close()

async def run_quic_server():
    configuration = QuicConfiguration(is_client=False)
    configuration.load_cert_chain("../tests/ssl_cert.pem", "../tests/ssl_key.pem")
    await serve("localhost", 4433, configuration=configuration, create_protocol=EchoQuicProtocol)
    await asyncio.Future()

def run_quic_client(quic: QuicConnectionProtocol):
    configuration = QuicConfiguration(is_client=True)
    configuration.load_verify_locations("../tests/pycacert.pem")
    quic._quic._is_client = True
    quic._quic.connect(quic._quic._network_paths[0], time.time())

if __name__ == "__main__":
    try:
        asyncio.run(run_quic_server())
    except Exception as e:
        print(f"Server terminated with an exception: {e}")
