# Fabric deploy/rollback handling of OASIS website.

from fabric.api import run, env, cd, prompt
from fabric.contrib.project import rsync_project

import datetime
import os

NOW = datetime.datetime.now()
NOW_STR = NOW.strftime('%Y-%m-%d-%H%M')
MAX_AGE = datetime.timedelta(days=10)
TARGET_DIR = '/home/groups/oasis'
HTDOCS_DN=os.path.join(TARGET_DIR, 'htdocs')

env.hosts = ['ssh.ocamlcore.org']
env.use_ssh_config = True

def releases():
  """List releases and their date."""
  releases = run('ls -1 %s' % (os.path.join(TARGET_DIR,
                                            'htdocs-*.tar.gz'))).split()
  date_releases = []
  for release in releases:
    date = datetime.datetime.strptime(os.path.basename(release),
                                      'htdocs-%Y-%m-%d-%H%M.tar.gz')
    date_releases.append((date, release))

  return date_releases

def cleanup():
  """Remove old releases."""
  for (date, release) in releases():
    if NOW - date > MAX_AGE:
      run ('rm "%s"' % release)

def check_short_release_names(short_names, choice):
  if choice in short_names:
    return choice
  else:
    raise Error('"%s" is not a release.' % choice)

def deploy():
  release_fn=os.path.join(TARGET_DIR, 'htdocs-' + NOW_STR + '.tar.gz')
  # Check we don't already have this version.
  run('! test -e "%s"' % release_fn)
  # Send data.
  rsync_project(local_dir='html/', remote_dir=HTDOCS_DN + '/',
                delete=True, extra_opts='--omit-dir-times --no-perms')
  # Do a backup for rollback.
  with cd(TARGET_DIR):
    run('tar czf "%s" htdocs' % release_fn)
  cleanup()

def rollback():
  all_releases = sorted(releases(), cmp=lambda (d1, _1),(d2, _2): cmp(d2, d1))
  if len(all_releases) > 1:
    print "Available releases:"
    short_names = dict()
    latest = None
    for _, release in all_releases:
      basename = os.path.basename(release).replace('.tar.gz','')
      if not latest:
        latest = basename
      short_names[basename] = release
      print basename
    rollback_to_release = prompt("Rollback to which release?",
                                 default=latest,
                                 validate=lambda r: check_short_release_names(short_names, r))
    rollback_release_fn = short_names[rollback_to_release]
    run('rm -R "%s"' % HTDOCS_DN)
    with cd(TARGET_DIR):
      run('tar xzf "%s"' % rollback_release_fn)
  else:
    print "No old releases."
