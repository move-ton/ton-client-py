
class TonContract(object):
    abi = None # json
    tvm = None # base64
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

wallet = TonContract(abi={
    "ABI version": 2,
    "header": ["time"],
    "functions": [
        {
            "name": "constructor",
            "inputs": [
            ],
            "outputs": [
            ]
        },
        {
            "name": "sendTransaction",
            "inputs": [
                {"name":"dest","type":"address"},
                {"name":"value","type":"uint128"},
                {"name":"bounce","type":"bool"}
            ],
            "outputs": [
            ]
        }
    ],
    "data": [
    ],
    "events": [
    ]
}, tvm = 'te6ccgECEAEAAi8AAgE0AwEBAcACAEPQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAib/APSkICLAAZL0oOGK7VNYMPShBgQBCvSkIPShBQAAAgEgCgcBAv8IAf5/Ie1E0CDXScIBjhTT/9M/0wDXC//4an/4Yfhm+GP4Yo4b9AVw+GpwAYBA9A7yvdcL//hicPhjcPhmf/hh4tMAAY4SgQIA1xgg+QFY+EIg+GX5EPKo3tM/AY4e+EMhuSCfMCD4I4ED6KiCCBt3QKC53pL4Y+CANPI02NMfAfABCQAO+EdukvI83gIBIAwLAN29Rar5/8ILdHHnaiaBBrpOEAxwpp/+mf6YBrhf/8NT/8MPwzfDH8MUcN+gK4fDU4AMAgegd5XuuF//wxOHwxuHwzP/ww8W98I3k5uPwzaPwAfCF8NXwhZGX//CHnhZ/8I2eFgHwlAOX/5PaqP/wzwCASAPDQHxuxXvk1+EFujhftRNDT/9M/0wDXC//4an/4Yfhm+GP4Yt76QNcNf5XU0dDTf9/XDACV1NHQ0gDf0fhFIG6SMHDe+Eq68uBk+AAhwgAglzAh+CdvELne8uBlISMiyM+FgMoAc89AzgH6AoBpz0DPgc+ByXD7AF8DwP+A4AOo4X+ELIy//4Q88LP/hGzwsA+EoBy//J7VTef/hnAGrdcCLQ1gIx0gAw3CHHAJDgIdcNH5LyPOFTEZDhwQQighD////9vLGS8jzgAfAB+EdukvI83g==')