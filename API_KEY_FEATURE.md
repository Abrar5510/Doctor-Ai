# API Key Input Feature

## Overview
The Doctor AI application now supports user-provided API keys for AI-powered diagnosis, allowing users to use their own OpenAI or OpenRouter API keys without requiring server-side configuration.

## Implementation Details

### Frontend (DiagnosisForm.jsx)
- **Toggle Switch**: Users can enable/disable AI-powered diagnosis
- **Provider Selection**: Choose between OpenAI (GPT-4) or OpenRouter (multiple models)
- **Secure Input**: Password-protected input field for API keys
- **Helper Links**: Direct links to obtain API keys from respective platforms
- **Dynamic Headers**: API keys are sent via `X-OpenAI-Key` or `X-OpenRouter-Key` headers

### Backend (routes.py)
- **Header Parsing**: Accepts API keys from request headers
- **Dynamic Initialization**: Creates AI assistant instances with user-provided keys
- **Enhanced Analysis**: Generates detailed explanations using the provided API key
- **Fallback Handling**: Continues with standard analysis if AI enhancement fails

## User Experience

1. User fills out patient information (symptoms, age, gender, medical history)
2. User enables "AI-Powered Diagnosis" toggle
3. User selects AI provider (OpenAI or OpenRouter)
4. User enters their API key in the secure input field
5. User submits the form
6. Backend uses the provided API key to generate AI-enhanced diagnostic insights

## Security Features

- API keys are transmitted via HTTPS
- Keys are stored only in component state (not persisted)
- Password input type masks the key entry
- Keys are sent via headers, not URL parameters
- Server-side validation and error handling

## Benefits

- **No Server Costs**: Users provide their own API keys
- **Privacy**: API keys remain with the user
- **Flexibility**: Support for multiple AI providers
- **Optional Feature**: Works with or without AI enhancement
- **User Control**: Users can choose when to use AI features

## Code Locations

- **Frontend Component**: `frontend/src/components/DiagnosisForm.jsx` (lines 154-211)
- **Backend Route**: `src/api/routes.py` (lines 42-96)
- **AI Service**: `src/services/ai_assistant.py` (lines 41-82)
- **Environment Config**: `.env.example` (lines 58-67)

## Future Enhancements

- Support for additional AI providers (Anthropic Claude, Google Gemini, etc.)
- API key validation before submission
- Usage tracking and cost estimation
- Saved preferences (with encryption)
- API key expiration warnings
