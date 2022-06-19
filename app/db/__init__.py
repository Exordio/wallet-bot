import discord

from clickhouse_driver import Client as ChClient
from ctst.vls import __USER_BASIC_INCOME, __OPERATION_JOIN, __OPERATION_MOVE, __OPERATION_EXIT, __OPERATION_MUTE, \
    __OPERATION_UNMUTE, __OPERATION_AFK, __REASON_ACTIVITY, __OPERATION_UNAFK, __BALANCES_TOP_LIMIT, __CLICKHOUSE_HOST

cl = ChClient(host=__CLICKHOUSE_HOST)


def clickhouse_init():
    print('Checking and creating tables if needed')

    try:
        cl.execute('create database if not exists discord')

        cl.execute('''
        create table if not exists discord.activity
    (
        user_id    UInt64,
        operation  UInt8,
        channel_id UInt64,
        create_at  DateTime default now()
    )
        engine = MergeTree order by create_at
            SETTINGS index_granularity = 8192;
        ''')

        cl.execute('''
        create table if not exists discord.wallet
    (
        user_id   UInt64,
        diff      Float32,
        reason    UInt8,
        create_at DateTime default now()
    )
        engine = MergeTree ORDER BY create_at
            SETTINGS index_granularity = 8192;
        ''')
    except Exception as err:
        print('Clickhouse problem: ')
        print(err)
        exit(1)

    print('Clickhouse init! ')


async def clh_ex_activity(payload):
    cl.execute('insert into discord.activity (user_id, operation, channel_id) values ', payload, types_check=True)


async def on_user_join(member, after):
    await clh_ex_activity([(member.id, __OPERATION_JOIN, after.channel.id)])


async def on_user_move(member, after):
    await clh_ex_activity([(member.id, __OPERATION_MOVE, after.channel.id)])


async def on_user_exit(member, before):
    await clh_ex_activity([(member.id, __OPERATION_EXIT, before.channel.id)])
    income = await user_calculate_income(member)
    if income is None:
        return 'UNF'
    else:
        await insert_user_income(member, income)
        return 'OK'


async def on_user_mute(member, after):
    await clh_ex_activity([(member.id, __OPERATION_MUTE, after.channel.id)])
    income = await user_calculate_income(member)
    if income is None:
        return 'UNF'
    else:
        await insert_user_income(member, income)
        return 'OK'


async def on_user_unmute(member, after):
    await clh_ex_activity([(member.id, __OPERATION_UNMUTE, after.channel.id)])


async def on_user_afk(member, after):
    await clh_ex_activity([(member.id, __OPERATION_AFK, after.channel.id)])
    income = await user_calculate_income(member)
    if income is None:
        return 'UNF'
    else:
        await insert_user_income(member, income)
        return 'OK'


async def on_user_unafk(member, after):
    await clh_ex_activity([(member.id, __OPERATION_UNAFK, after.channel.id)])


def as_dict(columns, result):
    return [{columns[result_el_idx][0]: result_el[result_el_idx] for result_el_idx in range(len(result_el))} for
            result_el in result]


async def insert_user_income(member, income):
    payload = [(member.id, income, __REASON_ACTIVITY)]
    cl.execute('insert into discord.wallet (user_id, diff, reason) values ', payload, types_check=True)


async def user_calculate_income(member):
    sql = ''' 
        with (
        select datedate as left_operation
        from discord.activity as a
                 join (
            select user_id, max(create_at) AS datedate
            from discord.activity
            where discord.activity.create_at <= now()
              and operation in (%(operation_join)i, %(operation_unafk)i, %(operation_unmute)i)
              and user_id = %(user_id)i
            group by user_id
            ) as d on d.user_id = a.user_id and d.datedate = a.create_at
        where operation in (%(operation_join)i, %(operation_unafk)i, %(operation_unmute)i)) as left_shitty_her,
        (select datedate as right_operation
         from discord.activity as a
                  join (
             select user_id, if(any(create_at) != anyLast(create_at), null, anyLast(create_at)) AS datedate
             from discord.activity
             where discord.activity.create_at >= left_shitty_her
               and operation in (%(operation_exit)i, %(operation_afk)i, %(operation_mute)i)
               and user_id = %(user_id)i
             group by user_id
             ) as d on d.user_id = a.user_id and d.datedate = a.create_at
         where operation in (%(operation_exit)i, %(operation_afk)i, %(operation_mute)i)) as right_shitty_her
    select dateDiff(second, left_shitty_her, right_shitty_her) as player_time_in_channel
    '''
    result = cl.execute(sql,
                        {
                            'user_id': member.id,
                            'operation_join': __OPERATION_JOIN,
                            'operation_exit': __OPERATION_EXIT,
                            'operation_unafk': __OPERATION_UNAFK,
                            'operation_unmute': __OPERATION_UNMUTE,
                            'operation_afk': __OPERATION_AFK,
                            'operation_mute': __OPERATION_MUTE
                        },
                        types_check=True)

    user_second_time_delta = result[0][0]

    return user_second_time_delta if user_second_time_delta is None else user_second_time_delta * __USER_BASIC_INCOME


async def get_user_balance(member):
    sql = '''
    select sum(diff)
    from discord.wallet
    where user_id = %(user_id)i
    group by user_id
    '''

    result = cl.execute(sql, {'user_id': member.id}, types_check=True)
    try:
        user_balance = result[0][0]
    except IndexError:
        user_balance = 0
    return user_balance


async def append_user_balance(member: discord.Member, value: float, reason: int):
    sql = '''
    insert into discord.wallet (user_id, diff, reason)
    values (%(user_id)i, %(value)f, %(reason)i)
    '''
    cl.execute(sql, {'user_id': member.id, 'value': value, 'reason': reason}, types_check=True)


async def perm_change_balance(member, value, reason):
    """Перманентная смена баланса."""
    await discard_user_balance(member, reason)
    await append_user_balance(member, value, reason)


async def get_users_balance_top():
    sql = 'select user_id, sum(diff) bal from discord.wallet group by user_id order by bal desc limit %(lm)i '
    result, cols = cl.execute(sql, {'lm': __BALANCES_TOP_LIMIT}, with_column_types=True, types_check=True)

    shiny = as_dict(cols, result)

    return shiny


async def discard_user_balance(member, reason):
    user_balance = await get_user_balance(member)
    shift_user_balance = - user_balance
    await append_user_balance(member, shift_user_balance, reason)


async def truncate_wallets():
    sql = 'truncate table discord.wallet'
    cl.execute(sql)


async def truncate_activity():
    sql = 'truncate table discord.activity'
    cl.execute(sql)


async def truncate_all():
    await truncate_activity()
    await truncate_wallets()
