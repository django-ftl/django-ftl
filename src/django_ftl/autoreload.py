from __future__ import absolute_import, print_function, unicode_literals

import atexit
import logging

try:
    import pyinotify
except ImportError:
    pyinotify = None


logger = logging.getLogger(__name__)


class BundleModifiedHandler(pyinotify.ProcessEvent):

    def my_init(self, bundle=None):
        self.bundle = bundle

    def process_IN_CLOSE_WRITE(self, evt):
        logger.debug("Clearing bundle due to changed file {0}".format(evt.pathname))
        self.bundle.reload()


class Reloader(object):
    def __init__(self, bundle):
        self.bundle = bundle
        self.wm = pyinotify.WatchManager()
        self.handler = BundleModifiedHandler(bundle=bundle)
        self.notifier = pyinotify.ThreadedNotifier(self.wm, self.handler)
        atexit.register(self.stop)
        logger.debug("Starting notifier for {0}".format(bundle))
        self.notifier.start()

    def add_watched_path(self, path):
        logger.debug("Observing {0} for changes".format(path))
        self.wm.add_watch(path, pyinotify.IN_CLOSE_WRITE)

    def stop(self):
        logger.debug("Shutting down observer for {0}".format(self.bundle))
        self.notifier.stop()


def create_bundle_reloader(bundle):
    if pyinotify is None:
        return None
    return Reloader(bundle)
