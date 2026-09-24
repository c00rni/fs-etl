# Financial statement ETL

This project aim to download all financial statement discorsure to the SEC.

## Update requirement.txt file

``` bash
pipreqs . --ignore .venv --force

## Generate Fernet key

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

## Configuration

Enviroment variables `$DATA_FOLDER` and `$DB_FOLDER` respectively persist downloaded fillings and mysql databases files. Ses volumes doivent donner des droit en ecriture a l'utilisateur du conteneur.

```bash
sudo chown -R 50000:0 <YOUR_LOCAL_FOLDER>
```

