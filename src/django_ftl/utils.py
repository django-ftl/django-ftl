def make_namespace(**attributes):
    class namespace:
        pass

    namespace = namespace()
    for k, v in attributes.items():
        setattr(namespace, k, v)

    return namespace
