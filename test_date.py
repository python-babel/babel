def test_format_current_moment(monkeypatch):
    import datetime as datetime_module
    frozen_instant = datetime.utcnow()

    class frozen_datetime(datetime):
@@ -771,7 +770,7 @@ def utcnow(cls):
            return frozen_instant

    # Freeze time! Well, some of it anyway.
    monkeypatch.setattr(datetime_module, "datetime", frozen_datetime)
    monkeypatch.setattr(dates, "datetime_", frozen_datetime)
    assert dates.format_datetime(locale="en_US") == dates.format_datetime(frozen_instant, locale="en_US")
