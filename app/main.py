from os import getenv

from db import clickhouse_init
from core import client
from ctrl.evnt import *
from ctrl.cmd import *
from ctrl.evnt import *

clickhouse_init()


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print(r'''
            |||| CREATED BY EXORD v.1.0 ||||
                      .---.  .---.
                    .' / )))^^\\  )
                   (> (( e Va  )   )
                   [_3 )   <   ((   )
                   __(/  _ B>.__) (  )
                  /          \ (    ) )
                 / .V      (\ \( ( ( (\
                / / ( .)  .) \ \)/ \ ) \
              ,--.\_/     /   \ / /     `.__
             /    \.'\ -  \__  / /._/       `''-.
            /  .^   "/## .'  \/ / \ \            `.   .-
           /  / \    {i}(    / / \__>\   c  ##     \.'  \
          / .'   \___.-._>._/ /\      `.    #\\     \  / `""`-..._-._
      _.-' /             __/ /  \n-     '-.____\      /_______________>
      c___/             //_.' `./  3            \    /
                               ( /'              `--'
                                `
    ''')


client.run(getenv('BOT_TOKEN'), reconnect=True)
