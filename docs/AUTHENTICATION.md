# Testing Dashboard Authentication

## Overview

VoiceScribe Studio's testing dashboard is protected by basic authentication to ensure that only authorized users can access the testing tools. This document explains how to configure the authentication credentials.

## Default Credentials

The default credentials for accessing the testing dashboard are:

- **Username**: `admin`
- **Password**: `testingsuite`

## Customizing Authentication Credentials

To change the default authentication credentials:

1. Open the file `app/main.py`
2. Locate the `create_testing_interface()` function
3. Find the following code section (approximately line 320):

```python
# Set up authentication variables
AUTH_USERNAME = "admin"
AUTH_PASSWORD = "testingsuite"
```

4. Change the values for `AUTH_USERNAME` and `AUTH_PASSWORD` to your preferred credentials
5. Save the file and restart the application

## Security Considerations

- This authentication system provides basic protection but is not intended for high-security environments
- For production deployment, consider implementing more robust authentication mechanisms
- Authentication credentials are stored in plaintext in the application code - avoid using sensitive passwords
- In a production environment, consider moving these credentials to environment variables or a secure configuration system

## Authentication Flow

1. User clicks the "Test Suite" button in the main application
2. A new browser tab opens to the testing dashboard login screen
3. User enters credentials
4. If valid, the testing dashboard appears; if invalid, an error message is displayed
5. User can return to the main application via browser tabs or the "Back to Main App" button

## Technical Implementation

The authentication system is implemented using Gradio's conditional display capabilities:

1. The testing dashboard interface contains two main sections:
   - Login form (visible by default)
   - Dashboard container (hidden by default)
2. When valid credentials are provided, the visibility states switch
3. The authentication state is managed on the server side for each session 