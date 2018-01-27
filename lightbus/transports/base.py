from typing import Sequence, Tuple, List, Generator

from lightbus.api import Api
from lightbus.exceptions import NothingToListenFor
from lightbus.message import RpcMessage, EventMessage, ResultMessage


class RpcTransport(object):
    """Implement the sending and receiving of RPC calls"""

    async def call_rpc(self, rpc_message: RpcMessage, options: dict):
        """Publish a call to a remote procedure"""
        raise NotImplementedError()

    async def consume_rpcs(self, apis: Sequence[Api]) -> Sequence[RpcMessage]:
        """Consume RPC calls for the given API"""
        raise NotImplementedError()


class ResultTransport(object):
    """Implement the send & receiving of results

    """

    def get_return_path(self, rpc_message: RpcMessage) -> str:
        raise NotImplementedError()

    async def send_result(self, rpc_message: RpcMessage, result_message: ResultMessage, return_path: str):
        """Send a result back to the caller

        Args:
            rpc_message (): The original message received from the client
            result_message (): The result message to be sent back to the client
            return_path (str): The string indicating where to send the result.
                As generated by :ref:`get_return_path()`.
        """
        raise NotImplementedError()

    async def receive_result(self, rpc_message: RpcMessage, return_path: str, options: dict) -> ResultMessage:
        """Receive the result for the given message

        Args:
            rpc_message (): The original message sent to the server
            return_path (str): The string indicated where to receive the result.
                As generated by :ref:`get_return_path()`.
            options (dict): Dictionary of options specific to this particular backend
        """
        raise NotImplementedError()


class EventTransport(object):
    """ Implement the sending/consumption of events over a given transport.

    The simplest implementation should simply be capable of:

        1. Consuming all events
        2. Sending events

    However, consuming all events will probably be unnecessary in most situations.
    You can therefore selectively listen for events by implementing
    ``start_listening_for()`` and ``stop_listening_for()``.

    Implementing these methods will have several benefits:

      * Will reduce resource use
      * Will allow for dynamically changing listened-for events at runtime

    See Also:

        lightbus.RedisEventTransport: Implements the start_listening_for()
            and stop_listening_for() methods

    """

    async def send_event(self, event_message: EventMessage, options: dict):
        """Publish an event"""
        raise NotImplementedError()

    def consume(self, listen_for: List[Tuple[str, str]], context: dict, **kwargs):
        """Consume messages for the given APIs

        Examples:

            Consuming events::

                listen_for = [
                    ('mycompany.auth', 'user_created'),
                    ('mycompany.auth', 'user_updated'),
                ]
                async with event_transport.consume(listen_for) as event_message:
                    print(event_message)

        """
        if not listen_for:
            raise NothingToListenFor(
                'EventTransport.consume() was called without providing anything '
                'to listen for in the "listen_for" argument.'
            )
        return self.fetch(listen_for, context, **kwargs)

    async def fetch(self, listen_for: List[Tuple[str, str]], context:dict, **kwargs) -> Generator[EventMessage, None, None]:
        """Consume RPC messages for the given events

        Must return a tuple, where the first item is a iterable of
        EventMessages and the second item is an arbitrary value which will
        be passed to consumption_complete() (below) should the events
        be executed successfully.

        Events the bus is not listening for may be returned, they
        will simply be ignored.
        """
        raise NotImplementedError()

    async def consumption_complete(self, event_message: EventMessage, context: dict):
        pass
