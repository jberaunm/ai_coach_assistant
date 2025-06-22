from stravalib import Client

client = Client()

token_response = client.exchange_code_for_token(
    client_id=163079, client_secret="d49c2f09e6f96af17f7fa4eb254b933cee64bc75", code="9e7995d9fcc3c16939be4039c81cccdd3b1fb335"
)
# The token response above contains both an access_token and a refresh token.
access_token = token_response["access_token"]
refresh_token = token_response["refresh_token"]  # You'll need this in 6 hours

print(access_token)
print(refresh_token)