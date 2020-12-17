set -euo pipefail
source ../env.sh

ids=$(curl -s -request POST 'https://api.zipwhip.com/webhook/list' \
--header 'Content-Type: application/x-www-form-urlencoded' \
--data-urlencode "session=$ZW_SESSION_KEY" | jq -r '.response[].webhookId')


for id in $ids; do
  echo "$id"
  curl --location --request POST 'https://api.zipwhip.com/webhook/delete' \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode "session=$ZW_SESSION_KEY" \
  --data-urlencode "webhookId=$id"
done
