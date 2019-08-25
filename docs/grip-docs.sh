#!/bin/bash

DOCS="FrontierDevelopments-oAuth2-notes.md"
for d in ${DOCS};
do
	HTMLDOC=$(basename "${d}" .md).html
	if [ "${d}" -nt "${HTMLDOC}" ];
	then
		grip "${d}" --export "${HTMLDOC}" \
			&& chmod 644 "${HTMLDOC}"
	fi
done
