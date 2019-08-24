#!/usr/bin/env python3
# vim: textwidth=0 wrapmargin=0 tabstop=2 shiftwidth=2 softtabstop smartindent

import os

print('Content-Type: text/plain')
print()
for e in os.environ:
  print("{} = {}".format(e, os.environ.get(e)))
