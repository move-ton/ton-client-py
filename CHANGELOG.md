## Version 1.17.0.1
  * `AppObject`, `AppSigningBox`, `AppEncryptionBox`, `AppDebotBrowser` interfaces implementation.  
    Can be found in `tonclient.objects`.  
    Now you can create child class from any of `AppObject` classes, implement required methods, 
    create instance of resulting class and pass it's `dispatcher` method instead of raw `callback` 
    for SDK methods which require `AppObject` as callback.  
    <br/>
    More info and usage examples can be found in `test/[test_crypto|test_async|test_debot]`

## Version 1.17.0.0
  * Binaries updated to `1.17.0`;
  * Changes `1.16.1` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1161--2021-06-16);
  * Changes `1.17.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1170--2021-06-21);

## Version 1.16.0.0
  * Binaries updated to `1.16.0`;
  * Changes `1.15.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1150--2021-05-18);
  * Changes `1.16.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1160--2021-05-25);

## Version 1.14.1.0
  * Binaries updated to `1.14.1`;
  * Changes `1.14.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1140--2021-04-28);
  * Changes `1.14.1` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1141--2021-04-29);

## Version 1.13.0.0
  * Binaries updated to `1.13.0`;
  * Changes `1.13.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1130--2021-04-23);
  * Bug fixed in `types.DecodedOutput.from_dict` method;
  * Modules' types rechecked

## Version 1.12.0.0
  * Binaries updated to `1.12.0`;
  * Changes `1.12.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1120--2021-04-01)  
    _**Has breaking changes in DeBot module**_ 

## Version 1.11.0.0
  * Binaries updated to `1.11.0`;
  * Changes `1.9.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#190-feb-19-2021)
  * Changes `1.10.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1100--2021-03-04)
  * Changes `1.11.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1110--2021-03-05)

## Version 1.8.0.0
  * Binaries updated to `1.8.0`;
  * Changes `1.6.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#160-jan-29-2021)
  * Changes `1.6.2` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#162-feb-3-2021)
  * Changes `1.6.3` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#163-feb-4-2021)
  * Changes `1.7.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#170-feb-9-2021)
  * Changes `1.8.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#180-feb-11-2021)

## Version 1.5.2.0
  * Binaries updated to `1.5.2`;
  * `net` module functions wait for `net.resume` call instead of returning error if 
    called while the module is suspended.

## Version 1.5.1.0
  * Binaries updated to `1.5.1`.  
    See https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md for details.

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
