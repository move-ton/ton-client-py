## Version 1.36.0.0

- Binaries updated to `1.36.0`;
- Changes `1.36.0` (https://github.com/tonlabs/ever-sdk/blob/master/CHANGELOG.md#1360--2022-07-01);

## Version 1.35.0.0

- Binaries updated to `1.35.0`;
- Changes `1.34.3` (https://github.com/tonlabs/ever-sdk/blob/master/CHANGELOG.md#1343--2022-06-08);
- Changes `1.35.0` (https://github.com/tonlabs/ever-sdk/blob/master/CHANGELOG.md#1350--2022-06-28);

## Version 1.34.2.0

- Binaries updated to `1.34.2`;
- Changes `1.34.0` (https://github.com/tonlabs/ever-sdk/blob/master/CHANGELOG.md#1340--2022-05-18);
- Changes `1.34.1` (https://github.com/tonlabs/ever-sdk/blob/master/CHANGELOG.md#1341--2022-05-26);
- Changes `1.34.2` (https://github.com/tonlabs/ever-sdk/blob/master/CHANGELOG.md#1342--2022-05-30);

**Breaking changes**

- `client.config` changed from instance attribute to method, now should call `client.config()` or `await client.config()`
- `AppDebotBrowser.perform_invoke_debot` method signature changed.
  Now it accepts `config: ClientConfig` instead of `client: TonClient`

## Version 1.33.1.0

- Binaries updated to `1.33.1`;
- Changes `1.33.0` (https://github.com/tonlabs/ever-sdk/blob/master/CHANGELOG.md#1330--2022-05-02);
- Changes `1.33.1` (https://github.com/tonlabs/ever-sdk/blob/master/CHANGELOG.md#1331--2022-05-10);

## Version 1.32.0.1

- Bug fix in `types.AbiData` by [PR#3](https://github.com/move-ton/ton-client-py/pull/3).
  Thanks to [@abionics](https://github.com/abionics)

## Version 1.32.0.0

- Binaries updated to `1.32.0`;
- Changes `1.32.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1320--2022-03-22);

## Version 1.31.0.0

- Binaries updated to `1.31.0`;
- Changes `1.31.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1310--2022-03-09);

## Version 1.30.0.0

- Binaries updated to `1.30.0`;
- Changes `1.27.1` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1271--2021-12-09);
- Changes `1.28.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1280--2021-12-24);
- Changes `1.28.1` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1281--2022-01-25);
- Changes `1.29.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1290--2022-02-03);
- Changes `1.30.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1300--2022-02-04);

## Version 1.27.0.1

- Internal refactor: methods' return types suggestion are correct and clear now;

## Version 1.27.0.0

- Binaries updated to `1.27.0`;
- Changes `1.26.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1260--2021-11-25);
- Changes `1.26.1` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1261--2021-12-01);
- Changes `1.27.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1270--2021-12-03);

## Version 1.25.0.0

- Binaries updated to `1.25.0`;
- Changes `1.25.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1250--2021-11-08);

## Version 1.24.0.0

- Binaries updated to `1.24.0`;
- Changes `1.24.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1240--2021-10-18);

## Version 1.23.0.0

- Binaries updated to `1.23.0`;
- Changes `1.23.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1230--2021-10-05);

## Version 1.22.0.0

- Binaries updated to `1.22.0`;
- Changes `1.22.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1220--2021-09-20);

## Version 1.21.5.0

- Binaries updated to `1.21.5`;
- Changes `1.21.3` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1213--2021-09-02);
- Changes `1.21.4` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1214--2021-09-08);
- Changes `1.21.5` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1215--2021-09-13);

## Version 1.21.2.0

- Binaries updated to `1.21.2`;
- Changes `1.21.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1210--2021-08-18);
- Changes `1.21.1` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1211--2021-08-24);
- Changes `1.21.2` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1212--2021-08-25);

## Version 1.20.1.0

- Binaries updated to `1.20.1`;
- Changes `1.20.1` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1201--2021-07-30);

## Version 1.20.0.0

- Binaries updated to `1.20.0`;
- Changes `1.20.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1200--2021-07-16);

## Version 1.19.0.0

- Binaries updated to `1.19.0`;
- Changes `1.19.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1190--2021-07-07);
- `TonException` object improved:
  - Now exception object has `client_error: ClientError` attribute.
    All `ClientError` attributes are available, e.g. `e.client_error.code`;
  - `module` attribute added to error `client_error` attribute.
    You can check error module, e.g. `e.client_error.module == ClientErrorCode`.
    All error modules names can be found in `tonclient.types.*ErrorCode`.

