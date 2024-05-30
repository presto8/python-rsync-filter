# python-rsync-filter

A Python module that implements rsync's sending-side rsync-filter specification.
See the "FILTER RULES" section of "man rsync".

This is a clean room implementation based on the documentation only without
looking at rsync's source code.

Rsync's filter rules are well defined, stable, and have been used in production
settings for many years. Developers needing file pattern include/exclude
functionality may prefer to use rsync's existing specification rather than
inventing their onw.
