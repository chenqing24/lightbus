# Design Document

Warren will be a new message queue for Python 3, backed by AMQP. 
The emphasis is on providing conceptually simple communication 
between multiple applications/processes.

Working is the working name for the project, it may change.

## Motivation

*This was originally and briefly discussed in a 
[Hacker News theead](https://news.ycombinator.com/item?id=14556988).*

Current Python message queues function well in the case where there 
is a single app which needs to queue tasks for execution later.
The reasons for this can be broken down as follows:

**Broker limitations** - Queues such as [rq](http://python-rq.org/)
support are limited by the use of Redis as a broker. This 
becomes a problem when dealing with losly coupled apps (details below)

**Complexity** - [Celery](http://celery.readthedocs.io/) in particular 
becomes particularly conceptually complex when dealing with with 
multiple applications communicating via AMQP. This is partly because 
Celery's terminology overlaps and somewhat conflicts with that of AMQP.
It is also because the Celery documentation is also pretty light on details 
when it comes to more complex setups.

**Conceptual mapping** - Messages sent via apps seem to break down into 
two categories, events & calls. Event messages should be sent without 
caring who is listening and without expecting a response. An app should 
be able to have multiple listeners for an event. Calls 
require that a process is present to respond, and the response must be 
returned to the calling process. I believe surfacing this distinction 
in the message queue library would significantly simplify client code 
and reduce boilerplate.

**Testing & debugging** - I’ve found writing tests for existing 
queues to be difficult. I want simple ways to both assert that a message was 
created and simulate incoming messages. Both should take identical parameters.
I would also like to see much better debugging tools, to help answer the question 
“Why isn’t App B receiving message X from App A?”

## Why AMQP

For the reasons detailed above I am proposing that this message queue be 
tightly coupled to the underlying broker (i.e. because 
supporting multiple brokers leads to significant complexity in other popular message queues).

I am also proposing that the broker be AMQP-based 
(e.g. [RabbitMQ](https://www.rabbitmq.com)). This is because I feel 
AMQP provides the features needed to losely couple applications via a message queue.

For example, I want to send a ``user.registered`` event from App A. App A should 
be able to send this without knowing if anyone is listening for it, without knowing 
what queue it should go on, and without knowing anything about the implementation
of the event handlers. Moreover, App B should be able to listen for ``user.registered`` without 
having to know anything about where the event comes from.

With brokers such as Redis this isn’t possible because App A needs push a message 
to the queue that App B is listening on. App A therefore needs to know that App B exists and 
that it is listening on a particular queue. Additionally, if App C then also wants to listen 
for the event then it will need its own queue. At this point App A needs to enqueue the message *twice*, 
once for App B and once for App C.

AMQP solves this by adding the concept of ‘exchanges’. 
With AMQP, App B would create its own queue and configure it to receive messages 
from one or more exchanges, perhaps also filtering for only certainly messages.
App A sends a message to the AMQP *exchange*. AMQP then places that message into 
each queue listening on that exchange. This includes the queue that App B created, 
and therefore App B receives the message.

Note that in this case App A only had to know what exchange to send the message to, 
and the logic for receiving messages lies entirely in the hands of the receivers.
App C and App D could come along and create their own queues and receive events 
without App A ever knowing or caring.

## Concerns

**History repeating** - Presumably this has all been done before. 
What did/do those implementations look like? What were their failings? Am 
I bound to repeat them?

**AMQP suitability** - I’ve heard rumours of RabbitMQ being unstable under 
heavy load. Is this still true? Are there alternative AMQP brokers? Also,
are there reasons AMQP wouldn’t be suitable?

**Demand** - Is there demand for a project such as this? Do others encounter these 
pain points? If not, why not?

**Collaborators** - Currently it is just me, @adamcharnock. These things are more 
sustainable with multiple people. See below…

## Get involved!

I’d much prefer to work on this as a team. Input at the design stage will 
also be particularly important, but coding and maintenance help is also excellent.

I’m hoping the implementation can be kept small and sleek, and I imagine this will 
be a slow burn over 12ish months.

There is probably also a web UI side-project down the road. Something for managing 
scheduled tasks, and perhaps monitoring/debugging.


## Implementation

Watch this space. I would like to at least partially address the above 
concerns before designing an implementation.

