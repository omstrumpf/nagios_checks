#!/bin/bash
# Usage: submit_passive_check <nagios_url> <host> <service> <state> <output> [perfdata]

# Source: https://www.dorkbrain.com/docs/2017/11/03/nagiosbash-example-script-to-submit-passive-checks/

usage() {
  echo "Usage:"
  echo "submit_passive_check.sh <nagios_url> <host> <service> <state> <output> [perfdata]"
}

if [ "$#" -lt 5 ] || [ "$#" -gt 6 ]; then
  echo "Illegal number of arguments."
  usage
  exit 1
fi

NAGIOS_URL="$1"
CHECK_HOST="$2"
CHECK_SERVICE="$3"
CHECK_STATE="$4"
CHECK_OUTPUT="$5"
CHECK_PERFDATA="$6"

CURL_OPTS="--silent"

# Note that this only works because I have middleware that fills in the
# user/password on my wireguard network. you may need to pass
# --user "${NAGIOS_USER}:${NAGIOS_PASS}".
CURL_LOG=$(curl ${CURL_OPTS} \
     --data-urlencode "cmd_typ=30" \
     --data-urlencode "cmd_mod=2" \
     --data-urlencode "host=${CHECK_HOST}" \
     --data-urlencode "service=${CHECK_SERVICE}" \
     --data-urlencode "plugin_state=${CHECK_STATE}" \
     --data-urlencode "plugin_output=${CHECK_OUTPUT}" \
     --data-urlencode "performance_data=${CHECK_PERFDATA}" \
     "${NAGIOS_URL}/cgi-bin/cmd.cgi")

echo "${CURL_LOG}" | grep -q "successfully submitted"
RESULT=$?
if [[ $RESULT -ne 0 ]]; then
  echo -e "ERROR: Error submitting passive check to Nagios CGI!\n\n${CURL_LOG}" >&2
  exit 1
fi

exit 0

