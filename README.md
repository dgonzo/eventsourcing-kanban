# Event Sourcing Kanban Example

## Quickstart

    $ python3 -m venv .venv
    $ source .venv/bin/activate
    $ pip install -r requirements.txt
    $ apistar create_tables
    $ apistar run
    $ http :8080/NewUser name="Name" password="Mk91Q^U%" email="email@dot.com"

## TODO

### First Priority
- [] active record classes (stored event schema, indexes and performance of the queries);
- [] active record strategy (database management system);
- [] the JSON object encoder and decoder;
- [] the optional cipher strategy; and
- [] the event store object which holds it all together.

### Second Priority
- [] the layers (interface, application, domain, infrastructure);
- [] how an aggregate can respond to commands by constructing and applying and publishing events;
- [] how to replay events to get current state using a mutator function; how an entity factory can work;
- [] how a repository can provide a dictionary-like interface for accessing domain entities by ID;
- [] how domain services can work;
- [] how an aggregate root can work;
- [] how to use entities within an aggregate;
- [] how to use value objects within an aggregate;
- [] how to use an application object both to bind the domain layer and infrastructure layer, and to present application services;
- [] application policies and publish-subscribe mechanisms;
- [] how interfaces can use an application object;
- [] how application logs can allow projections to update themselves from the application state; and
- [] how notification logs can allow remote projections to update another application.

### Third Priority
- [] how traversing historical events can be used to answer common "BI" questions like user behavior and detailed utilization trends
- [] how historical events can be used as a rich supply of data for use in forecasting and machine learning

