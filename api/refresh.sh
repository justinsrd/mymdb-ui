overall_start=$(date +%s)

source .env.droplet
echo 'Sourced environment variables'

if [ "$1" = 'renew' ]
then
  rm -r title*
  echo 'Removed old data files'
  download_files_start=$(date +%s)
  python3 setup.py
  download_files_end=$(date +%s)
  echo 'Downloaded new data files --' $((download_files_end-download_files_start)) 'seconds'
fi

ingestion_start=$(date +%s)
python3 ingestion.py
ingestion_end=$(date +%s)
echo 'Add files to database -- ' $((ingestion_end-ingestion_start)) 'seconds'

overall_end=$(date +%s)
echo 'Overall took' $((overall_end-overall_start)) 'seconds'


