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
