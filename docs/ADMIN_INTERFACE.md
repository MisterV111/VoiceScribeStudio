# VoiceScribe Studio - Admin Interface

## Overview

VoiceScribe Studio has been restructured with a clear separation between public-facing features and admin-only functionalities. This document outlines the architecture, access methods, and features available in each interface.

## Architecture

The application now consists of two distinct interfaces:

1. **Public Interface**
   - Accessible to all users
   - Contains core script generation, editing, and voiceover functionality
   - No authentication required

2. **Admin Interface**
   - Restricted to administrators
   - Password protected
   - Contains token analytics and testing suite
   - Requires authentication

## Authentication Details

The admin interface is protected by simple username/password authentication:

- **Username**: `admin`
- **Password**: `admin123`

> **Important**: Consider changing these default credentials in production environments by modifying the `ADMIN_USERNAME` and `ADMIN_PASSWORD` constants in `app/main.py`.

## Technical Implementation

The separation was implemented using a state-based interface switcher:

1. A single Gradio app contains all interfaces (public, login, and admin)
2. State variables track the current interface and authentication status
3. Clear navigation between interfaces with link-styled buttons
4. Token analytics and testing dashboard are only accessible through the admin interface
5. Authentication controls access to the admin dashboard

Benefits of this approach:
- Single server instance (port 7860)
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

## Admin Features

### Token Analytics
- Track API usage and costs for both DeepSeek and Claude models
- Visualize token consumption patterns
- Monitor fallback rates
- Analyze cost efficiency metrics
- Filter by time period and usage type

### Testing Suite
- Run automated tests across all templates
- View formatted test results with intuitive indicators
- Analyze script generation performance
- Compare results across different models
- Track validation metrics for quality assurance

## Security Considerations

- The authentication mechanism is simple and designed for internal use
- It provides a basic level of protection against unauthorized access
- For production deployments, consider implementing:
  - More robust authentication (e.g., hashed passwords, session management)
  - HTTPS for secure communication
  - Rate limiting for login attempts
  - Role-based access control for different admin levels

## Future Enhancements

Planned improvements to the admin interface include:

- More granular permission levels (editor, admin, super-admin)
- Enhanced analytics with more detailed metrics
- Configuration management through the admin UI
- System health monitoring and alerts
- User activity logs for auditing purposes 