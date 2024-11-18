# for start
API for warehause for work with products and orders
```
git clone https://github.com/DenisKadyrov/warehause_management.git
cd warehause_management
pip install -r requirements.txt
export PYTHONPATH=$PWD
docker-compose up -d
alembic upgrade head
python app/main.py
# for test
pytest
```
