# Railway Deployment Guide - VoiceScribe Studio

## Quick Deploy to Railway

VoiceScribe Studio is now ready for Railway deployment with shared tester authentication and admin access controls.

### Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Your VoiceScribe Studio repository 
3. **API Keys**: 
   - DeepSeek API key (primary LLM)
   - Anthropic API key (Claude fallback)
   - ElevenLabs API key (voice synthesis)

### Step 1: Connect Repository to Railway

1. **Login to Railway** and create a new project
2. **Connect GitHub repository**: Select your VoiceScribe Studio repository
3. **Railway will automatically detect** the Python application and configure Nixpacks

### Step 2: Configure Environment Variables

In your Railway project dashboard, add these environment variables:

#### Required API Keys
```bash
DEEPSEEK_API_KEY=your_deepseek_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here  
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

#### Authentication Credentials
```bash
# Tester Access (shared for all testers)
TESTER_USERNAME=voicescribe_tester
TESTER_PASSWORD=your_secure_tester_password_here

# Admin Access (your private access)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_admin_password_here
```

#### Optional Configuration
```bash
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
CLAUDE_MODEL=claude-3-7-sonnet-20250219
```

### Step 3: Deploy

1. **Automatic Deployment**: Railway will automatically build and deploy when you push to main branch
2. **Monitor Build**: Check the deployment logs for any issues
3. **Get Public URL**: Railway will provide a public URL like `https://your-app-name.railway.app`

### Step 4: Test Deployment

#### Test Tester Access
1. Visit your Railway URL
2. Click "🔒 Login" 
3. Use tester credentials:
   - Username: `voicescribe_tester` (or your custom username)
   - Password: Your tester password
4. Verify all features work (script generation, voiceover, etc.)

#### Test Admin Access  
1. Use admin credentials to access analytics and testing suite
2. Verify token tracking and testing dashboard functionality

## Authentication System

### Two User Types

1. **Testers**: Full access to all VoiceScribe features
   - Script generation with all templates
   - Voice synthesis and downloads
   - Reference processing (documents, URLs, YouTube)
   - Script editing and humanization

2. **Admins**: Everything testers have, plus:
   - Token usage analytics
   - Cross-template testing suite
   - Cost monitoring dashboard

### User Experience

- **First Visit**: Users see a login requirement message
- **After Login**: 
  - Testers see the full application interface
  - Admins can switch between public interface and admin dashboard
- **Access Control**: Change passwords in Railway dashboard to revoke access

## Cost Management

### Railway Hosting
- **Starter Plan**: $5/month (recommended for testing)
- **Developer Plan**: $10/month (if you need more resources)

### API Usage
- Monitor costs via admin dashboard token analytics
- Set informal usage guidelines for testers
- Revoke access by changing tester password if needed

## Security Features

- **HTTPS**: Automatic SSL certificates from Railway
- **Environment Variables**: All sensitive data in Railway dashboard, not code
- **Session Authentication**: Login required for all features
- **Input Validation**: Basic sanitization of user inputs
- **Error Handling**: Graceful degradation if APIs fail

## Access Management

### Sharing Access with Testers

Send testers:
```
VoiceScribe Studio Beta Access

URL: https://your-app-name.railway.app
Username: voicescribe_tester
Password: [provided separately]

Features available:
- AI script generation (5 templates)
- Professional voiceover creation
- Multi-format audio export (MP3, OGG, WAV)
- Document/URL/YouTube reference processing
- Script editing and humanization tools

Please provide feedback on your experience!
```

### Revoking Access

1. Go to Railway project dashboard
2. Navigate to Variables section
3. Change `TESTER_PASSWORD` value
4. App automatically restarts (~2 minutes)
5. All users must use new password

### Adding Individual Users (Future)

The current system supports shared credentials. For individual user accounts:

1. Extend authentication system in `app/main.py`
2. Add user management database
3. Create user registration/management interface
4. Update access control logic

## Monitoring and Maintenance

### Daily Checks
- **Railway Dashboard**: Monitor app health and resource usage
- **Admin Interface**: Check token usage and costs
- **Error Logs**: Review Railway logs for any issues

### Weekly Reviews
- **Cost Analysis**: Review API usage via token analytics
- **Performance**: Check app response times
- **User Feedback**: Collect and review tester feedback

### Monthly Tasks
- **Security Review**: Update passwords if needed
- **Cost Optimization**: Analyze usage patterns and optimize
- **Feature Updates**: Deploy improvements based on feedback

## Troubleshooting

### App Won't Start
1. Check Railway build logs for errors
2. Verify all required environment variables are set
3. Ensure API keys are valid
4. Check for any Python package installation failures

### Authentication Issues
1. Verify `TESTER_USERNAME` and `TESTER_PASSWORD` are set correctly
2. Check for typos in credentials
3. Clear browser cache and try again
4. Test with different browsers

### Feature Not Working
1. Check Railway application logs
2. Verify specific API keys (DeepSeek, Claude, ElevenLabs)
3. Test individual features in admin dashboard
4. Check network connectivity to APIs

### High Costs
1. Review token analytics in admin dashboard
2. Check which features are driving usage
3. Temporarily change tester password to limit access
4. Set usage guidelines with testers

## Support

### Getting Help
1. **Railway Support**: For hosting and deployment issues
2. **GitHub Issues**: For application bugs and feature requests
3. **API Documentation**: For API-related problems
   - [DeepSeek API Docs](https://platform.deepseek.com/api-docs)
   - [Anthropic API Docs](https://docs.anthropic.com)
   - [ElevenLabs API Docs](https://elevenlabs.io/docs)

### Emergency Procedures
1. **App Down**: Check Railway status, restart service if needed
2. **High Costs**: Change tester password immediately
3. **Security Breach**: Change all passwords, review access logs
4. **API Issues**: Check API status pages, test with different models

---

**Ready to Deploy?** 
Follow the steps above and your VoiceScribe Studio will be live for testing within minutes! 