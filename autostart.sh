#! /bin/sh
# /etc/init.d/weathermonitor

### BEGIN INIT INFO
# Provides:          weathermonitor
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start/stop WeatherMonitor in screen called 'weather'
# Description:       WeatherMonitor is a wunderground monitoring web app at port 5002. It is running in the user 'pi' screen 'weather'
### END INIT INFO

# If you want a command to always run, put it here

# Carry out specific functions when asked to by the system
case "$1" in
  start)
    echo "Starting weathermonitor"
    # run application you want to start
    sudo -u pi /media/drive1/development/bin/WeatherMonitor/runserver
    ;;
  stop)
    echo "Stopping weathermonitor"
    # kill application you want to stop
    sudo -u pi screen -S weather -p 0 -X quit
    ;;
  *)
    echo "Usage: /etc/init.d/weathermonitor {start|stop}"
    exit 1
    ;;
esac

exit 0 