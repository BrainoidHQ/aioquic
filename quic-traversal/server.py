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
            if event.end_stream:
                self.close()

async def run_quic_server():
    configuration = QuicConfiguration(is_client=False)
    configuration.load_verify_locations("../tests/pycacert.pem")
    configuration.load_cert_chain("../tests/ssl_cert.pem", "../tests/ssl_key.pem")
    await serve("localhost", 12346, configuration=configuration, create_protocol=EchoQuicProtocol)
    await run_quic_client()
    await asyncio.Future()

async def run_quic_client():
    print("Running client")
    configuration = QuicConfiguration(is_client=True)
    configuration.load_verify_locations("../tests/pycacert.pem")
    async with connect("localhost", 12345, configuration=configuration, create_protocol=EchoQuicProtocol, local_port=12346) as protocol:
        stream_id = protocol._quic.get_next_available_stream_id()
        protocol._quic.send_stream_data(stream_id, b"Hello!", end_stream=False)
        received_data = await protocol.received_data.get()
        print("Data Received:", received_data)

if __name__ == "__main__":
    try:
        asyncio.run(run_quic_server())
    except Exception as e:
        print(f"Server terminated with an exception: {e}")
