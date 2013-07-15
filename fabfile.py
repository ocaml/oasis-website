# Fabric deploy/rollback handling of OASIS website.

from fabric.api import run, env, cd, prompt, local, put

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

def deploy_release(release_fn):
  run('rm -R "%s"' % HTDOCS_DN)
  with cd(TARGET_DIR):
    run('tar xzf "%s"' % release_fn)
    run('chmod -R g+w htdocs')

def deploy():
  release_fn=os.path.join(TARGET_DIR, 'htdocs-' + NOW_STR + '.tar.gz')
  release_local_fn=os.path.join(os.getcwd(),
                                'dist',
                                os.path.basename(release_fn))
  # Check we don't already have this version.
  run('! test -e "%s"' % release_fn)

  # Build local tarball.
  if os.path.exists('tmp'):
    local('rm -Rf tmp')
  local('mkdir tmp')
  if not os.path.exists(os.path.dirname(release_local_fn)):
    local('mkdir "%s"' % os.path.dirname(release_local_fn))
  local('cp -pR html tmp/htdocs')
  local('tar czf "%s" -C tmp htdocs' % release_local_fn)
  local('rm -Rf tmp')

  # Send data and deploy.
  put(release_local_fn, release_fn)
  deploy_release(release_fn)
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
    deploy_release(rollback_release_fn)
  else:
    print "No old releases."
