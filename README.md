# rsyncfilter

A Python module that implements rsync's sending-side rsync-filter specification.

This is a clean room implementation based on the "FILTER RULES" section of the
"man rsync" documentation without looking at rsync's source code.

Rsync's filter rules are well defined, stable, and have been used in production
settings for many years. Developers needing file pattern include/exclude
functionality may prefer to use rsync's existing specification rather than
inventing their own.
