# Streaming metrics fixture

This disposable standard-library Python project tests three concurrent stacks.
Each stack adds a streaming helper, then a second operation that consumes it.
The host creates jj changes from checked file exports; no sandbox history or
credentials are imported. Run `python3 -m unittest discover -s tests -v`.
