set -x
set -e

ls -la
bash <(curl -s https://codecov.io/bash)
