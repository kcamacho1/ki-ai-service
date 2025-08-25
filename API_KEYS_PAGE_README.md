# API Keys Management Page

## Overview
The API Keys Management page is now a separate, dedicated page accessible via navigation from the main Ki Wellness AI Service dashboard.

## Features

### 🔑 API Key Management
- **Generate New Keys**: Create API keys with custom names and descriptions
- **View Existing Keys**: See all generated keys with usage statistics
- **Delete Keys**: Revoke access by deleting unused keys
- **Copy Keys**: Easy one-click copying of generated keys

### 📚 API Documentation
- **Authentication Guide**: How to use API keys in requests
- **Example Requests**: Curl examples for common operations
- **Endpoint Reference**: List of available API endpoints

### 🎨 User Experience
- **Clean Interface**: Dedicated page with focused functionality
- **Responsive Design**: Works on desktop and mobile devices
- **Toast Notifications**: Clear feedback for all actions
- **Loading States**: Visual indicators during operations

## Navigation

### From Main Dashboard
- Click the "API Keys" link in the top navigation bar
- The link is highlighted when you're on the API keys page

### Direct Access
- Navigate directly to `/api-keys` URL
- Requires admin authentication

## Usage

### 1. Generate New API Key
1. Click "Generate New Key" button
2. Enter a descriptive name (required)
3. Add optional description
4. Click "Create API Key"
5. Copy the generated key immediately

### 2. Manage Existing Keys
- View key details: name, description, creation date, usage count
- Delete unused keys with confirmation dialog
- Monitor key usage statistics

### 3. Use API Keys
- Include in `X-API-Key` header of all API requests
- Keep keys secure and don't share publicly
- Use different keys for different applications

## Security Features

- **One-time Display**: Generated keys are only shown once
- **Secure Storage**: Keys are hashed in the database
- **Admin Only**: Only authenticated admin users can access
- **Audit Trail**: Track creation and usage of keys

## Technical Details

### Page Route
- **URL**: `/api-keys`
- **Method**: GET
- **Authentication**: Required (admin only)
- **Template**: `templates/api_keys.html`

### JavaScript Class
- **Class**: `ApiKeysManager`
- **Instance**: `window.apiKeysManager`
- **Methods**: All API key management functionality

### API Endpoints Used
- `GET /api/settings/api-keys` - List all keys
- `POST /api/settings/api-keys` - Create new key
- `DELETE /api/settings/api-keys/{id}` - Delete key

## Benefits of Separate Page

1. **Focused Functionality**: Dedicated space for API key management
2. **Better Organization**: Cleaner main dashboard
3. **Improved UX**: More room for detailed information and documentation
4. **Easier Maintenance**: Separate concerns and easier to update
5. **Better Navigation**: Clear separation of features

## Future Enhancements

- **Key Permissions**: Different access levels for different keys
- **Usage Analytics**: Detailed usage reports and graphs
- **Key Rotation**: Automatic key expiration and renewal
- **Webhook Integration**: Notifications for key usage
- **Rate Limiting**: Per-key request limits
