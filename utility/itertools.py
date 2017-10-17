from collections import deque
from itertools import islice


def exactly_one(iterable):
    """Obtain exactly one item from the iterable or raise an exception."""
    i = iter(iterable)
    try:
        item = next(i)
    except StopIteration:
        raise ValueError("Too few items. Expected exactly one.")
    try:
        next(i)
    except StopIteration:
        return item
    raise ValueError("Too many items. Expected exactly one.")


def consume(iterator, n=None):
    """Advance the iterator n-steps ahead. If n is None, consuem entirely."""
    # Use function that consume iterators at C speed.
    if n is None:
        # feed the entire iterator intoa zero-length deque
        deque(iterator, maxlen=0)
    else:
        # advance to the empty slice starting at position n
        next(islice(iterator, n, n), None)


def last(iterable):
    """Obtain the last item from an iterable.

    :param iterable: Any iterable series.
    :raises ValueError: If the iterable is empty.
    """
    d = deque(iterable, maxlen=1)
    try:
        return d.pop()
    except IndexError:
        raise ValueError(f"cannot return last item from empty iterable {iterable!r}")


def deferred_chain(*iterator_factories):
    """Lazily concatentate iterable series.

    :param *iterator_factories: Each itrable factory must be a zero-argument callable which returns an iterators when
    invoked. Each factory will only be invoked as needed to generate the sequence, so may never be invoked if
    insufficient items are consumed.

    :returns: An iterator over the items produced by the iterators by invoking each iterator factory in turn.
    """
    for factory in iterator_factories:
        iterator = factory()
        yield from iterator
