from django_ftl.bundles import Bundle

# This module should not raise an exception if you try to import it


main = Bundle(["tests/main.ftl"], default_locale="en", require_activate=True)


class MyThing:
    my_label = main.format_lazy("simple")