## Version 1.18.0.0

- Binaries updated to `1.18.0`;
- Changes `1.18.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1180--2021-06-26);
- **Note: Possible breaking**

  ```python
  # tonclient/client.py

  # DEVNET_BASE_URL = 'net.ton.dev' changed to
  DEVNET_BASE_URLS = [
      'https://net1.ton.dev/',
      'https://net5.ton.dev/'
  ]

  # MAINNET_BASE_URL = 'main.ton.dev' changed to
  MAINNET_BASE_URLS = [
      'https://main2.ton.dev/',
      'https://main3.ton.dev/',
      'https://main4.ton.dev/'
  ]
  ```

  If you are using `DEVNET_BASE_URL` or `MAINNET_BASE_URL` somewhere, please set/update
  your client `NetworkConfig.endpoints` with new set of urls.

## Version 1.17.0.1

- Minimum `Python` version increased to `3.7`;
- `AppObject`, `AppSigningBox`, `AppEncryptionBox`, `AppDebotBrowser` interfaces implementation.
  Can be found in `tonclient.objects`.
  Now you can create child class from any of `AppObject` classes, implement required methods,
  create instance of resulting class and pass it's `dispatcher` method instead of raw `callback`
  for SDK methods which require `AppObject` as callback.
  <br/>
  More info and usage examples can be found in `test/[test_crypto|test_async|test_debot]`

## Version 1.17.0.0

- Binaries updated to `1.17.0`;
- Changes `1.16.1` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1161--2021-06-16);
- Changes `1.17.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1170--2021-06-21);

## Version 1.16.0.0

- Binaries updated to `1.16.0`;
- Changes `1.15.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1150--2021-05-18);
- Changes `1.16.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1160--2021-05-25);

## Version 1.14.1.0

- Binaries updated to `1.14.1`;
- Changes `1.14.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1140--2021-04-28);
- Changes `1.14.1` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1141--2021-04-29);

## Version 1.13.0.0

- Binaries updated to `1.13.0`;
- Changes `1.13.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1130--2021-04-23);
- Bug fixed in `types.DecodedOutput.from_dict` method;
- Modules' types rechecked

## Version 1.12.0.0

- Binaries updated to `1.12.0`;
- Changes `1.12.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1120--2021-04-01)
  _**Has breaking changes in DeBot module**_

## Version 1.11.0.0

- Binaries updated to `1.11.0`;
- Changes `1.9.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#190-feb-19-2021)
- Changes `1.10.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1100--2021-03-04)
- Changes `1.11.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#1110--2021-03-05)

## Version 1.8.0.0

- Binaries updated to `1.8.0`;
- Changes `1.6.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#160-jan-29-2021)
- Changes `1.6.2` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#162-feb-3-2021)
- Changes `1.6.3` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#163-feb-4-2021)
- Changes `1.7.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#170-feb-9-2021)
- Changes `1.8.0` (https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md#180-feb-11-2021)

## Version 1.5.2.0

- Binaries updated to `1.5.2`;
- `net` module functions wait for `net.resume` call instead of returning error if
  called while the module is suspended.

## Version 1.5.1.0

- Binaries updated to `1.5.1`.
  See https://github.com/tonlabs/TON-SDK/blob/master/CHANGELOG.md for details.

## Version 1.5.0.0

- `reconnect_timeout` parameter in `NetworkConfig`;
- `endpoints` parameter in `NetworkConfig`. It contains the list of available server
  addresses to connect. SDK will use one them with the least connect time.
  `server_address` parameter is still supported but endpoints is prevailing;
- `net.fetch_endpoints` function to receive available endpoints from the server;
- `net.set_endpoints` function to set endpoints list for using on next reconnect;
- `ErrorCode` type for each module. See `types.[MODULE]ErrorCode`.

## Version 1.4.0.1

- Core improvement: using `concurrent.future` along with `asyncio.future` for response
  resolving

## Version 1.4.0.0

Fully reworked binding. Is breaking to previous versions.

- Response resolvers reimplemented (no while loops with responses);
- Generators removed, callbacks added.
  Each callback receives `response_data`, `response_type`, `loop` arguments.
  `loop` argument is not none only when working with `asyncio`;
- Request params and responses are objects of core `types` now.
  See https://github.com/tonlabs/TON-SDK/tree/master/docs and `tonclient.types` for more info;
- Methods' docstrings updated;
- Tests updated.
