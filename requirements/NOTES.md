## When pip install fails on matplotlib

For when these fail:
```
pip install -r requirements/local.txt 
# or
pip install -r requirements/production.txt 
```

(1)  Go into "requirements/base.txt", comment out matplotlib and everything below:

```python
numpy>=1.8.1
#matplotlib==1.1.1
#pandas==0.14.0
```

(2)  Run pip install.  This will install the numpy package that matplotlib depends on.

```
pip install -r requirements/local.txt 
# or
pip install -r requirements/production.txt 
```

(3)  Uncomment out matplotlib and pandas.
```python
numpy>=1.8.1
matplotlib==1.1.1
pandas==0.14.0
```

(4) Re-run pip install--matplotlib should work now that numpy is installed
```
pip install -r requirements/local.txt 
# or
pip install -r requirements/production.txt 
```
