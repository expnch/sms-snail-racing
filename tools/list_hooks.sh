set -euo pipefail
source env.sh

curl -s -request POST 'https://api.zipwhip.com/webhook/list' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode "session=$ZW_SESSION_KEY" | jq '.response[]'
