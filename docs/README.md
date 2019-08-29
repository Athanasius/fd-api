# Contents
1. [TODO](TODO.md) - the current TODO list
1. [FrontierDevelopments-oAuth2-notes](FrontierDevelopments-oAuth2-notes.md) - Notes on how to utilise FDev's oAuth2 mechanism.
1. [FrontierDevelopments-CAPI-endpoints](FrontierDevelopments-CAPI-endpoints.md) = Notes on the available CAPI end points, how to use them, and what they return.
1. [fd-api-config.yaml-sample](fd-api-config.yaml-sample) - documentation of the required configuration file for this project to be usable.  Copy to the location of this docs/ directory (i.e. ..) and edit your Application information in.
1. [example-auth-decode.json](example-auth-decode.json) - Example (elided) output from the oAuth2 /decode end point.
1. [grip-docs.sh](grip-docs.sh) - Script to utilise the python program 'grip' to generate local .html copies of the .md files in this directory.  This saves spamming commits up to github to check formatting.  The resulting .html files are ignored by git.

## Notes
### User-Agent

Frontier Developments have requested that all access to both the CAPI
and the Authorization service use a custom User-Agent header that
matches this regular expression:

		EDCD-[A-Za-z]+-[.0-9]+
e.g.

		EDCD-miggy-0.0.1
so that they can more easily track down anyone causing issues. Obviously
the middle part should probably be something that aligns with the
application name you gave when applying for Authorization access.
