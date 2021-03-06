#!/usr/bin/python

from distutils.core import setup

setup(name='htcondor-jobview',
      version='0.4',
      description='Simple monitoring page for HTCondor',
      author='Brian Bockelman',
      author_email='bbockelm@cse.unl.edu',
      url='https://github.com/bbockelm/htcondor_jobview',
      packages=['htcondor_jobview'],
      package_dir = {'': 'src'},
      data_files=[('/etc', ['packaging/jobview.conf']),
                  ('/var/www/wsgi-scripts', ['packaging/htcondor-jobview.wsgi']),
                  ('/usr/share/htcondor-jobview/templates', ['templates/index.html']),
                  ('/etc/httpd/conf.d/', ['packaging/htcondor-jobview.conf']),
                  ('/etc/cron.d/', ['packaging/jobview.cron'])
                 ],
      scripts=["src/jobview-update"]
     )

