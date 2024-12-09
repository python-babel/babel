CUSTOM_EXTRACTOR_COOKIE = "custom extractor was here"


def custom_extractor(fileobj, keywords, comment_tags, options):
    if "treat" not in options:
        raise RuntimeError(f"The custom extractor refuses to run without a delicious treat; got {options!r}")
    return [(1, next(iter(keywords)), (CUSTOM_EXTRACTOR_COOKIE,), [])]
