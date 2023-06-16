
DIRNAME=`dirname $0`
pid_name=`uuidgen`
if [ -z $1 ]; then
    echo 'not file_name'
else
    python_file=$1
    stop_file_name='stop_stomp.sh'
    PY3=`which python3`
    sudo start-stop-daemon -S -b -x $PY3 -d $DIRNAME -m -v -p /run/$pid_name.pid -- ./$python_file
    echo -e sudo start-stop-daemon -K -p /run/`echo $pid_name`.pid '\n'sudo rm `echo $stop_file_name` '\n'sudo rm /run/$pid_name.pid > $stop_file_name
fi
