#!/bin/bash
# vim: textwidth=0 wrapmargin=0 shiftwidth=2 tabstop=2 softtabstop smartindent

DOCS="FrontierDevelopments-oAuth2-notes.md FrontierDevelopments-CAPI-endpoints.md ../TODO.md"
for d in ${DOCS};
do
  HTMLDOC=$(basename "${d}" .md).html
  if [ "${d}" -nt "${HTMLDOC}" ];
  then
    grip "${d}" --export "${HTMLDOC}" \
      && chmod 644 "${HTMLDOC}"
  fi
done
