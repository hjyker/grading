from invoke import run
from fabric2 import Connection, task

HOST = '162.14.74.170'
USER = 'ubuntu'
REMOTE_WORK_DIR = '/data/deploy_app/grading'

cnn = Connection(
    host=HOST,
    user=USER,
    connect_kwargs={
        'key_filename': ['/Users/hjyker/.ssh/id_work_ed25519'],
    })


def rsync_project():
    run(f'rsync -auvz -e "ssh -i ~/.ssh/id_work_ed25519" --exclude-from="./deploy/rsync.exclude.list" ./ {USER}@{HOST}:{REMOTE_WORK_DIR}')

def restart(c):
    c.run(f'cd {REMOTE_WORK_DIR}')
    c.run('sudo docker-compose up -d prod_service')

@task
def deploy_prod(c):
    rsync_project()
    # restart(c)
