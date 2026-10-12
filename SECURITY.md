# Security Policy

## Supported Versions

Security patches will mainly target the latest release version,
as listed on [PyPI](https://pypi.org/project/babel/) or [GitHub Releases](https://github.com/python-babel/babel/releases).

Patches for particularly high-impact security issues may be backported to older versions as needed,
but Babel has generally been extremely backward compatible (within major version series),
so for many users, simply upgrading to the latest release should be rather frictionless.

If you're using a version of Babel packaged by a downstream distribution,
such as Debian, Ubuntu, etc., they may backport patches from newer versions with a different policy.

## Reporting a Vulnerability

Please feel free to report vulnerabilities by any method below you feel comfortable with:

* You can use GitHub's form [over here](https://github.com/python-babel/babel/security/advisories/new).
* Contact a maintainer, presently [@akx](https://github.com/akx), over email (akx@iki.fi) or direct messages on listed socials.
  * If you need an encrypted channel of communications, please email/DM first and we'll set something up.

**Do not report sensitive vulnerability information in public.**

### What to include

* Keep it short: a few sentences describing the issue, the Babel and Python versions tested, and ideally a minimal proof-of-concept script that makes it obvious whether the issue is present (e.g. exits with `1` if vulnerable and `0` if not).
  Prefer a script that generates any input files over attachments.
* Check whether the issue also reproduces on `master`. If it reproduces on the latest release but not on `master`, it may have been fixed without its security impact being noticed. That's still worth reporting.
* Check the [reporting scope](#reporting-scope) and [threat model](#threat-model-stride) below, and reference an applicable threat-model item, if any.
  The list is not exhaustive; a vulnerability does not need to fit an existing item to be reported.
* An unexpected Python exception on invalid input is not, by itself, evidence of a security vulnerability or denial of service. If your report involves an exception, explain the additional security impact.
* If you used an LLM or other automated tooling to find the issue, you must verify the report yourself before submitting it: that the APIs exist, that the proof of concept runs, and that the impact is real.
  Deduplicate batches, and report one issue per distinct defect rather than one per trigger.
* A minimal patch is appreciated, but not required.
* Reports that do not contain a potential vulnerability (spam, requests for compliance or due-diligence work) will be discarded without a reply.

### Reporting scope

The STRIDE entries below describe trust assumptions, known limitations, and integration advice.
An entry's presence in the threat model does not exclude every vulnerability in that area.

Reports that require attacker control of inputs explicitly listed as trusted below, or merely demonstrate documented behavior such as unescaped output, are outside the security reporting scope.
Babel does not promise bounded resource use for arbitrary numeric magnitudes, input sizes, or adversarial catalogs and source trees.
Reports that only reproduce these limitations should be regular [issues](https://github.com/python-babel/babel/issues) or pull requests.

However, please report defects that cross the stated trust boundaries or demonstrate security impact beyond these limitations.
For example, a built-in extractor executing code from a scanned source file with trusted configuration and dependencies would violate an intended boundary.
For resource-exhaustion reports, include input size, numeric magnitude where relevant, runtime or memory measurements, and why the documented constraints and mitigations are insufficient.
If you are ever unsure whether a finding is in scope, report it privately with that explanation.

## Threat Model (STRIDE)

Babel's primary attack surface is:

* untrusted strings (locale identifiers, numbers, dates) reaching the formatting and parsing APIs,
* untrusted message catalogs and translations, and
* running the extraction tooling over untrusted source trees.

### Recommendations

In priority order:

1. **Allow-list locales.** Resolve untrusted identifiers against the locales your application supports before passing them to Babel APIs or using them in a filesystem path.
2. **Treat mapping files as code.** Never extract with an unreviewed `babel.cfg` / `pyproject.toml` / `setup.py`.
3. **Treat translations as untrusted input to your templates and format calls.** Verify that your template engine escapes translations themselves (see T-1); pass only plain values as format arguments; review contributed catalogs; fail builds when `pybabel compile` reports errors.
4. **Do not accept patterns from users.** Date, time and number patterns, plural rules, and format strings are developer input.
5. **Bound untrusted values.** Length-limit strings; reject non-finite and huge-magnitude numbers; limit list lengths; validate currency codes.
6. **Sandbox catalog and source-tree processing.** Parse uploaded PO/MO files and run extraction on third-party trees in workers with CPU, memory, and file-size limits, without secrets.
7. **Escape output.** Babel returns text, not markup.
8. **Keep Babel and Python up to date.**

## Threat Model in Detail

This section attempts to document the threat model for developers integrating Babel into applications, along with recommended mitigations.
The analysis below follows the [STRIDE](https://en.wikipedia.org/wiki/STRIDE_model) framework and covers the boundary between untrusted input and the Babel API.

Babel treats the following as trusted inputs:

* The installed package, including code and the locale data files
  `babel/global.dat` and `babel/locale-data/*.dat`, which are **pickles**.
* The process environment (`LANGUAGE`, `LC_*`, `LANG`, `TZ`) and system timezone configuration.
  `TZ` may name a file, which is then opened and parsed as TZif.
* Extraction mapping files, installed entry points, and `pybabel` command-line arguments.
* Patterns and format strings passed to the formatting functions.

### Spoofing

#### S-1: Entry point shadowing

Extraction methods are resolved from `babel.extractors` entry points *before* the built-in extractors, so any package installed in the same environment can replace `python` or `javascript`.
All `babel.checkers` entry points are loaded when `babel.messages.checkers` is imported.

*Mitigations:* use isolated virtual environments with pinned, hash-verified dependencies for extraction and compilation jobs.

#### S-2: Self-declared file metadata

Babel honors metadata declared in a PO file's header (such as charset and language).
`read_po()` with the default `abort_invalid=False` warns for malformed input and carries on with what it could parse.

*Mitigations:* do not derive trust decisions from catalog headers; use `abort_invalid=True` to reject malformed input detected by the PO parser. This does not validate the trustworthiness of the headers or bound resource use (see D-3).

### Tampering

#### T-1: Translations are code-adjacent

A translated string is typically used as a format string or rendered into markup.
A malicious or careless translation can inject HTML/JavaScript if rendered unescaped, cause exceptions to be raised, or cause memory over-allocation with e.g. an enormous field width.
See also I-1.

Template autoescaping does not necessarily escape translations themselves.
For example, Jinja's `{% trans %}` blocks and [new-style gettext calls](https://jinja.palletsprojects.com/en/stable/extensions/#new-style-gettext) treat translated strings as safe markup,
escaping their interpolation arguments instead.

*Mitigations:* review translations from untrusted contributors like code; verify how your template engine handles translated strings, and escape them for the output context. If translations intentionally contain markup, review or sanitize that markup before treating it as safe.

#### T-2: Output is not escaped, and some input is echoed

Babel returns plain text. Locale data (CLDR) is not HTML-safe by contract.
Some functions such as `get_currency_name()`, `get_currency_symbol()` and `format_currency()` return/embed an unrecognized currency code as-is.

*Mitigations:* escape Babel's output for the context it is rendered in like any other string. Validate currency codes with `babel.numbers.validate_currency()` or `is_currency()` before use.

#### T-3: Supply chain

Locale data is generated from CLDR at build time and shipped as pickles.

The CLDR import scripts are maintainer tooling and never run during `pip install`; the CLDR archive is fetched over HTTPS and verified against a pinned digest before extraction.

A compromised release or a writable `site-packages` means arbitrary code execution as soon as Babel is imported or loads locale data.
PyPI releases are always built in a GitHub Actions CI environment and published via PyPI Trusted Publishing.

*Mitigations:* pin with hash verification; keep `site-packages` read-only for the application user.

### Repudiation

#### R-1: No audit trail

Babel does not maintain an audit trail of catalog provenance, changes, or use.

*Mitigations:* audit logging is the integrating application's responsibility. If needed, record who supplied or approved a catalog, which version was deployed, and whether validation succeeded.

### Information Disclosure

#### I-1: `str.format` on translated strings

`str.format` allows attribute and item access, so a translation such as `"{user.__class__.__init__.__globals__[SECRET_KEY]}"` can read anything reachable from the arguments passed to it.

*Mitigations:* vet translations. Prefer `%` formatting for translatable strings and when possible pass plain values such as strings and numbers as format arguments.

#### I-2: Extraction reads through symlinked files

`pybabel extract` may follow symlinks, so strings from outside the scanned tree can end up in POT files.
POT files also contain source paths and line numbers by default, and translator comments when comment extraction is enabled.

*Mitigations:* do not run extraction over untrusted trees on a host holding sensitive files (see also D-2, D-3, E-1); use `--no-location` and review comment tags if the POT is published.

### Denial of Service

#### D-1: Numeric magnitude

`parse_decimal()` accepts whatever `Decimal` does, including `NaN`, `Infinity`, and exponents such as `1e999999999`.
A few bytes of input can therefore describe a number that is expensive to process, or fails; input length alone does not bound the cost of processing the number.

Formatting uses the **ambient** `decimal` context. Whether a value raises `decimal.InvalidOperation` depends on the precision, formatting operation, and pattern.
For example, with the default precision (28 digits), `format_decimal(Decimal('1e25'), locale='en')` raises, while formatting the same value as USD currency or in scientific notation succeeds.
Lowering the precision can produce rounded or failing output; raising it can allow larger output. Decimal precision is not a general resource limit.

*Mitigations:* reject non-finite values and bound the magnitude (see `Decimal.adjusted()`) of untrusted numbers before formatting. Do not modify the global decimal context in processes that format numbers; use `decimal.localcontext()`.

#### D-2: Super-linear algorithms

Babel's algorithms are written for well-formed, human-scale input, and not all of them are linear.

Message extraction and catalog updating are not hardened against adversarially constructed input, and formatting functions are not designed for very large inputs.
Fuzzy matching in catalog updates may exhibit quadratic behavior; disable it with `--no-fuzzy-matching` / `no_fuzzy_matching=True`.

*Mitigations:* bound list lengths and input sizes; run extraction and catalog updates on untrusted input only with CPU time limits.

#### D-3: Catalog memory amplification

Catalog reading builds the entire catalog in memory and the in-memory size of a catalog is not bounded by a constant multiple of the file size.

*Mitigations:* enforce file-size limits, but do not rely on them alone; parse catalogs from untrusted sources in a worker with memory and time limits.

#### D-4: Exception types

Bad input may raise unexpected ordinary Python exceptions, not necessarily only the documented ones.

*Mitigations:* catch broadly at the trust boundary. An unexpected exception type is a bug, not a vulnerability by itself.

### Elevation of Privilege

#### E-1: Mapping files and entry points are executable configuration

An extraction method of the form `package.module:function` (or `package.module.function`) in a mapping file is imported and called, and named methods are loaded from installed entry points (S-1).
Processing a repository's `babel.cfg`, `pyproject.toml` or `setup.py` is equivalent to running code from that repository or from anything importable in the environment.

*Mitigations:* never run `pybabel extract` with a mapping file you have not reviewed; for untrusted trees, supply your own mapping and run in a sandbox without network or secrets (see also D-2, D-3, I-2).

#### E-2: Locale data is pickled

`Locale` data is loaded with `pickle.load()` from the fixed directory `babel/locale-data/`.
Locale identifiers are reduced with `os.path.basename()` (and checked against reserved device names on Windows) before touching the filesystem.

*Mitigations:* keep the installation directory read-only; do not call `babel.localedata.load()` directly with untrusted names.

#### E-3: Locale and domain names become path segments

Translation catalogs live in paths like `<dirname>/<locale>/LC_MESSAGES/<domain>.mo`.
`babel.support.Translations.load()` locates them with the standard library's `gettext.find()`, and the `pybabel` commands build the same paths from their `--locale` and `--domain` options.
As with `gettext` itself, these names are the caller's responsibility. `Locale` parsing validates identifiers as locales, not as filesystem paths.

*Mitigations:* resolve untrusted locale input against an allow-list of identifiers your application supports, and pass the corresponding trusted identifiers to catalog loading and filesystem operations. Never derive `domain` from user input.

#### E-4: Plural rule compilation

For performance, `babel.plural.PluralRule` compiles rules to Python with `compile()`/`eval()`.
The source is regenerated from a strict parse, so rule text is never executed as written, and in normal use rules come from CLDR.
Untrusted rule strings can still raise `RecursionError` or `ZeroDivisionError`.

Babel itself never evaluates a catalog's `Plural-Forms` expression, but `gettext.GNUTranslations` (used by `babel.support.Translations`) may.

*Mitigations:* do not build `PluralRule` objects from untrusted input.
