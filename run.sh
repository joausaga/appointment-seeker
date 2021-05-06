#!/bin/bash


PROJECT_DIR=`pwd`

for arg in "$@"
do
    case $arg in
        --project_dir=*)
        PROJECT_DIR="${arg#*=}"
        shift # Remove --project_dir= from processing
        ;;
    esac
done

LOG_DIR="${PROJECT_DIR}/log"

if [[ ! -d $LOG_DIR ]]
then
    `mkdir $LOG_DIR`
fi

LOGFILE=${LOG_DIR}/run.log
ERRORFILE=${LOG_DIR}/run.err
ENV_DIR="/Users/jorgesaldivar/.pyenv/versions/appointment-seeker-env"
error=0

####
# Print a starting message
####
running_date=`date '+%Y-%m-%d %H:%M:%S'`
printf "\n\n#####\nStarting to process tweets at ${running_date}\n######\n\n" >> $LOGFILE

####
# Go to project directory
####
echo "Changing directory to ${PROJECT_DIR}..." >> $LOGFILE 2>> $ERRORFILE
cd $PROJECT_DIR

####
# Active virtual environment
####
if [ $? -eq 0 ]
then
    echo "Activating virtual environment..." >> $LOGFILE 
    source $ENV_DIR/bin/activate 2>> $ERRORFILE
    #pyenv activate $ENV_NAME 2>> $ERRORFILE
else
    error=1
fi

####
# Run script
####
if [ $? -eq 0 ]
then
    echo "Running seeker..." >> $LOGFILE 
    python seeker.py >> $LOGFILE 2>> $ERRORFILE
else
    error=1
fi


if [[ $? -eq 0 ]] && [[ $error -eq 0 ]]
then
    echo "Process has finished successfully"
    echo "For more information, check $LOGFILE"
else
    echo "There was an error running the process"
    echo "For more information, check $ERRORFILE"
fi

exit $error
