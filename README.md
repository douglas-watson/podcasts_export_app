Podcasts Export App
===================

Douglas Watson, 2022, MIT License

A macOS app that exports apple podcasts to a folder, for later use on a portable mp3 player.

![Podcasts Export Screenshot](images/screenshot.png)

Following the creation of my [automator script](https://github.com/douglas-watson/podcasts_export), many people struggled to install or use it, due to python dependencies. This project is an attempt to help those people by distributing a proper app. If all goes well, it should install like any other macOS app.


🎆 New features 🎆
-----------------

Compared to the automator script, this app allows you to select which downloaded episodes to export. Helpful for large collections.

This one is launched like a regular app, it is no longer registered as a service available from Podcasts.

![Podcasts Export Screenshot](images/dock.png)

Developing
----------

Create a virtual env or conda environment, and install requirements with:

    pip install -r requirements.txt

Building
--------

Build a mac app with:

    ./build.sh

Before distributing, create a disk image with:

    ./build.sh dmg