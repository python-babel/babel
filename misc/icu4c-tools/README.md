# icu4c-tools

Some haphazard tools for cross-checking results between ICU4C and Babel.
These are not meant to be production-ready or e.g. guaranteed to not leak memory in any way.

## icu4c_date_format

### Compiling

This worked on my macOS – on a Linux machine, you shouldn't need the `PKG_CONFIG_PATH` environment variable.

```
env PKG_CONFIG_PATH="/opt/homebrew/opt/icu4c@76/lib/pkgconfig" make bin/icu4c_date_format
```

### Running

E.g.

```
env TEST_TIMEZONES=Pacific/Honolulu TEST_LOCALES=en_US,en,en_GB TEST_TIME_FORMAT="YYYY-MM-dd H:mm zz" bin/icu4c_date_format
```
