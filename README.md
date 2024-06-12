# FY-Project
Final Year University of Birmingham Computer Science Project
- Live app shutdown on or before 17th June.

# About Prominent Profiles
Prominent Profiles is a new way to explore and share diverse viewpoints of important figures*. Unlike traditional methods that categorise media sources on a spectrum of left to right-wing, we delve deeper with target-dependent sentiment analysis enabling us to assess the sentiment directed specifically towards each individual. Our unique approach identifies articles where a figure is mentioned in at least 20% of sentences, ensuring comprehensive coverage that goes beyond the surface-level implications of headlines. Each analysed article is added to the individual's profile on our platform, creating a rich, multidimensional view of their public perception.

* United Kingdom News mentions so mainly UK Politicans, Royals + Trump/Biden

# Acknowledgements / Inspiration

This undergraduate project was inspired by the NewsMTSC paper and made possible by the Python library created to complement its work: NewsSentiment. Thank you!

- Hamborg, F., & Donnay, K. (2021). NewsMTSC: (Multi-)Target-dependent Sentiment Classification in News Articles. Proceedings of the 16th Conference of the European Chapter of the Association for Computational Linguistics (EACL 2021), April. [https://www.aclweb.org/anthology/2021.eacl-main.243](https://www.aclweb.org/anthology/2021.eacl-main.243)

Additionaly, I would like to extend this to the MAD-TSC paper for its further work and datasets made avaliable:

- Dufraisse, E., et al. (2023). MAD-TSC: A Multilingual Aligned News Dataset for Target-dependent Sentiment Classification. Proceedings of the Annual Meeting of the Association for Computational Linguistics (ACL 2023). [https://aclanthology.org/2023.acl-long.461/](https://aclanthology.org/2023.acl-long.461/)

# Running Locally

The most straightforward way to run the code locally is without docker:

1. Create a Python virtual machine environment: `python3 -m venv env`
2. Clone the git repo: `git clone https://github.com/meeky37/FY-Project.git`
3. Change directory to the requirements file: `cd Django_App/prominent_profiles/` and then navigate to `requirements.txt`
4. Install required Python packages: `pip install -r requirements.txt`
5. Install a specific package without dependencies: `pip install newssentiment==1.1.25 --no-deps` (Note: Installing without dependencies to prevent unnecessary downgrade of torch, which on M1 Mac prevents 'mps' GPU use)
6. Make and apply migrations:    
   ```bash
   python manage.py makemigrations
   python manage.py migrate
7. Create a superuser for the Django admin: `python manage.py createsuperuser`
8. Run the Django development server with custom settings: `python manage.py runserver 8000 --settings=prominent_profiles.test_settings`
9. To run Bing API commands, source a key from Azure and add it to `config.py`.
10. Collect article data: `python manage.py collect_article_data`
11. Trigger the extract and NLP processes: `python manage.py scrape_articles_concurrent`
12. Populate BingEntity for visible entities: `python manage.py visible_entity_bing` (Entities must be set to visible = TRUE via the admin page or dbshell)
13. Explore and try out management jobs in `nlp_processor` and `profiles_app` by reading the 
docstrings and applying them to your analysed data.
14. Navigate to the Vue.js project directory from the git root: `cd Vue_js/prominent_profiles`
15. Install required front-end libraries: `npm install`
16. Set the API base URL: Set `API_BASE_URL = 'http://localhost:8000'` in the project configuration.
17. Serve the Vue.js application: `npm run serve`
18. Access the Django admin and Vue app: Typically, `localhost:8000/admin` will serve the Django admin interface, and `localhost:8080` will serve the Vue.js application, although ports may vary.

# Deployment

1. Create a GitHub repository (others may work but we use GitHub Actions, so this is the most compatible route with YAML files as is).
2. Set up Ubuntu web server on Digital Ocean using the most recent Docker and Ubuntu configuration provided with 8GB memory if you plan to scrape - you can resize down to 2GB once you have some data.
3. Generate SSH keys.
4. Store the private key as a secret in GitHub.
5. Add a database (base price) when prompted by Digital Ocean.
6. Obtain a domain name (e.g., Namecheap).
7. Set up a Zoho mail account using this domain.
8. Configure the DNS records using documentation provided by your domain and mail provider.
9. Create a GitHub Container Registry Personal Access Token (GHCR PAT).
10. Set the following in GitHub settings $\rightarrow$ Security $\rightarrow$ Secrets and Variables $\rightarrow$ Actions:

    - BING_API_KEY
    - CERTBOT_EMAIL
    - DB_HOST
    - DB_NAME
    - DB_PASSWORD
    - DB_PORT
    - DB_USER
    - DJANGO_DEBUG
    - DROPLET_HOST
    - DROPLET_PUBLIC_KEY
    - DROPLET_USER
    - EMAIL_PASSWORD
    - GHCR_PAT
    - GHCR_USERNAME
    - RUNNING_IN_DOCKER
    - SECRET_KEY
    - SSH_KNOWN_HOSTS
    - SSH_PRIVATE_KEY

11. (Clone locally if you wish) and make a commit.
12. The build, test and deploy CI/CD pipeline should trigger automatically.
13. Visit your domain name to check Vue.
14. Visit your domain name /admin to check Django.

# References / Packages

## Sentiment Analysis Data In
- BingSearchAPI: [https://www.microsoft.com/en-us/bing/apis/bing-web-search-api](https://www.microsoft.com/en-us/bing/apis/bing-news-search-api)
- urllib3: [https://pypi.org/project/urllib3/1.26.18/](https://pypi.org/project/urllib3/1.26.18/)
- trafilatura: [https://pypi.org/project/trafilatura/1.6.2/](https://pypi.org/project/trafilatura/1.6.2/)
- fastcoref: [https://pypi.org/project/fastcoref/2.1.6/](https://pypi.org/project/fastcoref/2.1.6/)
- spacy: [https://pypi.org/project/spacy/3.7.2/](https://pypi.org/project/spacy/3.7.2/)
- textblob: [https://pypi.org/project/textblob/0.17.1/](https://pypi.org/project/textblob/0.17.1/)
- nltk (dependency of textblob): [https://pypi.org/project/nltk/3.8.1/](https://pypi.org/project/nltk/3.8.1/)
- intervalTree: [https://pypi.org/project/intervaltree/3.1.0/](https://pypi.org/project/intervaltree/3.1.0/)
- torch: [https://pypi.org/project/torch/2.1.0/](https://pypi.org/project/torch/2.1.0/)
- newsSentiment: [https://pypi.org/project/NewsSentiment/1.2.25/](https://pypi.org/project/NewsSentiment/1.2.25/)


## Article Duplicate Detection
- lexicalrichness: [https://pypi.org/project/lexicalrichness/0.5.1/](https://pypi.org/project/lexicalrichness/0.5.1/)
- ppdeep: [https://pypi.org/project/ppdeep/20200505/](https://pypi.org/project/ppdeep/20200505/)
- itertools.product (Python standard library): [https://docs.python.org/3/library/itertools.html#itertools.product](https://docs.python.org/3/library/itertools.html#itertools.product)



## Article/Profile Additional Data (pictures, descriptions)
- beautifulsoup4: [https://pypi.org/project/beautifulsoup4/4.12.2/](https://pypi.org/project/beautifulsoup4/4.12.2/)
- BingEntitySearchAPI: [https://www.microsoft.com/en-us/bing/apis/bing-entity-search-api](https://www.microsoft.com/en-us/bing/apis/bing-entity-search-api)


### Other packages / dependencies of above
- aiofiles: [https://pypi.org/project/aiofiles/22.1.0/](https://pypi.org/project/aiofiles/22.1.0/)
- aiosqlite: [https://pypi.org/project/aiosqlite/0.18.0/](https://pypi.org/project/aiosqlite/0.18.0/)
- anyio: [https://pypi.org/project/anyio/3.5.0/](https://pypi.org/project/anyio/3.5.0/)
- argon2-cffi: [https://pypi.org/project/argon2-cffi/21.3.0/](https://pypi.org/project/argon2-cffi/21.3.0/)
- attrs: [https://pypi.org/project/attrs/23.1.0/](https://pypi.org/project/attrs/23.1.0/)
- Babel: [https://pypi.org/project/Babel/2.11.0/](https://pypi.org/project/Babel/2.11.0/)
- bleach: [https://pypi.org/project/bleach/4.1.0/](https://pypi.org/project/bleach/4.1.0/)
- cffi: [https://pypi.org/project/cffi/1.15.1/](https://pypi.org/project/cffi/1.15.1/)
- cryptography: [https://pypi.org/project/cryptography/41.0.3/](https://pypi.org/project/cryptography/41.0.3/)
- FuzzyWuzzy: [https://pypi.org/project/FuzzyWuzzy/0.18.0/](https://pypi.org/project/FuzzyWuzzy/0.18.0/)
- gunicorn: [https://pypi.org/project/gunicorn/20.0.4/](https://pypi.org/project/gunicorn/20.0.4/)
- idna: [https://pypi.org/project/idna/3.4/](https://pypi.org/project/idna/3.4/)
- importlib-metadata: [https://pypi.org/project/importlib-metadata/6.0.0/](https://pypi.org/project/importlib-metadata/6.0.0/)
- Jinja2: [https://pypi.org/project/Jinja2/3.1.2/](https://pypi.org/project/Jinja2/3.1.2/)
- json5: [https://pypi.org/project/json5/0.9.6/](https://pypi.org/project/json5/0.9.6/)
- jsonschema: [https://pypi.org/project/jsonschema/4.19.2/](https://pypi.org/project/jsonschema/4.19.2/)
- MarkupSafe: [https://pypi.org/project/MarkupSafe/2.1.1/](https://pypi.org/project/MarkupSafe/2.1.1/)
- Pillow: [https://pypi.org/project/Pillow/10.1.0/](https://pypi.org/project/Pillow/10.1.0/)
- prometheus-client: [https://pypi.org/project/prometheus-client/0.14.1/](https://pypi.org/project/prometheus-client/0.14.1/)
- psutil: [https://pypi.org/project/psutil/5.9.0/](https://pypi.org/project/psutil/5.9.0/)
- Pygments: [https://pypi.org/project/Pygments/2.15.1/](https://pypi.org/project/Pygments/2.15.1/)
- PyJWT: [https://pypi.org/project/PyJWT/2.8.0/](https://pypi.org/project/PyJWT/2.8.0/)
- pyOpenSSL: [https://pypi.org/project/pyOpenSSL/23.2.0/](https://pypi.org/project/pyOpenSSL/23.2.0/)
- pyparsing: [https://pypi.org/project/pyparsing/3.1.1/](https://pypi.org/project/pyparsing/3.1.1/)
- pyrsistent: [https://pypi.org/project/pyrsistent/0.18.0/](https://pypi.org/project/pyrsistent/0.18.0/)
- python-dateutil: [https://pypi.org/project/python-dateutil/2.8.2/](https://pypi.org/project/python-dateutil/2.8.2/)
- pytz: [https://pypi.org/project/pytz/2023.3.post1/](https://pypi.org/project/pytz/2023.3.post1/)
- requests: [https://pypi.org/project/requests/2.31.0/](https://pypi.org/project/requests/2.31.0/)
- sqlparse: [https://pypi.org/project/sqlparse/0.4.4/](https://pypi.org/project/sqlparse/0.4.4/)
- tqdm: [https://pypi.org/project/tqdm/4.66.1/](https://pypi.org/project/tqdm/4.66.1/)
- psycopg2-binary: [https://pypi.org/project/psycopg2-binary/2.9.9/](https://pypi.org/project/psycopg2-binary/2.9.9/)
- rapidfuzz: [https://pypi.org/project/rapidfuzz/3.6.1/](https://pypi.org/project/rapidfuzz/3.6.1/)
- jsonlines: [https://pypi.org/project/jsonlines/4.0.0/](https://pypi.org/project/jsonlines/4.0.0/)
- numpy: [https://pypi.org/project/numpy/1.24.4/](https://pypi.org/project/numpy/1.24.4/)
- imbalanced-learn: [https://pypi.org/project/imbalanced-learn/0.11.0/](https://pypi.org/project/imbalanced-learn/0.11.0/)
- networkx: [https://pypi.org/project/networkx/3.1/](https://pypi.org/project/networkx/3.1/)
- openpyxl: [https://pypi.org/project/openpyxl/3.1.2/](https://pypi.org/project/openpyxl/3.1.2/)
- pandas: [https://pypi.org/project/pandas/2.0.3/](https://pypi.org/project/pandas/2.0.3/)
- regex: [https://pypi.org/project/regex/2023.10.3/](https://pypi.org/project/regex/2023.10.3/)
- sacremoses: [https://pypi.org/project/sacremoses/0.1.1/](https://pypi.org/project/sacremoses/0.1.1/)
- scikit-learn: [https://pypi.org/project/scikit-learn/1.3.2/](https://pypi.org/project/scikit-learn/1.3.2/)
- tabulate: [https://pypi.org/project/tabulate/0.9.0/](https://pypi.org/project/tabulate/0.9.0/)
- transformers: [https://pypi.org/project/transformers/4.24.0/](https://pypi.org/project/transformers/4.24.0/)
- matplotlib: [https://pypi.org/project/matplotlib/3.7.4/](https://pypi.org/project/matplotlib/3.7.4/)

- Django: [https://pypi.org/project/Django/4.2.10/](https://pypi.org/project/Django/4.2.10/)
- django-cors-headers: [https://pypi.org/project/django-cors-headers/4.3.1/](https://pypi.org/project/django-cors-headers/4.3.1/)
- djangorestframework: [https://pypi.org/project/djangorestframework/3.14.0/](https://pypi.org/project/djangorestframework/3.14.0/)
- djangorestframework-simplejwt: [https://pypi.org/project/djangorestframework-simplejwt/5.3.1/](https://pypi.org/project/djangorestframework-simplejwt/5.3.1/)
- django-admin-shortcuts: [https://pypi.org/project/django-admin-shortcuts/2.1.1/](https://pypi.org/project/django-admin-shortcuts/2.1.1/)
- django-admin-sortable2: [https://pypi.org/project/django-admin-sortable2/2.1.10/](https://pypi.org/project/django-admin-sortable2/2.1.10/)
- django-extensions: [https://pypi.org/project/django-extensions/3.2.3/](https://pypi.org/project/django-extensions/3.2.3/)
- django-rest-passwordreset: [https://pypi.org/project/django-rest-passwordreset/1.4.0/](https://pypi.org/project/django-rest-passwordreset/1.4.0/)
- celery: [https://pypi.org/project/celery/5.3.6/](https://pypi.org/project/celery/5.3.6/)

