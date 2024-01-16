import asyncio
from aioquic.asyncio import connect
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived

class EchoClientProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.received_data = asyncio.Queue()

    def quic_event_received(self, event):
        print("Received: ", event)
        if isinstance(event, StreamDataReceived):
            self.received_data.put_nowait(event.data)
            if event.end_stream:
                self.close()

async def run_quic_client():
    configuration = QuicConfiguration(is_client=True)
    configuration.load_verify_locations("../tests/pycacert.pem")

    async with connect("localhost", 4433, configuration=configuration, create_protocol=EchoClientProtocol, local_port=12345) as protocol:
        stream_id = protocol._quic.get_next_available_stream_id()
        protocol._quic.send_stream_data(stream_id, b"Hello!", end_stream=False)
        received_data = await protocol.received_data.get()
        print("Data Received:", received_data)

if __name__ == "__main__":
    asyncio.run(run_quic_client())
