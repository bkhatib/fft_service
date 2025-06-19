#!/bin/bash

# Create .env file
cat > .env << EOL
OPENAI_API_KEY=your_openai_api_key_here
INFORMATICA_AUTH=your_informatica_auth_here
INFORMATICA_API_URL=your_informatica_api_url_here
EOL

# Export variables for current session
export $(cat .env | xargs)

echo "Environment variables have been set up!" 