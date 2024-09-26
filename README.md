# for start
```
git clone https://github.com/DenisKadyrov/warehause_management.git
cd warehause_management
pip install -r requirements.txt
export PYTHONPATH=$PWD
docker-compose up
alembic upgrade head'
python app/main.py
# for test
pytest
```