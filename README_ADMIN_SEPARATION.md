# VoiceScribe Studio - Admin Separation

This document explains the architecture changes made to separate public and admin interfaces in VoiceScribe Studio.

## Architecture Overview

VoiceScribe Studio now has two separate interfaces:

1. **Public Interface**
   - Accessible to everyone
   - Contains core script generation, editing, and voiceover functionality
   - No authentication required

2. **Admin Interface**
   - Restricted to administrators
   - Password protected
   - Contains token analytics and testing suite
   - Requires authentication

## Authentication Details

The admin interface uses simple username/password authentication:

- **Username**: `admin`
- **Password**: `admin123`

> **Important**: You should change these default credentials in production by modifying the `ADMIN_USERNAME` and `ADMIN_PASSWORD` constants in the `app/main.py` file.

## Technical Implementation

The separation was implemented using a state-based interface switcher:

1. A single Gradio app contains all interfaces (public, login, and admin)
2. State variables track the current interface and authentication status
3. JavaScript enhances navigation between interfaces
4. Hidden buttons connected to Python functions handle interface switching
5. Token analytics and testing dashboard are only accessible through the admin interface
6. Authentication controls access to the admin dashboard

Benefits of this approach:
- Single server instance
- Seamless navigation between interfaces
- No browser refreshes or page reloads
- Secure access to admin features
- Centralized authentication

## Usage Instructions

### Accessing the Public Interface

1. Start the application with `python -m app.main`
2. Navigate to http://0.0.0.0:7860/ in your browser
3. Use the script generator, editor, and voiceover tabs freely

### Accessing the Admin Interface

1. Click the "Admin Login" link at the top of the public interface
2. Enter the admin credentials:
   - Username: `admin`
   - Password: `admin123`
3. Access the Token Analytics and Testing Suite tabs
4. Return to the public interface by clicking "Return to Public Interface"
5. Log out by clicking the "Logout" link

## Development Notes

- Token tracking for both interfaces is handled by the same database
- Testing functionality remains fully operational but is now part of the admin interface
- The code was restructured to improve maintainability and separation of concerns
- The authentication mechanism is simple and could be enhanced with more robust solutions in the future

For any questions or issues related to the admin separation, please contact the development team. 