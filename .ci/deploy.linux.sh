set -x
set -e

ls -la
coverage xml
bash <(curl -s https://codecov.io/bash)
