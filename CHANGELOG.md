## Version 1.5.0.0
  * `reconnect_timeout` parameter in `NetworkConfig`;
  * `endpoints` parameter in `NetworkConfig`. It contains the list of available server 
    addresses to connect. SDK will use one them with the least connect time. 
    `server_address` parameter is still supported but endpoints is prevailing;
  * `net.fetch_endpoints` function to receive available endpoints from the server;
  * `net.set_endpoints` function to set endpoints list for using on next reconnect;
  * `ErrorCode` type for each module. See `types.[MODULE]ErrorCode`.

## Version 1.4.0.1
  * Core improvement: using `concurrent.future` along with `asyncio.future` for response 
    resolving

## Version 1.4.0.0
Fully reworked binding. Is breaking to previous versions.  
  * Response resolvers reimplemented (no while loops with responses);
  * Generators removed, callbacks added.  
    Each callback receives `response_data`, `response_type`, `loop` arguments.
    `loop` argument is not none only when working with `asyncio`;
  * Request params and responses are objects of core `types` now.  
    See https://github.com/tonlabs/TON-SDK/tree/master/docs and `tonclient.types` for more info;
  * Methods' docstrings updated;
  * Tests updated.
