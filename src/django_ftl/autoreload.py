import logging

import django.core.signals as django_signals
import pyinotify

logger = logging.getLogger(__name__)


class BundleModifiedHandler(pyinotify.ProcessEvent):
    def my_init(self, reloader=None):
        self.reloader = reloader

    def process_IN_CLOSE_WRITE(self, evt):
        logger.debug(f"Clearing bundle due to changed file {evt.pathname}")
        self.reloader.trigger_reload()


class Reloader:
    def __init__(self, bundle):
        self.bundle = bundle
        self.wm = pyinotify.WatchManager()
        self.watches = {}
        self.handler = BundleModifiedHandler(reloader=self)
        # ThreadedNotifier seems to give us horrible problems with Django's
        # devserver when it comes to auto reloading. So we use a Notifier and
        # run the checks for every new request.
        logger.debug(f"Creating notifier for {bundle}")
        self.notifier = pyinotify.Notifier(self.wm, self.handler, timeout=100)
        django_signals.request_started.connect(self.new_request)

    def new_request(self, sender, **kwargs):
        try:
            self.notifier.process_events()
            while (
                self.notifier.check_events()
            ):  # loop in case more events appear while we are processing
                self.notifier.read_events()
                self.notifier.process_events()
        except RuntimeError:
            # Sometimes get:
            #  RuntimeError: concurrent poll() invocation
            pass

    def add_watched_path(self, path):
        logger.debug(f"Observing {path} for changes")
        self.watches.update(self.wm.add_watch(path, pyinotify.IN_CLOSE_WRITE))

    def trigger_reload(self):
        # Remove watches, because the Bundle will add them again after a reload.
        self.wm.rm_watch(list(self.watches.values()))
        self.bundle.reload()


def create_bundle_reloader(bundle):
    return Reloader(bundle)
