rm -r title*
echo 'Removed old data files'
source .env.local
echo 'Sourced environment variables'
python3 setup.py
echo 'Downloaded new data files'
python3 ingestion.py
echo 'Add files to database'