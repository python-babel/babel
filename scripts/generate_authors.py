from collections import Counter
from subprocess import check_output

import os

root_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))


def get_sorted_authors_list():
    authors = check_output(['git', 'log', '--format=%aN'], cwd=root_path).decode('UTF-8')
    counts = Counter(authors.splitlines())
    return [author for (author, count) in counts.most_common()]


def get_authors_file_content():
    author_list = '\n'.join('- %s' % a for a in get_sorted_authors_list())

    return '''
Babel is written and maintained by the Babel team and various contributors:

{author_list}

Babel was previously developed under the Copyright of Edgewall Software.  The
following copyright notice holds true for releases before 2013: "Copyright (c)
2007 - 2011 by Edgewall Software"

In addition to the regular contributions Babel includes a fork of Lennart
Regebro's tzlocal that originally was licensed under the CC0 license.  The
original copyright of that project is "Copyright 2013 by Lennart Regebro".
'''.format(author_list=author_list)


def write_authors_file():
    content = get_authors_file_content()
    with open(os.path.join(root_path, 'AUTHORS'), 'w', encoding='UTF-8') as fp:
        fp.write(content)


if __name__ == '__main__':
    write_authors_file()
