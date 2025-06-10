from stravalib import Client

client = Client()

token_response = client.exchange_code_for_token(
    client_id=163079, client_secret="d49c2f09e6f96af17f7fa4eb254b933cee64bc75", code="14a4ebb0241b0629a6a06c115da839be23ba4a27"
)
# The token response above contains both an access_token and a refresh token.
access_token = token_response["access_token"]
refresh_token = token_response["refresh_token"]  # You'll need this in 6 hours

print(access_token)
print(refresh_token)