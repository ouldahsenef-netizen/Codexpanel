# Overview

This is a hacker-themed website built with Python Flask backend and HTML/CSS/JavaScript frontend. The site features a stunning cyberpunk Matrix design with digital rain effects, neon purple and green colors, and authentic hacker aesthetics. It provides API tools for Free Fire game manipulation including bio updates, user info scanning, friend requests, and item injection. The website showcases the CODEX TEAM developers with their actual profile images and contact information.

# User Preferences

- Preferred communication style: Simple, everyday language
- Website requirements: Python & HTML only (no Node.js/React)
- Design preference: Authentic Matrix hacker theme with digital rain effects
- Color scheme: Black background with neon green (#00ff41) and purple (#9932cc)
- No terminal windows in the middle of screen - Matrix effects only
- Use actual developer profile images provided
- Focus on functionality over flashy presentations

# System Architecture

## Backend Architecture
- **Framework**: Python Flask web framework
- **Server Port**: 3000 (changed from 8000 to resolve port conflicts)
- **API Integration**: Direct HTTP requests to external Free Fire APIs
- **Token Validation**: Simple token verification system
- **Error Handling**: Comprehensive error responses with user-friendly messages
- **CORS**: Configured for cross-origin requests

## Frontend Architecture
- **Technology**: Pure HTML5, CSS3, and Vanilla JavaScript
- **Styling**: Custom CSS with Matrix-themed animations and effects
- **Fonts**: Fira Code monospace font for authentic hacker aesthetic
- **Icons**: Font Awesome 6 for UI icons
- **Responsiveness**: Mobile-first responsive design

## Visual Design
- **Matrix Rain**: Animated Japanese characters and binary falling effect
- **Color Palette**: Black (#000), Matrix Green (#00ff41), Neon Purple (#9932cc)
- **Typography**: Fira Code monospace throughout
- **Effects**: Glitch text animations, neon glow effects, hover animations
- **Layout**: Clean sectioned layout with cyberpunk borders and shadows

## API Integration
- **Bio Update**: https://change-bio-bngx.vercel.app/update_bio/
- **User Info**: https://info-me-ob50.vercel.app/get
- **Friend Spam**: https://spambngx.vercel.app/send_friend
- **Banner**: https://bnrbngx-nu.vercel.app/bnr
- **Likes**: https://likesbngx-rosy.vercel.app/send_like
- **Outfit**: https://outfit-eta.vercel.app/api

## Team Information
- **BLRXH4RDIXX**: Website Creator & Lead Developer (Green theme) - @BLRXH4RDIXX
- **BNGX**: API Provider & Data Specialist (Purple theme) - @BNGXTTT
- Profile images corrected and properly assigned to each developer

# File Structure
- `app.py`: Flask backend server (runs on port 3000)
- `templates/index.html`: Main HTML template
- `static/css/style.css`: Matrix theme styling
- `static/js/script.js`: Matrix effects and API interactions  
- `static/images/`: Developer profile images
- `pyproject.toml`: Python dependencies (Flask, requests)

# Recent Changes (August 21, 2025)
- **Fixed startup issue**: Changed Flask server port to 3000 (resolved multiple port conflicts)
- **Resolved workflow conflict**: Application runs via `python app.py` instead of npm commands
- **Verified functionality**: All static files (CSS, JS, images) serving correctly
- **Confirmed API endpoints**: All Flask routes responding properly
- **Fixed image display**: Images swapped correctly between BNGX and BLRXH4RDIXX profiles
- **Enhanced outfit/banner responses**: Smart handling of text vs image responses with beautiful formatting
- **Improved user info display**: Card-based layout with icons and organized data presentation
- **Updated credits**: BLRXH4RDIXX as website creator, BNGX as API provider
- **Added response intelligence**: Automatic detection and formatting of different API response types
- **MAJOR UPDATE - Enhanced Image Display**: Completely redesigned outfit/banner response handling
  - Smart detection of image URLs vs encoded data vs regular text
  - Improved backend processing for different response types (JSON, URLs, encoded data)
  - Enhanced frontend display with proper image rendering and fallback formatting
  - Better handling of PNG-encoded responses and long text data
  - Beautiful cyberpunk-themed containers for encoded data display
  - Automatic URL extraction from mixed text responses