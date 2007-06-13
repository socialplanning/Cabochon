Cabochon is an event server which works over HTTP.  It is heavily
inspired by Pebble.  Servers subscribe to named events with HTTP
callbacks. Clients issue those events to Cabochon.  Cabochon
sends the events on to subscribers.  

When used with the appropriate client library, Cabochon will not lose
messages.  It may sometimes send duplicate messages.  For most
applications, this won't matter.  When it does, it should be
preventable by having servers annotate data that is the result of
a message with some message id, and discard messages which duplicate
already-processed messages.

Restriction: You can't have multiple subscribers at the same URL.  


Installation and Setup
======================

Install ``Cabochon`` using easy_install::

    easy_install Cabochon

Make a config file as follows::

    paster make-config Cabochon config.ini
    
Tweak the config file as appropriate and then setup the application::

    paster setup-app config.ini
    
Then you are ready to go.
