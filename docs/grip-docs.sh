#!/bin/bash
# vim: textwidth=0 wrapmargin=0 shiftwidth=2 tabstop=2 softtabstop smartindent

DOCS="../README.md README.md FrontierDevelopments-oAuth2-notes.md FrontierDevelopments-CAPI-endpoints.md TODO.md"
for d in ${DOCS};
do
	HTMLDIR=$(dirname "${d}")
  HTMLDOC=$(basename "${d}" .md).html
	HTMLFILE="${HTMLDIR}/${HTMLDOC}"
  if [ "${d}" -nt "${HTMLFILE}" ];
  then
    grip "${d}" --export "${HTMLFILE}" \
      && chmod 644 "${HTMLFILE}"
  fi
done
