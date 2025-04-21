Usage scenarios
---------------

1. Merging Multiple PO Files (`concat`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Usage:**  
`pybabel concat [options] <po_files>`
Suppose you manage a project with several PO files for the same language (for example, modules or plugins have their own translations), and you want to combine them into a single file for further work or for delivery to translators.

**Example:**

.. code-block:: shell

    pybabel concat -o merged.po module1.po module2.po module3.po

**Features:**

- If the same string has different translations in different files, the resulting file for that string will include a special comment ``#-#-#-#-#  <file> (PROJECT VERSION)  #-#-#-#-#`` and the message will be marked with the ``fuzzy`` flag—this is useful for later manual conflict resolution.
- You can keep only unique strings using the ``-u`` (`--less-than=2`) option.
- Use `--use-first` to take only the first encountered translation for each string, skipping automatic merging of multiple options.
- Output can be sorted alphabetically or by source file (options `-s`, `-F`).

**Typical Use Case:**

    A project has translations from different teams. Before releasing, you need to gather all translations into one file, resolve possible conflicts, and provide the finalized version to translators for review.


2. Updating Translations with a Template and Compendium (`merge`)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Usage:**  
`pybabel merge [options] def.po ref.pot`
You need to update an existing translation file (`def.po`) based on a new template (`ref.pot`), reusing translations from an additional translation memory (compendium).

**Example:**

.. code-block:: shell

    pybabel merge -C my-compendium.po --backup def.po ref.pot

**Features:**

- The compendium (`-C`) allows you to pull translations from a shared translation memory. Multiple compendiums can be used.
- By default, translations from the compendium are used only for new or missing entries in `def.po`.
- The `--compendium-overwrite` option allows overwriting existing translations with those found in the compendium (helpful for terminology standardization).
- When a translation from the compendium is used, a comment is automatically added (this can be disabled with `--no-compendium-comment`).
- The `--backup` flag saves a backup copy of your file before updating (`~` suffix by default, configurable with `--suffix`).

**Typical Use Case:**

    After a release, a new translation template is provided. The team decides to enrich the translation by leveraging a common compendium in order to improve quality and unify terms. The merge command is run with the compendium and backup options enabled.
