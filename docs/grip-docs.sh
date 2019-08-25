#!/bin/bash

DOCS="FrontierDevelopments-oAuth2-notes.md"
for d in ${DOCS};
do
	HTMLDOC=$(basename "${d}" .md).html
	grip "${d}" --export "${HTMLDOC}" \
		&& chmod 644 "${HTMLDOC}"
done
