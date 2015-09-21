set -x
set -e

coverage xml
ls -la
cat coverage.xml
bash <(curl -s https://raw.githubusercontent.com/codecov/codecov-bash/master/codecov)
