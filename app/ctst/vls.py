from os import getenv
from dotenv import load_dotenv

load_dotenv()

__OPERATION_JOIN = 1
__OPERATION_EXIT = 2
__OPERATION_AFK = 3
__OPERATION_UNAFK = 4
__OPERATION_MOVE = 5
__OPERATION_MUTE = 6
__OPERATION_UNMUTE = 7

__USER_BASIC_INCOME = float(getenv('WALLET_INCOME'))
__COIN_ROUND_INT_VALUE = int(getenv('COIN_ROUND'))
__BALANCES_TOP_LIMIT = int(getenv('BALANCES_TOP_LIMIT'))

__REASON_ACTIVITY = 0
__REASON_ADMIN_CHANGING = 1
__REASON_SYSTEM_CHANGING = 2
__REASON_USER_TRANSACTION = 3

if (__cl_host_possible_prod := getenv('CLICKHOUSE_HOST_DEV')) is not None:
    __CLICKHOUSE_HOST = __cl_host_possible_prod
elif (__cl_host_possible_dev := getenv('CLICKHOUSE_HOST_PROD')) is not None:
    __CLICKHOUSE_HOST = __cl_host_possible_dev
else:
    print('Error in find clickhouse connect host string.')
    exit(1)
