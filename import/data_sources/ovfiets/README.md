## About OvFiets

- Scraper for http://fiets.openov.nl/ the status of available rental bikes at train stations
- Raw data is saved as is for history persistency
- Raw data is cleaned and copied to another model.
- Django REST api views the cleaned data.
- Django model needs to be in sync with the imported model

## Instructions OvFiets

### Move to import root
```
cd ..
```
### Set python path

```
export PYTHONPATH=.
```

### Create models

```
python data_sources/ovfiets/models.py
```

### Load wfs data (neighbourhoods)

```
python load_wfs_postgres.py https://map.data.amsterdam.nl/maps/gebieden stadsdeel,buurt_simple 4326 --db externaldata
```

### Import api instance
```
python data_sources/ovfiets/slurp.py
```

### Cleanup and copy to model
```
python data_sources/ovfiets/copy_to_model.py
```

### Link neighbourhoods
```
python data_sources/ovfiets/copy_to_model.py --link_areas
```