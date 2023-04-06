import crontab, getpass, os, uuid
from .config import read_config, write_config


def add(plugin, task, freq):
    cron = crontab.CronTab(user=getpass.getuser())
    task_name = f'{plugin}|{task}'

    # добавить задачу в конфиг
    task_id = str(uuid.uuid4())
    config = read_config('config.ini')
    config['Tasks'][task_name] = task_id
    write_config(config, 'config.ini')

    # очистить старые задачи с таким же именем
    for job in cron:
        if job.comment == task_name:
            cron.remove(job)

    # сделать посекундное ожидание
    sec = 0
    seconds = []
    while not sec or sec % 60:
        seconds.append(sec)
        sec += freq

    cronstart_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "cronstart.py")
    for i in seconds:
        command = f'sleep {i}; python3 "{cronstart_path}" "{task_id}"'
        tab = cron.new(comment=task_name, command=command)
        tab.minute.every(seconds[-1] // 60 + 1)
    cron.write()


def remove(plugin, task):
    cron = crontab.CronTab(user=getpass.getuser())
    task_name = f'{plugin}|{task}'
    for job in cron:
        if job.comment == task_name:
            cron.remove(job)
    cron.write()

    # убрать задачу из конфигa
    config = read_config('config.ini')
    del config['Tasks'][task_name]
    write_config(config, 'config.ini')


def get():
    config = read_config('config.ini')
    tasks = config.items('Tasks')
    return list(map(lambda x: x[0].split('|')[1], tasks))
