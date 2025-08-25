# Authentication & Account Discovery Tools

This folder contains tools for setting up OAuth authentication with the Google Ads API and discovering account hierarchies.

## Tools

### `generate_refresh_token.py`
**Purpose**: Generate OAuth2 refresh tokens for Google Ads API authentication.

**Usage**:
```bash
python generate_refresh_token.py --client-id YOUR_CLIENT_ID --client-secret YOUR_SECRET

# For headless environments (copy/paste flow)
python generate_refresh_token.py --client-id YOUR_CLIENT_ID --client-secret YOUR_SECRET --console
```

**Prerequisites**:
- Google Cloud Console project with OAuth client configured
- Google Ads API enabled in the project

**Output**: Prints the refresh token to stdout for use in `~/.google-ads.yaml`

### `list_accessible_customers.py`
**Purpose**: List all customer accounts accessible with your current OAuth credentials.

**Usage**:
```bash
python list_accessible_customers.py
```

**Output**:
- Shows accessible manager/customer resource names
- If login_customer_id is set, shows account hierarchy

**Example Output**:
```
Accessible manager/customer resource names:
 - customers/1234567890
 - customers/9876543210

Hierarchy under login_customer_id=1234567890:
 - 9876543210 | level=1 | name=Client Account | hidden=False
```

### `list_hierarchy_check_target.py`
**Purpose**: Search for a specific customer ID within account hierarchies (useful for debugging access issues).

**Usage**:
```bash
python list_hierarchy_check_target.py
```

**Configuration**: Edit the `TARGET` variable in the script to specify which customer ID to search for.

**Output**: Shows where the target customer ID appears in accessible hierarchies.

## Setup Workflow

### 1. Create OAuth Credentials
1. Go to Google Cloud Console → APIs & Services → Credentials
2. Create OAuth 2.0 Client ID (Desktop application)
3. Copy the client ID and client secret

### 2. Generate Refresh Token
```bash
python generate_refresh_token.py \
  --client-id "123456789.apps.googleusercontent.com" \
  --client-secret "your-client-secret"
```

### 3. Create Configuration File
Create `~/.google-ads.yaml`:
```yaml
developer_token: "YOUR_DEVELOPER_TOKEN"
client_id: "123456789.apps.googleusercontent.com"
client_secret: "your-client-secret" 
refresh_token: "the-refresh-token-from-step-2"
login_customer_id: "8630268244"  # Optional MCC ID
endpoint: googleads.googleapis.com
use_proto_plus: True
```

### 4. Verify Access
```bash
python list_accessible_customers.py
```

## Common Issues

### "No refresh token" Error
- Run `generate_refresh_token.py` first
- Ensure the refresh token is correctly copied to `~/.google-ads.yaml`

### "Customer not accessible" Error  
- Verify the customer ID exists in `list_accessible_customers.py` output
- Check if you need to set `login_customer_id` for MCC access
- Ensure your Google account has appropriate permissions

### "SERVICE_DISABLED" Error
- Enable Google Ads API in Google Cloud Console
- Wait a few minutes for propagation

### "Invalid credentials" Error
- Verify client_id and client_secret are correct
- Regenerate refresh token if OAuth client was recreated

## Dependencies

```bash
pip install google-ads google-auth-oauthlib
```

## Security Notes

- Keep your `~/.google-ads.yaml` file secure
- Never commit OAuth credentials to version control
- Refresh tokens don't expire but can be revoked
- Use different OAuth clients for different environments (dev/prod)