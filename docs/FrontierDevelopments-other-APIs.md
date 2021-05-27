# Other Frontier Developers APIs for Elite Dangerous

## Community Goals

As of 2021-05-27 we know of:

    https://api.orerve.net/2.0/website/initiatives/list?lang=en 

1. Note the `lang=en` parameter passed.  These languages are known to be
  supported:

    1. `de` - German
    1. `fr` - French
    1. `es` - Spanish
    1. `pt` - Portugese (Brazilian?)
    1. `ru` - Russian

1. The output format will differ depending on the `Accept` HTTP header
   you send.
   
    1. `Accept: */*` will return JSON, as per the response header
     `Content-Type: application/json`.
    1. `Accept: text/xml` will return XML as per the response header
     `Content-Type: application/xml`.

