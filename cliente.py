from requests import get, patch

r = get("http://127.0.0.1:1621/contas/12345").json()

print(r['cont'])

r = patch("http://127.0.0.1:1621/contas/12345/deposito?valor=100.0").json()

print(r['resp'])

r = get("http://127.0.0.1:1621/contas/12345").json()

print(r['cont'])