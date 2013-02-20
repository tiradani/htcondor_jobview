
import os
import sys
import tempfile
import ConfigParser

import rrdtool

import htcondor_jobview.jobs
import htcondor_jobview.cluster_summary

def get_rrd_name(cp, plot):
    return os.path.join(cp.get("jobview", "db_directory"), "%s.rrd" % plot)

def create_rrd(cp, plot):
    path = get_rrd_name(cp, plot)
    if plot == "jobs":
        rrdtool.create(path,
            "--step", "180",
            "DS:running:GAUGE:360:U:U",
            "DS:pending:GAUGE:360:U:U",
            "RRA:AVERAGE:0.5:1:1000",
            "RRA:MIN:0.5:20:8760",
            "RRA:MAX:0.5:20:8760",
            "RRA:AVERAGE:0.5:20:8760",
            )
    else:
        rrdtool.create(path,
            "--step", "180",
            "DS:total:GAUGE:360:U:U",
            "DS:free:GAUGE:360:U:U",
            "RRA:AVERAGE:0.5:1:1000",
            "RRA:MIN:0.5:20:8760",
            "RRA:MAX:0.5:20:8760",
            "RRA:AVERAGE:0.5:20:8760",
            )

def update_rrd(cp):
    jobs_tables, group_tables, schedd_tables, user_tables = \
        htcondor_jobview.jobs.summarize_jobs(cp)

    path = get_rrd_name(cp, "jobs")
    if not os.path.exists(path):
        create_rrd(cp, "jobs")

    rrdtool.update(path, "N:%d:%d" % (jobs_tables['running'], jobs_tables['pending']))

    total, free = htcondor_jobview.cluster_summary.get_cpu_slots(cp)
    path = get_rrd_name(cp, "cluster")

    path = get_rrd_name(cp, "cluster")
    if not os.path.exists(path):
        create_rrd(cp, "cluster")

    rrdtool.update(path, "N:%d:%d" % (total, free))

def graph_rrd(cp, plot, interval):
    if interval == "hourly":
        rrd_interval = "h"
    elif interval == "daily":
        rrd_interval = "d"
    elif interval == "monthly":
        rrd_interval = "m"
    elif interval == "yearly":
        rrd_interval = "y"
    else:
        raise ValueError("Unknown interval: %s" % interval)

    fd, path = tempfile.mkstemp(".png")
    if plot == "jobs":
        rrdtool.graph(path,
            "--imgformat", "PNG",
            "--width", "480",
            "--start", "-1%s" % rrd_interval,
            "--vertical-label", "Jobs",
            "--lower-limit", "0",
            "DEF:running=%s:running:AVERAGE" % get_rrd_name(cp, plot),
            "DEF:pending=%s:pending:AVERAGE" % get_rrd_name(cp, plot),
            "LINE1:running#0000FF:Running",
            "LINE2:pending#00FF00:Pending",
            "COMMENT:%s" % cp.get("jobview", "site_name"),
            "COMMENT:\\n",
            "COMMENT:           max     avg      cur\\n",
            "COMMENT:Running ",
            "GPRINT:running:MAX:%-6.0lf",
            "GPRINT:running:AVERAGE:%-6.0lf",
            "GPRINT:running:LAST:%-6.0lf",
            "COMMENT:\\n",
            "COMMENT:Pending ",
            "GPRINT:pending:MAX:%-6.0lf",
            "GPRINT:pending:AVERAGE:%-6.0lf",
            "GPRINT:pending:LAST:%-6.0lf\\n",
            )
    elif plot == "cluster":
        rrdtool.graph(path,
            "--imgformat", "PNG",
            "--width", "480",
            "--start", "-1%s" % rrd_interval,
            "--vertical-label", "Jobs",
            "--lower-limit", "0",
            "DEF:total=%s:total:AVERAGE" % get_rrd_name(cp, plot),
            "DEF:free=%s:free:AVERAGE" % get_rrd_name(cp, plot),
            "LINE1:total#0000FF:Total",
            "LINE2:free#00FF00:Free",
            "COMMENT:%s" % cp.get("jobview", "site_name"),
            "COMMENT:\\n",
            "COMMENT:         max     avg      cur\\n",
            "COMMENT:Total ",
            "GPRINT:total:MAX:%-6.0lf",
            "GPRINT:total:AVERAGE:%-6.0lf",
            "GPRINT:total:LAST:%-6.0lf",
            "COMMENT:\\n",
            "COMMENT:Free   ",
            "GPRINT:free:MAX:%-6.0lf",
            "GPRINT:free:AVERAGE:%-6.0lf",
            "GPRINT:free:LAST:%-6.0lf\\n",
            )

    os.unlink(path)

    return os.fdopen(fd).read()

if __name__ == '__main__':
    cp = ConfigParser.ConfigParser()
    cp.read(sys.argv[1])
    update_rrd(cp)
    print graph_rrd(cp, "jobs", "hourly")

