set -e
set -x

# Install packages with brew
brew update >/dev/null
brew outdated pyenv || brew upgrade --quiet pyenv

# Install required python version for this build
pyenv install -ks $PYTHON_VERSION
pyenv global $PYTHON_VERSION
python --version
